#include "PlayerViewModeSubsystem.h"

#include "PlayerTopDownCamera.h"
#include "InnerRealmSubsystem.h"
#include "SpellCastingBindingSubsystem.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"

namespace ViewModeInput
{
    // Tunable per-pixel orbit angles: faster response for live-casting camera control.
    constexpr float OrbitYawDegreesPerMousePixel = 1.25f;
    constexpr float OrbitPitchDegreesPerMousePixel = 0.75f;

    // Wheel movement arrives as individual pulses. Keep sprint active briefly
    // between closely-spaced pulses instead of leaving a persistent toggle on.
    constexpr float SprintPulseWindowSeconds = 0.45f;
}

TStatId UPlayerViewModeSubsystem::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UPlayerViewModeSubsystem, STATGROUP_Tickables);
}

void UPlayerViewModeSubsystem::Deinitialize()
{
    if (bTopDown)
    {
        ExitTopDown(CachedController.Get());
    }
    ReleaseTopDownInput();
    RestoreTemplateJump();
    if (OrbitCamera.IsValid())
    {
        OrbitCamera->Destroy();
        OrbitCamera.Reset();
    }
    Super::Deinitialize();
}

APlayerTopDownCamera* UPlayerViewModeSubsystem::GetOrSpawnCamera()
{
    if (OrbitCamera.IsValid()) return OrbitCamera.Get();
    UWorld* World = GetWorld();
    if (!World) return nullptr;

    FActorSpawnParameters Params;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    APlayerTopDownCamera* Actor = World->SpawnActor<APlayerTopDownCamera>(
        APlayerTopDownCamera::StaticClass(), FVector::ZeroVector, FRotator::ZeroRotator, Params);
    OrbitCamera = Actor;
    return Actor;
}

void UPlayerViewModeSubsystem::ReapplyTopDownInput(APlayerController* PC)
{
    if (!PC) return;
    // SetIgnoreMoveInput / SetIgnoreLookInput are reference-counted in Unreal.
    // TAB's InnerRealm owns a SEPARATE lock. Reapply after meditation MUST NOT
    // acquire a second top-down lock, or WASD remains blocked in third-person.
    if (bOwnsTopDownInputLock && InputLockController.Get() != PC)
    {
        ReleaseTopDownInput();
    }
    if (!bOwnsTopDownInputLock)
    {
        PC->SetIgnoreMoveInput(true);
        PC->SetIgnoreLookInput(true);
        InputLockController = PC;
        bOwnsTopDownInputLock = true;
    }
    PC->bShowMouseCursor = true;
    FInputModeGameAndUI Mode;
    Mode.SetHideCursorDuringCapture(false);
    Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
    PC->SetInputMode(Mode);
}

void UPlayerViewModeSubsystem::ReleaseTopDownInput()
{
    if (bOwnsTopDownInputLock)
    {
        // Release only OUR lock; another system (such as the InnerRealm) may
        // still legitimately own another lock on the same controller.
        if (APlayerController* Owner = InputLockController.Get())
        {
            Owner->SetIgnoreMoveInput(false);
            Owner->SetIgnoreLookInput(false);
        }
        bOwnsTopDownInputLock = false;
        InputLockController.Reset();
    }
}

void UPlayerViewModeSubsystem::EnterTopDown(APlayerController* PC)
{
    if (bTopDown || !PC || !PC->GetPawn()) return;
    APlayerTopDownCamera* CameraActor = GetOrSpawnCamera();
    if (!CameraActor) return;

    CachedController = PC;
    SavedThirdPersonView = PC->GetViewTarget();
    SavedCharacter = Cast<ACharacter>(PC->GetPawn());
    OrbitYawDegrees = PC->GetControlRotation().Yaw;
    OrbitElevationDegrees = 62.0f;
    bSprinting = false;
    SprintWindowRemainingSeconds = 0.0f;
    bHaveDestination = false;

    if (ACharacter* Character = SavedCharacter.Get())
    {
        bPreviousUseControllerRotationYaw = Character->bUseControllerRotationYaw;
        Character->bUseControllerRotationYaw = false;
        if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
        {
            PreviousWalkSpeed = Movement->MaxWalkSpeed;
            bPreviousOrientRotationToMovement = Movement->bOrientRotationToMovement;
            Movement->bOrientRotationToMovement = true;
            Movement->StopMovementImmediately();
        }
    }

    CameraActor->SetOrbit(OrbitYawDegrees, OrbitElevationDegrees);
    UpdateCamera(PC);
    bTopDown = true;
    if (UWorld* World = GetWorld())
    {
        if (USpellCastingBindingSubsystem* Bindings = World->GetSubsystem<USpellCastingBindingSubsystem>())
        {
            Bindings->SetTopDownLiveInputEnabled(true);
        }
    }
    ReapplyTopDownInput(PC);
    PC->SetViewTargetWithBlend(CameraActor, 0.25f);
    if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Cyan,
        TEXT("TOP-DOWN: RMB move | LMB drag orbit | keep scrolling up to sprint | Shift return"));
}

