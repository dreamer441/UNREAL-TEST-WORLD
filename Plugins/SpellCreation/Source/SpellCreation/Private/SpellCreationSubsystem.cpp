#include "SpellCreationSubsystem.h"

#include "EarthSpellMath.h"

namespace SpellCreationNormalization
{
    static FEarthSpellDefinition Normalize(FEarthSpellDefinition Spell)
    {
        Spell.SphereRadiusCm = FMath::Max(Spell.SphereRadiusCm, 1.0f);
        Spell.CubeXcm = FMath::Max(Spell.CubeXcm, 1.0f);
        Spell.CubeYcm = FMath::Max(Spell.CubeYcm, 1.0f);
        Spell.CubeZcm = FMath::Max(Spell.CubeZcm, 1.0f);
        Spell.ConeRadiusCm = FMath::Max(Spell.ConeRadiusCm, 1.0f);
        Spell.ConeHeightCm = FMath::Max(Spell.ConeHeightCm, 1.0f);
        Spell.DistanceM = FMath::Max(Spell.DistanceM, 0.0f);
        Spell.SpeedMps = FMath::Max(Spell.SpeedMps, 0.0f);
        Spell.DensityKgPerM3 = FMath::Max(Spell.DensityKgPerM3, 1.0f);
        Spell.Hardness = FMath::Clamp(Spell.Hardness, 0.0f, 1.0f);
        Spell.Toughness = FMath::Clamp(Spell.Toughness, 0.0f, 1.0f);
        Spell.Elasticity = FMath::Clamp(Spell.Elasticity, 0.0f, 1.0f);
        Spell.Cohesion = FMath::Clamp(Spell.Cohesion, 0.0f, 1.0f);
        Spell.Rigidity = FMath::Clamp(Spell.Rigidity, 0.0f, 1.0f);
        Spell.MassKg = UEarthSpellMath::CalculateMassKg(Spell);
        return Spell;
    }
}

void USpellCreationSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    ResetToDefaultEarthSpell();
}

void USpellCreationSubsystem::SetStoredSpellDefinition(const FEarthSpellDefinition& NewSpell)
{
    StoredSpell = SpellCreationNormalization::Normalize(NewSpell);
}

void USpellCreationSubsystem::ResetToDefaultEarthSpell()
{
    StoredSpell = SpellCreationNormalization::Normalize(FEarthSpellDefinition());
}
