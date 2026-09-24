#include "InnerRealmSubsystem.h"

#include "InnerRealmActor.h"
#include "EarthSpellMath.h"
#include "LiveSpellRanges.h"
#include "LiveSpellSessionSubsystem.h"
#include "SpellCreationSubsystem.h"
#include "SpellCastingBindingSubsystem.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PawnMovementComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Input/SInputKeySelector.h"
#include "Widgets/Input/SSlider.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SScrollBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Text/STextBlock.h"
#include "Styling/CoreStyle.h"

namespace InnerRealmEditor
{
    static void GetDimensionRange(const EEarthSpellShape Shape, const int32 Index, float& OutMin, float& OutMax)
    {
        switch (Shape)
        {
            case EEarthSpellShape::Sphere:
                OutMin = LiveSpellRanges::MinSphereRadiusCm;
                OutMax = LiveSpellRanges::MaxSphereRadiusCm;
                break;
            case EEarthSpellShape::Cube:
                OutMin = LiveSpellRanges::MinCubeSideCm;
                OutMax = LiveSpellRanges::MaxCubeSideCm;
                break;
            case EEarthSpellShape::Cone:
            default:
                if (Index == 0)
                {
                    OutMin = LiveSpellRanges::MinConeRadiusCm;
                    OutMax = LiveSpellRanges::MaxConeRadiusCm;
                }
                else
                {
                    OutMin = LiveSpellRanges::MinConeHeightCm;
                    OutMax = LiveSpellRanges::MaxConeHeightCm;
                }
                break;
        }
    }
}

void UInnerRealmSubsystem::Deinitialize()
{
    if (bActive)
    {
        ExitRealm();
    }
    RemoveEditorWidget();
    Super::Deinitialize();
}

void UInnerRealmSubsystem::Tick(float DeltaTime)
{
    UWorld* World = GetWorld();
    if (!World || !World->IsGameWorld())
    {
        return;
    }

    APlayerController* PC = World->GetFirstPlayerController();
    if (!PC)
    {
        return;
    }

    if (PC->WasInputKeyJustPressed(EKeys::Tab))
    {
        bActive ? ExitRealm() : EnterRealm();
    }
}

TStatId UInnerRealmSubsystem::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UInnerRealmSubsystem, STATGROUP_Tickables);
}

USpellCreationSubsystem* UInnerRealmSubsystem::GetSpellCreation() const
{
    UWorld* World = GetWorld();
    return World ? World->GetSubsystem<USpellCreationSubsystem>() : nullptr;
}

USpellCastingBindingSubsystem* UInnerRealmSubsystem::GetSpellBindings() const
{
    UWorld* World = GetWorld();
    return World ? World->GetSubsystem<USpellCastingBindingSubsystem>() : nullptr;
}

FEarthSpellDefinition UInnerRealmSubsystem::ReadSpell() const
{
    if (const USpellCreationSubsystem* SpellCreation = GetSpellCreation())
    {
        return SpellCreation->GetStoredSpellDefinition();
    }
    return FEarthSpellDefinition();
}

void UInnerRealmSubsystem::WriteSpell(const FEarthSpellDefinition& Spell)
{
    if (USpellCreationSubsystem* SpellCreation = GetSpellCreation())
    {
        SpellCreation->SetStoredSpellDefinition(Spell);
    }
}

void UInnerRealmSubsystem::SetShape(const EEarthSpellShape Shape)
{
    FEarthSpellDefinition Spell = ReadSpell();
    Spell.Shape = Shape;
    WriteSpell(Spell);
}

FText UInnerRealmSubsystem::GetShapeName() const
{
    switch (ReadSpell().Shape)
    {
        case EEarthSpellShape::Sphere: return FText::FromString(TEXT("SPHERE"));
        case EEarthSpellShape::Cube:   return FText::FromString(TEXT("CUBE"));
        case EEarthSpellShape::Cone:   return FText::FromString(TEXT("CONE"));
        default:                       return FText::FromString(TEXT("EARTH FORM"));
    }
}

FInputChord UInnerRealmSubsystem::GetBindingChord(const ESpellLiveAction Action) const
{
    if (const USpellCastingBindingSubsystem* Bindings = GetSpellBindings())
    {
        const FKey Key = Bindings->GetBinding(Action);
        if (Key.IsValid())
        {
            return FInputChord(Key);
        }
    }
    return FInputChord();
}