void UPlayerViewModeSubsystem::ExitTopDown(APlayerController* PC)
{
    if (!bTopDown) return;
    bTopDown = false;
    if (UWorld* World = GetWorld())
    {
        if (USpellCastingBindingSubsystem* Bindings = World->GetSubsystem<USpellCastingBindingSubsystem>())
        {
            Bindings->SetTopDownLiveInputEnabled(false);
        }
    }
    bHaveDestination = false;
    SprintWindowRemainingSeconds = 0.0f;
    SetSprint(false);

    if (ACharacter* Character = SavedCharacter.Get())
    {
        Character->bUseControllerRotationYaw = bPreviousUseControllerRotationYaw;
        if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
        {
            Movement->bOrientRotationToMovement = bPreviousOrientRotationToMovement;
            Movement->MaxWalkSpeed = PreviousWalkSpeed;
        }
    }

    ReleaseTopDownInput();

    if (PC)
    {
        PC->bShowMouseCursor = false;
        PC->SetInputMode(FInputModeGameOnly());
        AActor* ReturnView = SavedThirdPersonView.IsValid() ? SavedThirdPersonView.Get() : Cast<AActor>(PC->GetPawn());
        if (ReturnView) PC->SetViewTargetWithBlend(ReturnView, 0.25f);
    }
    SavedThirdPersonView.Reset();
    SavedCharacter.Reset();
    bWasMeditating = false;
}

void UPlayerViewModeSubsystem::SetSprint(const bool bEnabled)
{
    if (bSprinting == bEnabled) return;
    bSprinting = bEnabled;
    if (ACharacter* Character = SavedCharacter.Get())
    {
        if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
        {
            // Only top-down changes MaxWalkSpeed; original value restored on exit.
            Movement->MaxWalkSpeed = PreviousWalkSpeed * (bEnabled ? 1.75f : 1.0f);
        }
    }
    if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 1.2f, FColor::Cyan,
        bEnabled ? TEXT("SPRINT") : TEXT("WALK"));
}

void UPlayerViewModeSubsystem::RestoreTemplateJump()
{
    if (ACharacter* Previous = JumpSuppressedCharacter.Get())
    {
        Previous->JumpMaxCount = PreviousJumpMaxCount;
    }
    JumpSuppressedCharacter.Reset();
}

void UPlayerViewModeSubsystem::SuppressTemplateJump(APlayerController* PC)
{
    ACharacter* Current = PC ? Cast<ACharacter>(PC->GetPawn()) : nullptr;
    if (Current != JumpSuppressedCharacter.Get())
    {
        RestoreTemplateJump();
        if (Current)
        {
            JumpSuppressedCharacter = Current;
            PreviousJumpMaxCount = Current->JumpMaxCount;
        }
    }
    if (Current)
    {
        // JumpMaxCount=0 blocks the template's existing Space -> Jump action.
        // Do not change the blueprint's input asset or interfere with casting.
        Current->JumpMaxCount = 0;
        if (PC->WasInputKeyJustPressed(EKeys::SpaceBar))
        {
            Current->StopJumping();
        }
    }
}

void UPlayerViewModeSubsystem::UpdateCamera(APlayerController* PC)
{
    if (!PC || !PC->GetPawn() || !OrbitCamera.IsValid()) return;
    OrbitCamera->FollowPosition(PC->GetPawn()->GetActorLocation());
    OrbitCamera->SetOrbit(OrbitYawDegrees, OrbitElevationDegrees);
}

bool UPlayerViewModeSubsystem::FindCursorWorldPoint(APlayerController* PC, FVector& OutPoint) const
{
    if (!PC) return false;

    FHitResult Hit;
    if (PC->GetHitResultUnderCursorByChannel(
        UEngineTypes::ConvertToTraceType(ECC_Visibility), false, Hit) && Hit.bBlockingHit)
    {
        // Do not navigate toward your own collision capsule when it happens to be under the cursor.
        if (Hit.GetActor() != PC->GetPawn())
        {
            OutPoint = Hit.ImpactPoint;
            return true;
        }
    }

    // Fallback for a blank/open-world cell or surfaces without Visibility tracing:
    // intersect the cursor ray with a flat plane through the player's feet.
    FVector RayOrigin, RayDirection;
    const APawn* Pawn = PC->GetPawn();
    if (!Pawn || !PC->DeprojectMousePositionToWorld(RayOrigin, RayDirection)) return false;
    if (FMath::Abs(RayDirection.Z) < 0.001f) return false;
    const float T = (Pawn->GetActorLocation().Z - RayOrigin.Z) / RayDirection.Z;
    if (T < 0.0f || T > 100000.0f) return false;
    OutPoint = RayOrigin + RayDirection * T;
    return true;
}

