#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "InnerRealmActor.generated.h"

class UCameraComponent;
class UPointLightComponent;
class USceneComponent;
class UStaticMeshComponent;

/**
 * Pure presentation actor for the meditation realm.
 * It contains only a fixed camera and a blank physical plane.
 */
UCLASS()
class INNERREALM_API AInnerRealmActor : public AActor
{
    GENERATED_BODY()

public:
    AInnerRealmActor();

private:
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USceneComponent> Root;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UCameraComponent> RealmCamera;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UStaticMeshComponent> BlankPlane;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UPointLightComponent> RealmLight;
};