void UInnerRealmSubsystem::HandleBindingSelected(const ESpellLiveAction Action, const FInputChord& Chord)
{
    if (Chord.Key == EKeys::Tab)
    {
        ExitRealm();
        return;
    }

    USpellCastingBindingSubsystem* Bindings = GetSpellBindings();
    if (!Bindings)
    {
        return;
    }

    if (!Chord.Key.IsValid())
    {
        Bindings->ClearBinding(Action);
        return;
    }

    // Pressing the same assigned key again is the explicit empty/unassign gesture.
    if (Bindings->GetBinding(Action) == Chord.Key)
    {
        Bindings->ClearBinding(Action);
        return;
    }

    if (!Bindings->SetBinding(Action, Chord.Key) && GEngine)
    {
        GEngine->AddOnScreenDebugMessage(-1, 1.5f, FColor::Yellow,
            TEXT("That key is reserved for movement/camera/casting."));
    }
}

FText UInnerRealmSubsystem::GetCurrentSpellSummary() const
{
    const FEarthSpellDefinition Spell = ReadSpell();
    return FText::FromString(FString::Printf(
        TEXT("EARTH / %s   |   speed %.0f m/s   |   density %.0f kg/m3   |   mass %.0f kg   |   distance %.1f m"),
        *GetShapeName().ToString(),
        Spell.SpeedMps,
        Spell.DensityKgPerM3,
        UEarthSpellMath::CalculateMassKg(Spell),
        Spell.DistanceM));
}

AInnerRealmActor* UInnerRealmSubsystem::GetOrCreateRealmActor()
{
    if (RealmActor.IsValid())
    {
        return RealmActor.Get();
    }

    UWorld* World = GetWorld();
    if (!World)
    {
        return nullptr;
    }

    FActorSpawnParameters Params;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    AInnerRealmActor* Actor = World->SpawnActor<AInnerRealmActor>(
        AInnerRealmActor::StaticClass(), FVector::ZeroVector, FRotator::ZeroRotator, Params);
    if (Actor)
    {
        RealmActor = Actor;
    }
    return Actor;
}

void UInnerRealmSubsystem::EnterRealm()
{
    if (bActive)
    {
        return;
    }

    UWorld* World = GetWorld();
    APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;
    AInnerRealmActor* Realm = GetOrCreateRealmActor();
    if (!PC || !Realm)
    {
        return;
    }

    bActive = true;
    PreviousViewTarget = PC->GetViewTarget();
    if (ULiveSpellSessionSubsystem* LiveSession = World->GetSubsystem<ULiveSpellSessionSubsystem>())
    {
        LiveSession->ResetSession();
    }
    if (USpellCastingBindingSubsystem* Bindings = GetSpellBindings())
    {
        Bindings->SetSuspended(true);
    }

    CaptureAndFreezePlayer(PC);
    PositionRealmNearPlayer(Realm, PC);
    ApplyPlayerInputState(true);
    PC->SetViewTargetWithBlend(Realm, 0.15f);
    CreateEditorWidget();
}

void UInnerRealmSubsystem::ExitRealm()
{
    if (!bActive)
    {
        return;
    }

    UWorld* World = GetWorld();
    APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;

    RemoveEditorWidget();
    if (PC)
    {
        AActor* ReturnTarget = PreviousViewTarget.IsValid()
            ? PreviousViewTarget.Get()
            : Cast<AActor>(PC->GetPawn());
        if (ReturnTarget)
        {
            PC->SetViewTargetWithBlend(ReturnTarget, 0.15f);
        }
    }

    PreviousViewTarget.Reset();
    bActive = false;
    if (USpellCastingBindingSubsystem* Bindings = GetSpellBindings())
    {
        Bindings->SetSuspended(false);
    }
    ApplyPlayerInputState(false);
    RestoreFrozenPlayer();
}

