#include "EarthSpellMath.h"

namespace EarthSpellMathPrivate
{
    static float Cm3ToM3(const float VolumeCm3)
    {
        return VolumeCm3 / 1000000.0f;
    }
}

float UEarthSpellMath::CalculateVolumeM3(const FEarthSpellDefinition& Spell)
{
    switch (Spell.Shape)
    {
        case EEarthSpellShape::Sphere:
        {
            const float RadiusM = FMath::Max(Spell.SphereRadiusCm, 0.5f) * 0.01f;
            return (4.0f / 3.0f) * PI * RadiusM * RadiusM * RadiusM;
        }
        case EEarthSpellShape::Cube:
        {
            return EarthSpellMathPrivate::Cm3ToM3(
                FMath::Max(Spell.CubeXcm, 1.0f) *
                FMath::Max(Spell.CubeYcm, 1.0f) *
                FMath::Max(Spell.CubeZcm, 1.0f));
        }
        case EEarthSpellShape::Cone:
        default:
        {
            const float RadiusM = FMath::Max(Spell.ConeRadiusCm, 0.5f) * 0.01f;
            const float HeightM = FMath::Max(Spell.ConeHeightCm, 1.0f) * 0.01f;
            return (PI * RadiusM * RadiusM * HeightM) / 3.0f;
        }
    }
}

float UEarthSpellMath::CalculateDensityKgPerM3(const FEarthSpellDefinition& Spell)
{
    return FMath::Max(Spell.DensityKgPerM3, 1.0f);
}

float UEarthSpellMath::CalculateMassKg(const FEarthSpellDefinition& Spell)
{
    return FMath::Max(CalculateDensityKgPerM3(Spell) * CalculateVolumeM3(Spell), 0.01f);
}

float UEarthSpellMath::CalculateContactRadiusCm(const FEarthSpellDefinition& Spell)
{
    switch (Spell.Shape)
    {
        case EEarthSpellShape::Sphere:
            return FMath::Max(Spell.SphereRadiusCm, 0.5f);
        case EEarthSpellShape::Cube:
            return 0.5f * FMath::Max(FMath::Max(Spell.CubeYcm, Spell.CubeZcm), 1.0f);
        case EEarthSpellShape::Cone:
        default:
            return FMath::Max(Spell.ConeRadiusCm, 0.5f);
    }
}

FVector UEarthSpellMath::CalculateHalfExtentsCm(const FEarthSpellDefinition& Spell)
{
    switch (Spell.Shape)
    {
        case EEarthSpellShape::Sphere:
        {
            const float R = FMath::Max(Spell.SphereRadiusCm, 0.5f);
            return FVector(R, R, R);
        }
        case EEarthSpellShape::Cube:
            return FVector(
                FMath::Max(Spell.CubeXcm, 1.0f) * 0.5f,
                FMath::Max(Spell.CubeYcm, 1.0f) * 0.5f,
                FMath::Max(Spell.CubeZcm, 1.0f) * 0.5f);
        case EEarthSpellShape::Cone:
        default:
            return FVector(
                FMath::Max(Spell.ConeRadiusCm, 0.5f),
                FMath::Max(Spell.ConeRadiusCm, 0.5f),
                FMath::Max(Spell.ConeHeightCm, 1.0f) * 0.5f);
    }
}
