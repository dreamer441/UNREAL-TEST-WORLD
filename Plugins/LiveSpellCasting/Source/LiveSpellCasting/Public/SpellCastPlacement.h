#pragma once

#include "CoreMinimal.h"
#include "EarthSpellDefinition.h"

class APlayerController;

struct LIVESPELLCASTING_API FResolvedSpellCastPlacement
{
    FVector SpawnLocation = FVector::ZeroVector;
    FVector LaunchDirection = FVector::ForwardVector;
    FRotator SpawnRotation = FRotator::ZeroRotator;
};

/** Shared character-relative spawn placement used by both preview and execution. */
struct LIVESPELLCASTING_API FSpellCastPlacement
{
    static bool Resolve(
        APlayerController* PlayerController,
        const FEarthSpellDefinition& Spell,
        const FVector& DesiredAimDirection,
        FResolvedSpellCastPlacement& OutPlacement);
};
