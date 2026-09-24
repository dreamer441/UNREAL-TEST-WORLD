#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "EarthTestInputSubsystem.generated.h"

/**
 * Disposable execution harness.
 * SPACE executes only an active LiveSpellSession; no session means no cast.
 * It owns no spell defaults, bindings, shape logic, material physics, or impacts.
 */
UCLASS()
class EARTHTESTHARNESS_API UEarthTestInputSubsystem : public UTickableWorldSubsystem
{
    GENERATED_BODY()
public:
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;

private:
    void ExecuteLiveEarthSpell();
};