bool UPlayerViewModeSubsystem::GetTopDownCastRay(FVector& OutOrigin, FVector& OutDirection) const
{
    if (!bTopDown) return false;
    UWorld* World = GetWorld();
    APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;
    APawn* Pawn = PC ? PC->GetPawn() : nullptr;
    if (!Pawn) return false;

    OutOrigin = Pawn->GetActorLocation() + FVector(0.0f, 0.0f, 100.0f);
    FVector Point;
    if (FindCursorWorldPoint(PC, Point))
    {
        FVector ToPoint = Point - OutOrigin;
        ToPoint.Z = 0.0f; // Current Earth prototype casts horizontally, from the player.
        if (ToPoint.SizeSquared() > FMath::Square(75.0f))
        {
            OutDirection = ToPoint.GetSafeNormal();
            return true;
        }
    }
    OutDirection = FRotator(0.0f, OrbitYawDegrees, 0.0f).Vector();
    return true;
}

void UPlayerViewModeSubsystem::HandleTopDownInput(APlayerController* PC, const float DeltaSeconds)
{
    if (!PC) return;

    // A mouse wheel cannot be held like a key. Upward scroll pulses refresh a
    // short sprint window; without new pulses it automatically expires.
    const float WheelAxis = PC->GetInputAnalogKeyState(EKeys::MouseWheelAxis);
    const bool bUpPulse = WheelAxis > 0.05f || PC->WasInputKeyJustPressed(EKeys::MouseScrollUp);
    const bool bDownPulse = WheelAxis < -0.05f || PC->WasInputKeyJustPressed(EKeys::MouseScrollDown);
    const bool bHoldingMove = PC->IsInputKeyDown(EKeys::RightMouseButton);
    if (!bHoldingMove || bDownPulse)
    {
        SprintWindowRemainingSeconds = 0.0f;
    }
    else if (bUpPulse)
    {
        SprintWindowRemainingSeconds = ViewModeInput::SprintPulseWindowSeconds;
    }
    else
    {
        SprintWindowRemainingSeconds = FMath::Max(0.0f, SprintWindowRemainingSeconds - DeltaSeconds);
    }
    SetSprint(bHoldingMove && SprintWindowRemainingSeconds > 0.0f);

    if (PC->IsInputKeyDown(EKeys::LeftMouseButton))
    {
        float DeltaX = 0.0f, DeltaY = 0.0f;
        PC->GetInputMouseDelta(DeltaX, DeltaY);
        OrbitYawDegrees = FRotator::NormalizeAxis(OrbitYawDegrees + DeltaX * ViewModeInput::OrbitYawDegreesPerMousePixel);
        // Drag vertically to adjust how top-down the view is.
        OrbitElevationDegrees = FMath::Clamp(OrbitElevationDegrees - DeltaY * ViewModeInput::OrbitPitchDegreesPerMousePixel, 16.0f, 84.0f);
    }

    if (!bHoldingMove) bHaveDestination = false;
    else
    {
        FVector Point;
        if (FindCursorWorldPoint(PC, Point))
        {
            MoveDestination = Point;
            bHaveDestination = true;
        }
    }

    ACharacter* Character = Cast<ACharacter>(PC->GetPawn());
    if (Character && bHoldingMove && bHaveDestination)
    {
        FVector Delta = MoveDestination - Character->GetActorLocation();
        Delta.Z = 0.0f;
        const float ArrivalRadius = 80.0f;
        if (Delta.SizeSquared() > FMath::Square(ArrivalRadius))
        {
            // bForce=true deliberately bypasses ignored input from the old Third Person mapping.
            Character->AddMovementInput(Delta.GetSafeNormal(), 1.0f, true);
        }
        else if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
        {
            Movement->StopMovementImmediately();
        }
    }
}

void UPlayerViewModeSubsystem::Tick(const float DeltaSeconds)
{
    UWorld* World = GetWorld();
    if (!World || !World->IsGameWorld()) return;
    APlayerController* PC = World->GetFirstPlayerController();
    if (!PC) return;

    // Space is always reserved for casting in BOTH views, even when the template
    // Third Person Blueprint still contains its default IA_Jump mapping.
    SuppressTemplateJump(PC);

    // TAB / InnerRealm always has priority. It temporarily owns view+input without
    // changing the chosen outer-world camera mode.
    const UInnerRealmSubsystem* Realm = World->GetSubsystem<UInnerRealmSubsystem>();
    const bool bMeditating = Realm && Realm->IsActive();
    if (bMeditating)
    {
        SprintWindowRemainingSeconds = 0.0f;
        if (bTopDown) SetSprint(false);
        bWasMeditating = true;
        return;
    }
    if (bWasMeditating)
    {
        bWasMeditating = false;
        if (bTopDown)
        {
            // InnerRealm restores the preceding view, then this node restores cursor/input.
            ReapplyTopDownInput(PC);
            if (OrbitCamera.IsValid()) PC->SetViewTargetWithBlend(OrbitCamera.Get(), 0.0f);
        }
    }

    if (PC->WasInputKeyJustPressed(EKeys::LeftShift) || PC->WasInputKeyJustPressed(EKeys::RightShift))
    {
        if (bTopDown) ExitTopDown(PC);
        else EnterTopDown(PC);
        return;
    }

    if (bTopDown)
    {
        CachedController = PC;
        HandleTopDownInput(PC, DeltaSeconds);
        UpdateCamera(PC);
    }
}
