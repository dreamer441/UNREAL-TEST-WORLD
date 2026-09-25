#include "SpellExecutionSubsystem.h"

#include "EarthSpellSpawner.h"
#include "LiveSpellSessionSubsystem.h"
#include "PlayerViewModeSubsystem.h"
#include "SpellCastPlacement.h"
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
    if (Controller && Controller->WasInputKeyJustPressed(EKeys::SpaceBar))
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

    bool bSpawned = false;
    switch (ResolvedSpell.Definition.Element)
    {
    case ESpellElement::Earth:
        bSpawned = FEarthSpellSpawner::SpawnAndLaunch(
            World,
            Controller,
            ResolvedSpell,
            Placement.SpawnLocation,
            Placement.SpawnRotation,
            Placement.LaunchDirection) != nullptr;
        break;
    default:
        return FSpellExecutionResult::ForOutcome(ESpellExecutionOutcome::UnsupportedElement);
    }

    if (!bSpawned)
    {
        return FSpellExecutionResult::ForOutcome(ESpellExecutionOutcome::SpawnFailed);
    }

    // Only a successfully realized spell consumes temporary live construction.
    LiveSession->ResetSession();
    return FSpellExecutionResult::ForOutcome(ESpellExecutionOutcome::Executed, true);
}
