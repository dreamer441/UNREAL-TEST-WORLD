#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "EarthSpellDefinition.h"
#include "SpellDefinition.h"
#include "SpellCreationSubsystem.generated.h"

/**
 * Data node for spell construction.
 * Owns canonical generic spell data and a synchronized legacy reflected shadow.
 */
UCLASS()
class SPELLCREATION_API USpellCreationSubsystem : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    UFUNCTION(BlueprintPure, Category="Spell Creation")
    FSpellDefinition GetStoredGenericSpellDefinition() const { return StoredGenericSpell; }

    UFUNCTION(BlueprintCallable, Category="Spell Creation")
    void SetStoredGenericSpellDefinition(const FSpellDefinition& NewSpell);

    UFUNCTION(BlueprintPure, Category="Spell Creation")
    FEarthSpellDefinition GetStoredSpellDefinition() const { return StoredSpell; }

    UFUNCTION(BlueprintCallable, Category="Spell Creation")
    void SetStoredSpellDefinition(const FEarthSpellDefinition& NewSpell);

    UFUNCTION(BlueprintCallable, Category="Spell Creation")
    void ResetToDefaultEarthSpell();

private:
    UPROPERTY()
    FEarthSpellDefinition StoredSpell;

    /** Canonical runtime value; StoredSpell retains the original reflected type. */
    UPROPERTY()
    FSpellDefinition StoredGenericSpell;
};