void UInnerRealmSubsystem::CaptureAndFreezePlayer(APlayerController* PC)
{
    FrozenPawn.Reset();
    bSavedCharacterMovement = false;

    APawn* Pawn = PC ? PC->GetPawn() : nullptr;
    if (!Pawn)
    {
        return;
    }

    FrozenPawn = Pawn;
    FrozenPawnTransform = Pawn->GetActorTransform();

    if (ACharacter* Character = Cast<ACharacter>(Pawn))
    {
        if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
        {
            SavedMovementMode = static_cast<uint8>(Movement->MovementMode);
            SavedCustomMovementMode = Movement->CustomMovementMode;
            bSavedCharacterMovement = true;
            Movement->StopMovementImmediately();
            Movement->DisableMovement();
        }
    }
    else if (UPawnMovementComponent* Movement = Pawn->GetMovementComponent())
    {
        Movement->StopMovementImmediately();
        Movement->Deactivate();
    }
}

void UInnerRealmSubsystem::RestoreFrozenPlayer()
{
    APawn* Pawn = FrozenPawn.Get();
    if (!Pawn)
    {
        FrozenPawn.Reset();
        bSavedCharacterMovement = false;
        return;
    }

    Pawn->SetActorTransform(FrozenPawnTransform, false, nullptr, ETeleportType::TeleportPhysics);

    if (bSavedCharacterMovement)
    {
        if (ACharacter* Character = Cast<ACharacter>(Pawn))
        {
            if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
            {
                Movement->SetMovementMode(static_cast<EMovementMode>(SavedMovementMode), SavedCustomMovementMode);
            }
        }
    }
    else if (UPawnMovementComponent* Movement = Pawn->GetMovementComponent())
    {
        Movement->Activate(true);
    }

    FrozenPawn.Reset();
    bSavedCharacterMovement = false;
}

void UInnerRealmSubsystem::PositionRealmNearPlayer(AInnerRealmActor* Realm, APlayerController* PC)
{
    if (!Realm)
    {
        return;
    }

    FVector Base = FVector::ZeroVector;
    if (PC && PC->GetPawn())
    {
        Base = PC->GetPawn()->GetActorLocation();
    }
    Realm->SetActorLocation(Base + FVector(0.0f, 0.0f, 10000.0f));
}

void UInnerRealmSubsystem::ApplyPlayerInputState(const bool bEntering)
{
    UWorld* World = GetWorld();
    APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;
    if (!PC)
    {
        return;
    }

    PC->SetIgnoreMoveInput(bEntering);
    PC->SetIgnoreLookInput(bEntering);
    PC->bShowMouseCursor = bEntering;

    if (bEntering)
    {
        FInputModeGameAndUI Mode;
        Mode.SetHideCursorDuringCapture(false);
        Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
        PC->SetInputMode(Mode);
    }
    else
    {
        PC->SetInputMode(FInputModeGameOnly());
        PC->bShowMouseCursor = false;
    }
}

float UInnerRealmSubsystem::GetSpeedSlider() const
{
    return LiveSpellRanges::Normalize(ReadSpell().SpeedMps, LiveSpellRanges::MinSpeedMps, LiveSpellRanges::MaxSpeedMps);
}

float UInnerRealmSubsystem::GetDistanceSlider() const
{
    return LiveSpellRanges::Normalize(ReadSpell().DistanceM, LiveSpellRanges::MinDistanceM, LiveSpellRanges::MaxDistanceM);
}

float UInnerRealmSubsystem::GetDensitySlider() const
{
    return LiveSpellRanges::Normalize(ReadSpell().DensityKgPerM3, LiveSpellRanges::MinDensityKgPerM3, LiveSpellRanges::MaxDensityKgPerM3);
}

float UInnerRealmSubsystem::GetHardnessSlider() const { return ReadSpell().Hardness; }
float UInnerRealmSubsystem::GetToughnessSlider() const { return ReadSpell().Toughness; }
float UInnerRealmSubsystem::GetElasticitySlider() const { return ReadSpell().Elasticity; }

void UInnerRealmSubsystem::SetSpeedSlider(const float Value)
{
    FEarthSpellDefinition Spell = ReadSpell();
    Spell.SpeedMps = LiveSpellRanges::Denormalize(Value, LiveSpellRanges::MinSpeedMps, LiveSpellRanges::MaxSpeedMps);
    WriteSpell(Spell);
}

void UInnerRealmSubsystem::SetDistanceSlider(const float Value)
{
    FEarthSpellDefinition Spell = ReadSpell();
    Spell.DistanceM = LiveSpellRanges::Denormalize(Value, LiveSpellRanges::MinDistanceM, LiveSpellRanges::MaxDistanceM);
    WriteSpell(Spell);
}

