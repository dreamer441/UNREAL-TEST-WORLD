#pragma once

#include "CoreMinimal.h"
#include "EarthSpellDefinition.h"
#include "EarthSpellMath.generated.h"

/** Pure shape/body math. No world, actor, UI, or impact responsibilities. */
UCLASS()
class SPELLCREATION_API UEarthSpellMath : public UObject
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintPure, Category="Spell|Math")
    static float CalculateVolumeM3(const FEarthSpellDefinition& Spell);

    UFUNCTION(BlueprintPure, Category="Spell|Math")
    static float CalculateDensityKgPerM3(const FEarthSpellDefinition& Spell);

    UFUNCTION(BlueprintPure, Category="Spell|Math")
    static float CalculateMassKg(const FEarthSpellDefinition& Spell);

    UFUNCTION(BlueprintPure, Category="Spell|Math")
    static float CalculateContactRadiusCm(const FEarthSpellDefinition& Spell);

    UFUNCTION(BlueprintPure, Category="Spell|Math")
    static FVector CalculateHalfExtentsCm(const FEarthSpellDefinition& Spell);
};
