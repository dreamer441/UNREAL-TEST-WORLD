#include "LiveSpellSessionSubsystem.h"

#include "EarthSpellMath.h"
#include "LiveSpellRanges.h"
#include "SpellCreationSubsystem.h"

void ULiveSpellSessionSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    ResetSession();
}

void ULiveSpellSessionSubsystem::ResetSession()
{
    Stage = ELiveSpellStage::Empty;
    bEarthExplicitlySelected = false;
    bHasShapeOverride = false;
    ShapeOverride = EEarthSpellShape::Sphere;
    ParameterOverrides01.Empty();
    ++Generation;
}

void ULiveSpellSessionSubsystem::SelectEarth()
{
    // Element is the root of a live construction. Re-selecting/replacing the
    // element deliberately clears everything downstream so the hierarchy is
    // always rebuilt in order.
    bEarthExplicitlySelected = true;
    bHasShapeOverride = false;
    ShapeOverride = EEarthSpellShape::Sphere;
    ParameterOverrides01.Empty();
    Stage = ELiveSpellStage::ElementSelected;
    ++Generation;
}

void ULiveSpellSessionSubsystem::SelectShape(const EEarthSpellShape Shape)
{
    if (!CanSelectShape())
    {
        return;
    }

    ShapeOverride = Shape;
    bHasShapeOverride = true;

    // Changing shape invalidates all modifiers from the previous shape/build.
    // The player must deliberately apply modifiers again before casting.
    ParameterOverrides01.Empty();
    Stage = ELiveSpellStage::ShapeSelected;
    ++Generation;
}

FEarthSpellDefinition ULiveSpellSessionSubsystem::GetPersistentDefaults() const
{
    UWorld* World = GetWorld();
    const USpellCreationSubsystem* SpellCreation = World ? World->GetSubsystem<USpellCreationSubsystem>() : nullptr;
    return SpellCreation ? SpellCreation->GetStoredSpellDefinition() : FEarthSpellDefinition();
}

EEarthSpellShape ULiveSpellSessionSubsystem::GetResolvedShape() const
{
    return bHasShapeOverride ? ShapeOverride : GetPersistentDefaults().Shape;
}

void ULiveSpellSessionSubsystem::SetParameterNormalized(const ELiveSpellParameter Parameter, const float NormalizedValue)
{
    if (!CanApplyModifier())
    {
        return;
    }

    ParameterOverrides01.Add(Parameter, FMath::Clamp(NormalizedValue, 0.0f, 1.0f));
    Stage = ELiveSpellStage::ModifierActive;
}

bool ULiveSpellSessionSubsystem::IsParameterActive(const ELiveSpellParameter Parameter) const
{
    return ParameterOverrides01.Contains(Parameter);
}

float ULiveSpellSessionSubsystem::GetParameterNormalized(const ELiveSpellParameter Parameter) const
{
    if (const float* Value = ParameterOverrides01.Find(Parameter))
    {
        return *Value;
    }
    return 0.0f;
}

FEarthSpellDefinition ULiveSpellSessionSubsystem::ResolveSpell() const
{
    FEarthSpellDefinition Spell = GetPersistentDefaults();

    // Live casting treats speed differently from authored TAB defaults.
    // A freshly constructed live spell is stationary until the player
    // explicitly activates the Speed modifier key for this cast.
    Spell.SpeedMps = 0.0f;

    if (bHasShapeOverride)
    {
        Spell.Shape = ShapeOverride;
    }

    for (const TPair<ELiveSpellParameter, float>& Pair : ParameterOverrides01)
    {
        const float N = FMath::Clamp(Pair.Value, 0.0f, 1.0f);
        switch (Pair.Key)
        {
            case ELiveSpellParameter::SphereRadius:
                Spell.SphereRadiusCm = LiveSpellRanges::Denormalize(N, LiveSpellRanges::MinSphereRadiusCm, LiveSpellRanges::MaxSphereRadiusCm);
                break;
            case ELiveSpellParameter::CubeX:
                Spell.CubeXcm = LiveSpellRanges::Denormalize(N, LiveSpellRanges::MinCubeSideCm, LiveSpellRanges::MaxCubeSideCm);
                break;
            case ELiveSpellParameter::CubeY:
                Spell.CubeYcm = LiveSpellRanges::Denormalize(N, LiveSpellRanges::MinCubeSideCm, LiveSpellRanges::MaxCubeSideCm);
                break;
            case ELiveSpellParameter::CubeZ:
                Spell.CubeZcm = LiveSpellRanges::Denormalize(N, LiveSpellRanges::MinCubeSideCm, LiveSpellRanges::MaxCubeSideCm);
                break;
            case ELiveSpellParameter::ConeRadius:
                Spell.ConeRadiusCm = LiveSpellRanges::Denormalize(N, LiveSpellRanges::MinConeRadiusCm, LiveSpellRanges::MaxConeRadiusCm);
                break;
            case ELiveSpellParameter::ConeHeight:
                Spell.ConeHeightCm = LiveSpellRanges::Denormalize(N, LiveSpellRanges::MinConeHeightCm, LiveSpellRanges::MaxConeHeightCm);
                break;
            case ELiveSpellParameter::Speed:
                Spell.SpeedMps = LiveSpellRanges::Denormalize(N, LiveSpellRanges::MinSpeedMps, LiveSpellRanges::MaxSpeedMps);
                break;
            case ELiveSpellParameter::Density:
                Spell.DensityKgPerM3 = LiveSpellRanges::Denormalize(N, LiveSpellRanges::MinDensityKgPerM3, LiveSpellRanges::MaxDensityKgPerM3);
                break;
            case ELiveSpellParameter::Distance:
                Spell.DistanceM = LiveSpellRanges::Denormalize(N, LiveSpellRanges::MinDistanceM, LiveSpellRanges::MaxDistanceM);
                break;
            case ELiveSpellParameter::Hardness:
                Spell.Hardness = N;
                break;
            case ELiveSpellParameter::Toughness:
                Spell.Toughness = N;
                break;
            case ELiveSpellParameter::Elasticity:
                Spell.Elasticity = N;
                break;
        }
    }

    Spell.MassKg = UEarthSpellMath::CalculateMassKg(Spell);
    return Spell;
}
