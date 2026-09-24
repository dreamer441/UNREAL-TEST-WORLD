#include "InnerRealmActor.h"

#include "Camera/CameraComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

AInnerRealmActor::AInnerRealmActor()
{
    PrimaryActorTick.bCanEverTick = false;

    Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    SetRootComponent(Root);

    RealmCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("RealmCamera"));
    RealmCamera->SetupAttachment(Root);
    RealmCamera->SetRelativeLocation(FVector::ZeroVector);
    RealmCamera->SetRelativeRotation(FRotator::ZeroRotator);
    RealmCamera->FieldOfView = 60.0f;

    BlankPlane = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BlankPlane"));
    BlankPlane->SetupAttachment(Root);
    BlankPlane->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    BlankPlane->SetCastShadow(false);
    BlankPlane->SetRelativeLocation(FVector(600.0f, 0.0f, 0.0f));
    BlankPlane->SetRelativeRotation(FRotator(90.0f, 0.0f, 0.0f));
    BlankPlane->SetRelativeScale3D(FVector(35.0f, 35.0f, 35.0f));

    static ConstructorHelpers::FObjectFinder<UStaticMesh> PlaneMesh(TEXT("/Engine/BasicShapes/Plane.Plane"));
    if (PlaneMesh.Succeeded())
    {
        BlankPlane->SetStaticMesh(PlaneMesh.Object);
    }

    static ConstructorHelpers::FObjectFinder<UMaterialInterface> PlaneMaterial(
        TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
    if (PlaneMaterial.Succeeded())
    {
        BlankPlane->SetMaterial(0, PlaneMaterial.Object);
    }

    RealmLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("RealmLight"));
    RealmLight->SetupAttachment(Root);
    RealmLight->SetRelativeLocation(FVector(250.0f, 0.0f, 150.0f));
    RealmLight->SetIntensity(10000.0f);
    RealmLight->SetAttenuationRadius(2500.0f);
    RealmLight->SetCastShadows(false);
}
