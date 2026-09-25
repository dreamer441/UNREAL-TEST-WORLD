#include "LiveSpellSessionSubsystem.h"
#include "SpellCreationSubsystem.h"
void ULiveSpellSessionSubsystem::Initialize(FSubsystemCollectionBase& Collection) { Super::Initialize(Collection); State.Reset(); }
void ULiveSpellSessionSubsystem::ResetSession() { State.Reset(); }
void ULiveSpellSessionSubsystem::SelectEarth() { State.SelectElement(ESpellElement::Earth); }
void ULiveSpellSessionSubsystem::SelectShape(EEarthSpellShape Shape) { State.SelectShape(Shape == EEarthSpellShape::Sphere ? ESpellShape::Sphere : Shape == EEarthSpellShape::Cube ? ESpellShape::Cube : ESpellShape::Cone); }
EEarthSpellShape ULiveSpellSessionSubsystem::GetResolvedShape() const { const ESpellShape Shape = State.HasExplicitShape() ? State.GetResolvedShape() : GetPersistentGenericDefaults().Shape; return Shape == ESpellShape::Sphere ? EEarthSpellShape::Sphere : Shape == ESpellShape::Cube ? EEarthSpellShape::Cube : EEarthSpellShape::Cone; }
void ULiveSpellSessionSubsystem::SetParameterNormalized(ELiveSpellParameter Parameter, float Value) { State.SetParameterNormalized(Parameter, Value); }
FSpellDefinition ULiveSpellSessionSubsystem::GetPersistentGenericDefaults() const { if (const UWorld* World = GetWorld()) if (const USpellCreationSubsystem* Creation = World->GetSubsystem<USpellCreationSubsystem>()) return Creation->GetStoredGenericSpellDefinition(); return FSpellDefinition(); }
FResolvedSpell ULiveSpellSessionSubsystem::ResolveGenericSpell() const { return State.Resolve(GetPersistentGenericDefaults()); }
FEarthSpellDefinition ULiveSpellSessionSubsystem::ResolveSpell() const { return FSpellDefinitionAdapter::ToLegacyEarth(ResolveGenericSpell().Definition); }
