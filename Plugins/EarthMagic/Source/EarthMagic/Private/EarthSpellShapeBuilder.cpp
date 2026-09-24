#include "EarthSpellShapeBuilder.h"

#include "Engine/StaticMesh.h"
#include "UObject/UObjectGlobals.h"

UStaticMesh* FEarthSpellShapeBuilder::ResolveStaticMesh(const EEarthSpellShape Shape)
{
    // Engine BasicShapes are stable, convex, visible, and ship with collision.
    // Keeping the asset mapping inside this node prevents shape-specific asset knowledge
    // from leaking into the spell definition or impact code.
    switch (Shape)
    {
        case EEarthSpellShape::Sphere:
            return LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
        case EEarthSpellShape::Cube:
            return LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
        case EEarthSpellShape::Cone:
        default:
            return LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cone.Cone"));
    }
}

FVector FEarthSpellShapeBuilder::CalculateMeshScale(const FEarthSpellDefinition& Spell)
{
    // Engine basic sphere/cube/cone are approximately 100 cm in their base dimensions.
    // Sphere radius is 50 cm; cone base diameter is 100 cm and height is 100 cm.
    switch (Spell.Shape)
    {
        case EEarthSpellShape::Sphere:
        {
            const float Uniform = FMath::Max(Spell.SphereRadiusCm, 1.0f) / 50.0f;
            return FVector(Uniform);
        }
        case EEarthSpellShape::Cube:
            return FVector(
                FMath::Max(Spell.CubeXcm, 1.0f) / 100.0f,
                FMath::Max(Spell.CubeYcm, 1.0f) / 100.0f,
                FMath::Max(Spell.CubeZcm, 1.0f) / 100.0f);
        case EEarthSpellShape::Cone:
        default:
        {
            const float Radial = FMath::Max(Spell.ConeRadiusCm, 1.0f) / 50.0f;
            const float Height = FMath::Max(Spell.ConeHeightCm, 1.0f) / 100.0f;
            return FVector(Radial, Radial, Height);
        }
    }
}
