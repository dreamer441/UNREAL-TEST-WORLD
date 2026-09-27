#include "SpellExecutionSubsystem.h"

#include "EarthSpellSpawner.h"
#include "LiveSpellSessionSubsystem.h"
#include "PlayerViewModeSubsystem.h"
#include "SpellCastPlacement.h"
#include "SpellLoadoutSubsystem.h"
#include "SpellPatternResolver.h"
#include "SpellMotionResolver.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"

TStatId USpellExecutionSubsystem::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(USpellExecutionSubsystem, STATGROUP_Tickables);
}

void USpellExecutionSubsystem::SetExecutionSuspended(const bool bInSuspended)
{
    if (bInSuspended)
    {
        ++ExecutionSuspensionDepth;
    }
    else if (ExecutionSuspensionDepth > 0)
    {
        --ExecutionSuspensionDepth;
    }
}

void USpellExecutionSubsystem::Tick(const float DeltaSeconds)
{
    if (IsExecutionSuspended())
    {
        return;
    }

    UWorld* World = GetWorld();
    if (!World || !World->IsGameWorld())
    {
        return;
    }

    APlayerController* Controller = World->GetFirstPlayerController();
    if (!Controller)
    {
        return;
    }

    // Prepared spell slots 1..0: load first, SPACE remains the universal execution key.
    static const FKey SlotKeys[USpellLoadoutSubsystem::SlotCount] =
    {
        EKeys::One, EKeys::Two, EKeys::Three, EKeys::Four, EKeys::Five,
        EKeys::Six, EKeys::Seven, EKeys::Eight, EKeys::Nine, EKeys::Zero
    };

    if (USpellLoadoutSubsystem* Loadout = World->GetSubsystem<USpellLoadoutSubsystem>())
    {
        if (ULiveSpellSessionSubsystem* LiveSession = World->GetSubsystem<ULiveSpellSessionSubsystem>())
        {
            for (int32 SlotIndex = 0; SlotIndex < USpellLoadoutSubsystem::SlotCount; ++SlotIndex)
            {
                if (Controller->WasInputKeyJustPressed(SlotKeys[SlotIndex]))
                {
                    FSpellDefinition PreparedSpell;
                    if (Loadout->GetSlotSpell(SlotIndex, PreparedSpell))
                    {
                        Loadout->EquipSlot(SlotIndex);
                        LiveSession->LoadPreparedSpell(PreparedSpell);
                    }
                    break;
                }
            }
        }
    }

    if (Controller->WasInputKeyJustPressed(EKeys::SpaceBar))
    {
        ExecuteLiveSpell();
    }
}

FSpellExecutionResult USpellExecutionSubsystem::ExecuteLiveSpell()
{
    if (IsExecutionSuspended())
    {
        return FSpellExecutionResult::ForOutcome(ESpellExecutionOutcome::ExecutionSuspended);
    }

    UWorld* World = GetWorld();
    if (!World)
    {
        return FSpellExecutionResult::ForOutcome(ESpellExecutionOutcome::NoWorld);
    }

    APlayerController* Controller = World->GetFirstPlayerController();
    if (!Controller)
    {
        return FSpellExecutionResult::ForOutcome(ESpellExecutionOutcome::NoController);
    }

    ULiveSpellSessionSubsystem* LiveSession = World->GetSubsystem<ULiveSpellSessionSubsystem>();
    if (!LiveSession || !LiveSession->CanCast())
    {
        // The grammar is strict: Element -> Shape -> Modifier -> Cast.
        return FSpellExecutionResult::ForOutcome(ESpellExecutionOutcome::NoLiveConstruction);
    }

    const FResolvedSpell ResolvedSpell = LiveSession->ResolveGenericSpell();
    FVector AimDirection = FVector::ForwardVector;
    FVector ViewLocation;
    FRotator ViewRotation;
    Controller->GetPlayerViewPoint(ViewLocation, ViewRotation);
    AimDirection = ViewRotation.Vector().GetSafeNormal();

    if (const UPlayerViewModeSubsystem* Views = World->GetSubsystem<UPlayerViewModeSubsystem>())
    {
        FVector TopDownOrigin;
        FVector TopDownDirection;
        if (Views->GetTopDownCastRay(TopDownOrigin, TopDownDirection))
        {
            AimDirection = TopDownDirection;
        }
    }

    FResolvedSpellCastPlacement Placement;
    if (!FSpellCastPlacement::Resolve(Controller, ResolvedSpell, AimDirection, Placement))
    {
        return FSpellExecutionResult::ForOutcome(ESpellExecutionOutcome::PlacementFailed);
    }

    TArray<FResolvedPatternInstance> ResolvedInstances;
    FSpellPatternResolver::ResolveInstances(
        ResolvedSpell.Definition.Pattern,
        Placement.SpawnLocation,
        Placement.LaunchDirection,
        ResolvedInstances);

    const FQuat BaseSpellRotation = Placement.SpawnRotation.Quaternion();

    int32 SpawnedCount = 0;
    switch (ResolvedSpell.Definition.Element)
    {
    case ESpellElement::Earth:
        for (const FResolvedPatternInstance& Instance : ResolvedInstances)
        {
            const FQuat FinalRotation =
                Instance.PatternRotation * BaseSpellRotation;

            const FVector InstanceLaunchDirection =
                FSpellMotionResolver::ResolveDirection(
                    ResolvedSpell.Definition.MotionDirection,
                    ResolvedSpell.Definition.Pattern,
                    Instance.Location,
                    Placement.SpawnLocation,
                    Placement.LaunchDirection);

            if (FEarthSpellSpawner::SpawnAndLaunch(
                World,
                Controller,
                ResolvedSpell,
                Instance.Location,
                FinalRotation.Rotator(),
                InstanceLaunchDirection))
            {
                ++SpawnedCount;
            }
        }
        break;

    default:
        return FSpellExecutionResult::ForOutcome(ESpellExecutionOutcome::UnsupportedElement);
    }

    if (SpawnedCount <= 0)
    {
        return FSpellExecutionResult::ForOutcome(ESpellExecutionOutcome::SpawnFailed);
    }

    // Only a successfully realized spell consumes temporary live construction.
    LiveSession->ResetSession();
    return FSpellExecutionResult::ForOutcome(ESpellExecutionOutcome::Executed, true);
}