void UInnerRealmSubsystem::SetDensitySlider(const float Value)
{
    FEarthSpellDefinition Spell = ReadSpell();
    Spell.DensityKgPerM3 = LiveSpellRanges::Denormalize(Value, LiveSpellRanges::MinDensityKgPerM3, LiveSpellRanges::MaxDensityKgPerM3);
    WriteSpell(Spell);
}

void UInnerRealmSubsystem::SetHardnessSlider(const float Value)
{
    FEarthSpellDefinition Spell = ReadSpell();
    Spell.Hardness = FMath::Clamp(Value, 0.0f, 1.0f);
    WriteSpell(Spell);
}

void UInnerRealmSubsystem::SetToughnessSlider(const float Value)
{
    FEarthSpellDefinition Spell = ReadSpell();
    Spell.Toughness = FMath::Clamp(Value, 0.0f, 1.0f);
    WriteSpell(Spell);
}

void UInnerRealmSubsystem::SetElasticitySlider(const float Value)
{
    FEarthSpellDefinition Spell = ReadSpell();
    Spell.Elasticity = FMath::Clamp(Value, 0.0f, 1.0f);
    WriteSpell(Spell);
}

float UInnerRealmSubsystem::GetDimensionSlider(const int32 Index) const
{
    const FEarthSpellDefinition Spell = ReadSpell();
    float Value = Spell.SphereRadiusCm;

    if (Spell.Shape == EEarthSpellShape::Cube)
    {
        Value = Index == 0 ? Spell.CubeXcm : (Index == 1 ? Spell.CubeYcm : Spell.CubeZcm);
    }
    else if (Spell.Shape == EEarthSpellShape::Cone)
    {
        Value = Index == 0 ? Spell.ConeRadiusCm : Spell.ConeHeightCm;
    }

    float Min = 0.0f;
    float Max = 1.0f;
    InnerRealmEditor::GetDimensionRange(Spell.Shape, Index, Min, Max);
    return LiveSpellRanges::Normalize(Value, Min, Max);
}

void UInnerRealmSubsystem::SetDimensionSlider(const int32 Index, const float SliderValue)
{
    FEarthSpellDefinition Spell = ReadSpell();
    float Min = 0.0f;
    float Max = 1.0f;
    InnerRealmEditor::GetDimensionRange(Spell.Shape, Index, Min, Max);
    const float Value = LiveSpellRanges::Denormalize(SliderValue, Min, Max);

    if (Spell.Shape == EEarthSpellShape::Sphere)
    {
        Spell.SphereRadiusCm = Value;
    }
    else if (Spell.Shape == EEarthSpellShape::Cube)
    {
        if (Index == 0) Spell.CubeXcm = Value;
        else if (Index == 1) Spell.CubeYcm = Value;
        else Spell.CubeZcm = Value;
    }
    else
    {
        if (Index == 0) Spell.ConeRadiusCm = Value;
        else Spell.ConeHeightCm = Value;
    }

    WriteSpell(Spell);
}

EVisibility UInnerRealmSubsystem::GetDimensionVisibility(const int32 Index) const
{
    const EEarthSpellShape Shape = ReadSpell().Shape;
    if (Shape == EEarthSpellShape::Sphere && Index > 0) return EVisibility::Collapsed;
    if (Shape == EEarthSpellShape::Cone && Index > 1) return EVisibility::Collapsed;
    return EVisibility::Visible;
}

FText UInnerRealmSubsystem::GetDimensionLabel(const int32 Index) const
{
    const FEarthSpellDefinition Spell = ReadSpell();
    FString Name;
    float Value = 0.0f;

    if (Spell.Shape == EEarthSpellShape::Sphere)
    {
        Name = TEXT("Radius");
        Value = Spell.SphereRadiusCm;
    }
    else if (Spell.Shape == EEarthSpellShape::Cube)
    {
        if (Index == 0) { Name = TEXT("X"); Value = Spell.CubeXcm; }
        else if (Index == 1) { Name = TEXT("Y"); Value = Spell.CubeYcm; }
        else { Name = TEXT("Z"); Value = Spell.CubeZcm; }
    }
    else
    {
        if (Index == 0) { Name = TEXT("Radius"); Value = Spell.ConeRadiusCm; }
        else { Name = TEXT("Height"); Value = Spell.ConeHeightCm; }
    }

    return FText::FromString(FString::Printf(TEXT("%s: %.0f cm"), *Name, Value));
}

