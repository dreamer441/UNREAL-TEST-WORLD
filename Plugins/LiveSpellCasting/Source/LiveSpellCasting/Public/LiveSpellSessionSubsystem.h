#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "EarthSpellDefinition.h"
#include "LiveSpellSessionSubsystem.generated.h"

/** A live overrideable numeric property. Missing entry = formal live state 0 / use TAB default. */
UENUM()
enum class ELiveSpellParameter : uint8
{
    SphereRadius,
    CubeX,
    CubeY,
    CubeZ,
    ConeRadius,
    ConeHeight,
    Speed,
    Density,
    Distance,
    Hardness,
    Toughness,
    Elasticity
};

/** Explicit construction hierarchy for live casting. */
UENUM()
enum class ELiveSpellStage : uint8
{
    Empty,
    ElementSelected,
    ShapeSelected,
    ModifierActive
};

/**
 * One transient live spell construction.
 *
 * Construction is intentionally hierarchical:
 *   Element -> Shape -> Modifier -> Cast
 *
 * SpellCreation keeps persistent TAB defaults. This node stores only the
 * temporary choices made during live casting. Inactive numeric parameters
 * fall back to persistent TAB defaults, except Speed: live casts always start
 * at 0 m/s and only gain speed when the Speed modifier is explicitly used.
 */
UCLASS()
class LIVESPELLCASTING_API ULiveSpellSessionSubsystem : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    void ResetSession();

    ELiveSpellStage GetStage() const { return Stage; }
    bool HasConstruction() const { return Stage != ELiveSpellStage::Empty; }
    bool HasElement() const { return Stage >= ELiveSpellStage::ElementSelected; }
    bool HasExplicitShape() const { return Stage >= ELiveSpellStage::ShapeSelected && bHasShapeOverride; }
    bool HasModifier() const { return Stage >= ELiveSpellStage::ModifierActive && ParameterOverrides01.Num() > 0; }
    bool CanSelectShape() const { return HasElement(); }
    bool CanApplyModifier() const { return HasExplicitShape(); }
    bool CanCast() const { return HasElement() && HasExplicitShape() && HasModifier(); }

    /** Starts/restarts the construction at the element stage. */
    void SelectEarth();
    bool IsEarthExplicitlySelected() const { return bEarthExplicitlySelected; }

    /** Ignored until an element has been selected. Selecting a shape clears old modifiers. */
    void SelectShape(EEarthSpellShape Shape);
    bool HasShapeOverride() const { return bHasShapeOverride; }
    EEarthSpellShape GetResolvedShape() const;

    /** Ignored until both element and shape are explicitly selected. */
    void SetParameterNormalized(ELiveSpellParameter Parameter, float NormalizedValue);
    bool IsParameterActive(ELiveSpellParameter Parameter) const;
    float GetParameterNormalized(ELiveSpellParameter Parameter) const;

    /** Persistent defaults + live overrides. Speed is forced to 0 until explicitly activated. */
    FEarthSpellDefinition ResolveSpell() const;

    /** Increments whenever construction is reset/consumed/restarted. */
    uint32 GetGeneration() const { return Generation; }

private:
    ELiveSpellStage Stage = ELiveSpellStage::Empty;
    bool bEarthExplicitlySelected = false;
    bool bHasShapeOverride = false;
    EEarthSpellShape ShapeOverride = EEarthSpellShape::Sphere;
    TMap<ELiveSpellParameter, float> ParameterOverrides01;
    uint32 Generation = 0;

    FEarthSpellDefinition GetPersistentDefaults() const;
};
