#include "PlayerTopDownCamera.h"

#include "Camera/CameraComponent.h"
#include "Components/SceneComponent.h"
#include "GameFramework/SpringArmComponent.h"

APlayerTopDownCamera::APlayerTopDownCamera()
{
    PrimaryActorTick.bCanEverTick = false;
    Pivot = CreateDefaultSubobject<USceneComponent>(TEXT("FollowPivot"));
    SetRootComponent(Pivot);

    CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("OrbitBoom"));
    CameraBoom->SetupAttachment(Pivot);
    CameraBoom->TargetArmLength = 2200.0f; // cm; farther top-down overview for live casting
    CameraBoom->bUsePawnControlRotation = false;
    CameraBoom->bInheritPitch = false;
    CameraBoom->bInheritYaw = false;
    CameraBoom->bInheritRoll = false;
    CameraBoom->bDoCollisionTest = true;
    CameraBoom->ProbeSize = 14.0f;
    CameraBoom->bEnableCameraLag = true;
    CameraBoom->CameraLagSpeed = 9.0f;
    // Follow and orbit smoothing live in the camera presentation actor, never
    // in movement/input logic. Rotation lag keeps high-sensitivity dragging fluid.
    CameraBoom->bEnableCameraRotationLag = true;
    CameraBoom->CameraRotationLagSpeed = 14.0f;
    CameraBoom->bUseCameraLagSubstepping = true;

    Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("TopDownCamera"));
    Camera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
    Camera->SetFieldOfView(65.0f);

    SetOrbit(0.0f, 62.0f);
}

void APlayerTopDownCamera::SetOrbit(const float OrbitYaw, const float ElevationDegrees)
{
    // Spring arm extends opposite to its forward vector, placing camera above pawn.
    CameraBoom->SetRelativeRotation(FRotator(-ElevationDegrees, OrbitYaw, 0.0f));
}

void APlayerTopDownCamera::FollowPosition(const FVector& WorldLocation)
{
    // Keep the camera actor spatially near its player for World Partition.
    SetActorLocation(WorldLocation + FVector(0.0f, 0.0f, 130.0f));
}