void UInnerRealmSubsystem::CreateEditorWidget()
{
    if (EditorWidget.IsValid() || !GEngine || !GEngine->GameViewport)
    {
        return;
    }

    static FTextBlockStyle BlackKeyTextStyle = FCoreStyle::Get().GetWidgetStyle<FTextBlockStyle>("NormalText");
    BlackKeyTextStyle.SetColorAndOpacity(FSlateColor(FLinearColor::Black));
    const FSlateColor BlackText(FLinearColor::Black);

    auto MakeBindSelector = [this](const ESpellLiveAction Action) -> TSharedRef<SWidget>
    {
        return SNew(SBox)
            .WidthOverride(92.0f)
            [
                SNew(SInputKeySelector)
                .SelectedKey_Lambda([this, Action]() { return GetBindingChord(Action); })
                .OnKeySelected_Lambda([this, Action](const FInputChord& Chord)
                {
                    HandleBindingSelected(Action, Chord);
                })
                .AllowGamepadKeys(false)
                .AllowModifierKeys(false)
                .EscapeCancelsSelection(true)
                .KeySelectionText(FText::FromString(TEXT("key")))
                .NoKeySpecifiedText(FText::FromString(TEXT("+")))
                .TextStyle(&BlackKeyTextStyle)
                .Margin(FMargin(6.0f, 3.0f))
            ];
    };

    auto MakeShapeControl = [this, &MakeBindSelector, BlackText](
        const ESpellLiveAction Action,
        const EEarthSpellShape Shape,
        const TCHAR* Label) -> TSharedRef<SWidget>
    {
        return SNew(SHorizontalBox)
            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0, 2, 8, 2)
            [ MakeBindSelector(Action) ]
            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0, 2)
            [
                SNew(SButton)
                .IsFocusable(false)
                .ContentPadding(FMargin(12.0f, 6.0f))
                .OnClicked_Lambda([this, Shape]()
                {
                    SetShape(Shape);
                    return FReply::Handled();
                })
                [
                    SNew(STextBlock)
                    .ColorAndOpacity(BlackText)
                    .Text_Lambda([this, Shape, Label]()
                    {
                        return FText::FromString(ReadSpell().Shape == Shape
                            ? FString::Printf(TEXT("[ %s ]"), Label)
                            : FString(Label));
                    })
                ]
            ];
    };

    auto MakeDimension = [this, &MakeBindSelector, BlackText](
        const EEarthSpellShape Shape,
        const int32 Index,
        const ESpellLiveAction Action) -> TSharedRef<SWidget>
    {
        return SNew(SVerticalBox)
            .Visibility_Lambda([this, Shape]()
            {
                return ReadSpell().Shape == Shape ? EVisibility::Visible : EVisibility::Collapsed;
            })
            + SVerticalBox::Slot().AutoHeight().Padding(0, 3)
            [
                SNew(SHorizontalBox)
                + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0, 0, 8, 0)
                [ MakeBindSelector(Action) ]
                + SHorizontalBox::Slot().FillWidth(1.0f).VAlign(VAlign_Center)
                [
                    SNew(STextBlock)
                    .ColorAndOpacity(BlackText)
                    .Text_Lambda([this, Index]() { return GetDimensionLabel(Index); })
                ]
            ]
            + SVerticalBox::Slot().AutoHeight().Padding(100, 0, 0, 9)
            [
                SNew(SSlider)
                .IsFocusable(false)
                .Value_Lambda([this, Index]() { return GetDimensionSlider(Index); })
                .OnValueChanged_Lambda([this, Index](float V) { SetDimensionSlider(Index, V); })
            ];
    };

    auto Section = [BlackText](const TCHAR* Title) -> TSharedRef<SWidget>
    {
        return SNew(SBorder)
            .Padding(FMargin(8.0f, 6.0f))
            .BorderBackgroundColor(FLinearColor(0.78f, 0.76f, 0.70f, 0.96f))
            [
                SNew(STextBlock)
                .ColorAndOpacity(BlackText)
                .Text(FText::FromString(Title))
            ];
    };

    EditorWidget = SNew(SBox)
        .HAlign(HAlign_Center)
        .VAlign(VAlign_Center)
        [
            SNew(SBorder)
            .Padding(FMargin(24.0f))
            .BorderBackgroundColor(FLinearColor(0.92f, 0.90f, 0.84f, 0.96f))
            [
                SNew(SBox)
                .WidthOverride(820.0f)
                .HeightOverride(760.0f)
                [
                    SNew(SScrollBox)
                    + SScrollBox::Slot()
                    [
                        SNew(SVerticalBox)

                        + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0, 0, 0, 4)
                        [ SNew(STextBlock).ColorAndOpacity(BlackText).Text(FText::FromString(TEXT("MEDITATION REALM / EARTH SPELL CONSTRUCTION"))) ]

                        + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0, 0, 0, 8)
                        [ SNew(STextBlock).ColorAndOpacity(BlackText).Text(FText::FromString(TEXT("Sliders are persistent defaults. Key boxes configure temporary live overrides. Press the same assigned key again to clear it."))) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 7)
                        [ SNew(STextBlock).ColorAndOpacity(BlackText).Text(FText::FromString(TEXT("LIVE HOLD: unpressed = TAB default; press starts at minimum; 1 s small, 2 s medium, 3 s maximum."))) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 14)
                        [ SNew(STextBlock).ColorAndOpacity(BlackText).Text_Lambda([this]() { return GetCurrentSpellSummary(); }) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 3)
                        [ Section(TEXT("ELEMENT")) ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0, 4, 0, 8)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0, 0, 8, 0)
                            [ MakeBindSelector(ESpellLiveAction::SelectEarth) ]
                            + SHorizontalBox::Slot().FillWidth(1.0f).VAlign(VAlign_Center)
                            [ SNew(STextBlock).ColorAndOpacity(BlackText).Text(FText::FromString(TEXT("EARTH  (tap = select; green aura confirms it)"))) ]
                        ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
                        [ Section(TEXT("SHAPE")) ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0, 4, 0, 4)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().Padding(0,0,14,0)[MakeShapeControl(ESpellLiveAction::SelectSphere, EEarthSpellShape::Sphere, TEXT("Sphere"))]
                            + SHorizontalBox::Slot().AutoWidth().Padding(0,0,14,0)[MakeShapeControl(ESpellLiveAction::SelectCube, EEarthSpellShape::Cube, TEXT("Cube"))]
                            + SHorizontalBox::Slot().AutoWidth()[MakeShapeControl(ESpellLiveAction::SelectCone, EEarthSpellShape::Cone, TEXT("Cone"))]
                        ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
                        [ Section(TEXT("SIZE / SHAPE DIMENSIONS")) ]
                        + SVerticalBox::Slot().AutoHeight()[MakeDimension(EEarthSpellShape::Sphere, 0, ESpellLiveAction::SphereRadius)]
                        + SVerticalBox::Slot().AutoHeight()[MakeDimension(EEarthSpellShape::Cube, 0, ESpellLiveAction::CubeX)]
                        + SVerticalBox::Slot().AutoHeight()[MakeDimension(EEarthSpellShape::Cube, 1, ESpellLiveAction::CubeY)]
                        + SVerticalBox::Slot().AutoHeight()[MakeDimension(EEarthSpellShape::Cube, 2, ESpellLiveAction::CubeZ)]
                        + SVerticalBox::Slot().AutoHeight()[MakeDimension(EEarthSpellShape::Cone, 0, ESpellLiveAction::ConeRadius)]
                        + SVerticalBox::Slot().AutoHeight()[MakeDimension(EEarthSpellShape::Cone, 1, ESpellLiveAction::ConeHeight)]

                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
                        [ Section(TEXT("MOTION / MATERIAL")) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,8,0)[MakeBindSelector(ESpellLiveAction::Speed)]
                            + SHorizontalBox::Slot().FillWidth(1.0f).VAlign(VAlign_Center)
                            [ SNew(STextBlock).ColorAndOpacity(BlackText).Text_Lambda([this](){ return FText::FromString(FString::Printf(TEXT("Speed: %.1f m/s   (0 = create; gravity still applies)"), ReadSpell().SpeedMps)); }) ]
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(100,0,0,9)
                        [ SNew(SSlider).IsFocusable(false).Value_Lambda([this](){ return GetSpeedSlider(); }).OnValueChanged_Lambda([this](float V){ SetSpeedSlider(V); }) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,8,0)[MakeBindSelector(ESpellLiveAction::Density)]
                            + SHorizontalBox::Slot().FillWidth(1.0f).VAlign(VAlign_Center)
                            [ SNew(STextBlock).ColorAndOpacity(BlackText).Text_Lambda([this](){ return FText::FromString(FString::Printf(TEXT("Density: %.0f kg/m3   |   derived mass: %.1f kg"), ReadSpell().DensityKgPerM3, UEarthSpellMath::CalculateMassKg(ReadSpell()))); }) ]
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(100,0,0,9)
                        [ SNew(SSlider).IsFocusable(false).Value_Lambda([this](){ return GetDensitySlider(); }).OnValueChanged_Lambda([this](float V){ SetDensitySlider(V); }) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,8,0)[MakeBindSelector(ESpellLiveAction::Hardness)]
                            + SHorizontalBox::Slot().FillWidth(1.0f).VAlign(VAlign_Center)
                            [ SNew(STextBlock).ColorAndOpacity(BlackText).Text_Lambda([this](){ return FText::FromString(FString::Printf(TEXT("Hardness: %.2f"), ReadSpell().Hardness)); }) ]
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(100,0,0,9)
                        [ SNew(SSlider).IsFocusable(false).Value_Lambda([this](){ return GetHardnessSlider(); }).OnValueChanged_Lambda([this](float V){ SetHardnessSlider(V); }) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,8,0)[MakeBindSelector(ESpellLiveAction::Toughness)]
                            + SHorizontalBox::Slot().FillWidth(1.0f).VAlign(VAlign_Center)
                            [ SNew(STextBlock).ColorAndOpacity(BlackText).Text_Lambda([this](){ return FText::FromString(FString::Printf(TEXT("Toughness: %.2f"), ReadSpell().Toughness)); }) ]
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(100,0,0,9)
                        [ SNew(SSlider).IsFocusable(false).Value_Lambda([this](){ return GetToughnessSlider(); }).OnValueChanged_Lambda([this](float V){ SetToughnessSlider(V); }) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,8,0)[MakeBindSelector(ESpellLiveAction::Elasticity)]
                            + SHorizontalBox::Slot().FillWidth(1.0f).VAlign(VAlign_Center)
                            [ SNew(STextBlock).ColorAndOpacity(BlackText).Text_Lambda([this](){ return FText::FromString(FString::Printf(TEXT("Elasticity: %.2f"), ReadSpell().Elasticity)); }) ]
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(100,0,0,9)
                        [ SNew(SSlider).IsFocusable(false).Value_Lambda([this](){ return GetElasticitySlider(); }).OnValueChanged_Lambda([this](float V){ SetElasticitySlider(V); }) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,7,0,3)
                        [ Section(TEXT("SPATIAL")) ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,8,0)[MakeBindSelector(ESpellLiveAction::Distance)]
                            + SHorizontalBox::Slot().FillWidth(1.0f).VAlign(VAlign_Center)
                            [ SNew(STextBlock).ColorAndOpacity(BlackText).Text_Lambda([this](){ return FText::FromString(FString::Printf(TEXT("Distance: %.1f m   (additional distance from safe point in front of character)"), ReadSpell().DistanceM)); }) ]
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(100,0,0,9)
                        [ SNew(SSlider).IsFocusable(false).Value_Lambda([this](){ return GetDistanceSlider(); }).OnValueChanged_Lambda([this](float V){ SetDistanceSlider(V); }) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,10,0,0)
                        [ SNew(STextBlock).ColorAndOpacity(BlackText).Text(FText::FromString(TEXT("DEFAULT LIVE TEST: Q Earth | A primary shape dimension | S Speed | D Density | SPACE casts only after construction starts."))) ]
                    ]
                ]
            ]
        ];

    GEngine->GameViewport->AddViewportWidgetContent(EditorWidget.ToSharedRef(), 5000);
}

void UInnerRealmSubsystem::RemoveEditorWidget()
{
    if (EditorWidget.IsValid() && GEngine && GEngine->GameViewport)
    {
        GEngine->GameViewport->RemoveViewportWidgetContent(EditorWidget.ToSharedRef());
    }
    EditorWidget.Reset();
}
