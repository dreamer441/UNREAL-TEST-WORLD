#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "SpellPreviewSubsystem.generated.h"

/** Presentation-only live construction feedback. */
UCLASS()
class SPELLPREVIEW_API USpellPreviewSubsystem : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual void Tick(float DeltaSeconds) override;
    virtual TStatId GetStatId() const override;
};
