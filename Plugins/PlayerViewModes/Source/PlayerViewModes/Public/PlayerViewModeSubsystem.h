#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "PlayerViewModeSubsystem.generated.h"

class AActor;
class ACharacter;
class APlayerController;
class APlayerTopDownCamera;

/**
 * Input/mode coordinator. SHIFT switches third-person <-> top-down.
 * Top-down RMB: hold to follow cursor; LMB drag: orbit; scroll up repeatedly for sprint bursts.
 * InnerRealm owns TAB and gets priority; this subsystem preserves the view across meditation.
 * Never accesses SpellCreation, EarthMagic, Impact or MaterialCore.
 */
UCLASS()
class PLAYERVIEWMODES_API UPlayerViewModeSubsystem : public UTickableWorldSubsystem
{
    GENERATED_BODY()
public:
    virtual void Tick(float DeltaSeconds) override;
    virtual TStatId GetStatId() const override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintPure, Category="Player View")
    bool IsTopDown() const { return bTopDown; }

    /** Gameplay-facing aim contract: returns a player-based horizontal cast ray in top-down. */
    bool GetTopDownCastRay(FVector& OutOrigin, FVector& OutDirection) const;

private:
    TWeakObjectPtr<APlayerController> CachedController;
    TWeakObjectPtr<APlayerTopDownCamera> OrbitCamera;
    TWeakObjectPtr<AActor> SavedThirdPersonView;
    TWeakObjectPtr<ACharacter> SavedCharacter;

    bool bTopDown = false;
    bool bWasMeditating = false;
    // Unreal's SetIgnore*Input calls are STACKED. Acquire at most one pair,
    // and release the same pair once when leaving top-down. TAB's InnerRealm
    // independently acquires/releases its own pair during meditation.
    bool bOwnsTopDownInputLock = false;
    TWeakObjectPtr<APlayerController> InputLockController;
    bool bSprinting = false;
    // Mouse wheels emit discrete scroll pulses, never a sustained held key.
    // Repeated upward pulses refresh this window; sprint ends on timeout or RMB release.
    float SprintWindowRemainingSeconds = 0.0f;

    // Default Third Person Blueprint still binds Space to Jump. Keep that asset
    // unchanged, disable standard Character jumps at runtime and restore at shutdown.
    TWeakObjectPtr<ACharacter> JumpSuppressedCharacter;
    int32 PreviousJumpMaxCount = 1;
    bool bHaveDestination = false;
    FVector MoveDestination = FVector::ZeroVector;
    float OrbitYawDegrees = 0.0f;
    float OrbitElevationDegrees = 62.0f;
    float PreviousWalkSpeed = 500.0f;
    bool bPreviousOrientRotationToMovement = false;
    bool bPreviousUseControllerRotationYaw = false;

    void EnterTopDown(APlayerController* PC);
    void ExitTopDown(APlayerController* PC);
    void ReapplyTopDownInput(APlayerController* PC);
    void ReleaseTopDownInput();
    void HandleTopDownInput(APlayerController* PC, float DeltaSeconds);
    void UpdateCamera(APlayerController* PC);
    void SetSprint(bool bEnabled);
    void SuppressTemplateJump(APlayerController* PC);
    void RestoreTemplateJump();
    APlayerTopDownCamera* GetOrSpawnCamera();
    bool FindCursorWorldPoint(APlayerController* PC, FVector& OutPoint) const;
};
