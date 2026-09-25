#include "SpellCreationSubsystem.h"

void USpellCreationSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    ResetToDefaultEarthSpell();
}

void USpellCreationSubsystem::SetStoredGenericSpellDefinition(const FSpellDefinition& NewSpell)
{
    StoredGenericSpell = FSpellDefinitionAdapter::Resolve(NewSpell).Definition;
    StoredSpell = FSpellDefinitionAdapter::ToLegacyEarth(StoredGenericSpell);
}

void USpellCreationSubsystem::SetStoredSpellDefinition(const FEarthSpellDefinition& NewSpell)
{
    SetStoredGenericSpellDefinition(FSpellDefinitionAdapter::FromLegacyEarth(NewSpell));
}

void USpellCreationSubsystem::ResetToDefaultEarthSpell()
{
    SetStoredSpellDefinition(FEarthSpellDefinition());
}
