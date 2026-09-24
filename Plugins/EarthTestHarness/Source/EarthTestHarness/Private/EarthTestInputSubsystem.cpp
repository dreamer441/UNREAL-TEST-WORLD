#include "EarthTestInputSubsystem.h"

#include "EarthSpellBody.h"
#include "InnerRealmSubsystem.h"
#include "LiveSpellSessionSubsystem.h"
#include "PlayerViewModeSubsystem.h"
#include "SpellCastPlacement.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"

void UEarthTestInputSubsystem::Tick(float DeltaTime)
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

    if (const UInnerRealmSubsystem* InnerRealm = World->GetSubsystem<UInnerRealmSubsystem>())
    {
        if (InnerRealm->IsActive())
        {
            return;
        }
    }

    if (PC->WasInputKeyJustPressed(EKeys::SpaceBar))
    {
        ExecuteLiveEarthSpell();
    }
}

TStatId UEarthTestInputSubsystem::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UEarthTestInputSubsystem, STATGROUP_Tickables);
}

void UEarthTestInputSubsystem::ExecuteLiveEarthSpell()
{
    UWorld* World = GetWorld();
    APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;
    ULiveSpellSessionSubsystem* LiveSession = World ? World->GetSubsystem<ULiveSpellSessionSubsystem>() : nullptr;
    if (!World || !PC || !LiveSession || !LiveSession->CanCast())
    {
        // Live casting is a strict grammar: Element -> Shape -> Modifier -> Cast.
        // SPACE is inert until the construction has reached the Modifier stage.
        return;
    }

    const FEarthSpellDefinition Spell = LiveSession->ResolveSpell();

    FVector AimDirection = FVector::ForwardVector;
    FVector ViewLocation;
    FRotator ViewRotation;
    PC->GetPlayerViewPoint(ViewLocation, ViewRotation);
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
    if (!FSpellCastPlacement::Resolve(PC, Spell, AimDirection, Placement))
    {
        return;
    }

    FActorSpawnParameters Params;
    Params.Owner = PC;
    Params.Instigator = PC->GetPawn();
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;

    if (AEarthSpellBody* Body = World->SpawnActor<AEarthSpellBody>(
        AEarthSpellBody::StaticClass(), Placement.SpawnLocation, Placement.SpawnRotation, Params))
    {
        Body->Configure(Spell);
        Body->Launch(Placement.LaunchDirection);

        // Casting consumes only the transient live construction. TAB defaults and
        // key assignments remain untouched; pressing SPACE again does nothing until
        // another live input starts a new construction.
        LiveSession->ResetSession();
    }
}
