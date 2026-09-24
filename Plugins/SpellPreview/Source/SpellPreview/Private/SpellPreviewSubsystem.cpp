#include "SpellPreviewSubsystem.h"

#include "DrawDebugHelpers.h"
#include "EarthSpellDefinition.h"
#include "LiveSpellRanges.h"
#include "LiveSpellSessionSubsystem.h"
#include "PlayerViewModeSubsystem.h"
#include "SpellCastPlacement.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"

namespace
{
    constexpr float PreviewThickness = 1.8f;
    constexpr float SpeedRingThickness = 3.0f;

    int32 GetDensityGridSteps(const FEarthSpellDefinition& Spell)
    {
        const float N = LiveSpellRanges::Normalize(
            Spell.DensityKgPerM3,
            LiveSpellRanges::MinDensityKgPerM3,
            LiveSpellRanges::MaxDensityKgPerM3);

        // Intentionally visual rather than physical resolution: low density is a
        // sparse 4-step construction grid, maximum density reaches 15 steps.
        return FMath::Clamp(FMath::RoundToInt(FMath::Lerp(4.0f, 15.0f, N)), 4, 15);
    }

    int32 GetSpeedRingCount(const FEarthSpellDefinition& Spell)
    {
        const float SpeedMps = FMath::Max(Spell.SpeedMps, 0.0f);
        const float N = LiveSpellRanges::Normalize(
            SpeedMps,
            LiveSpellRanges::MinSpeedMps,
            LiveSpellRanges::MaxSpeedMps);

        // Visual speed language:
        //   zero -> 0 rings
        //   low  -> 1 ring
        //   mid  -> 2 rings
        //   high -> 3 rings
        // Use a tiny dead-zone so a nominal zero never renders a stray ring
        // because of floating-point/slider residue.
        if (SpeedMps <= 0.1f || N <= 0.001f)
        {
            return 0;
        }
        if (N < (1.0f / 3.0f))
        {
            return 1;
        }
        if (N < (2.0f / 3.0f))
        {
            return 2;
        }
        return 3;
    }

    FVector RotateLocal(const FQuat& Rotation, const FVector& Local)
    {
        return Rotation.RotateVector(Local);
    }

    FVector ToWorld(const FVector& Center, const FQuat& Rotation, const FVector& Local)
    {
        return Center + RotateLocal(Rotation, Local);
    }

    void DrawPreviewCircle(
        UWorld* World,
        const FVector& Center,
        const float Radius,
        const FVector& PlaneAxisA,
        const FVector& PlaneAxisB,
        const FColor& Color,
        const float Thickness)
    {
        DrawDebugCircle(
            World,
            Center,
            FMath::Max(Radius, 1.0f),
            48,
            Color,
            false,
            0.0f,
            0,
            Thickness,
            PlaneAxisA,
            PlaneAxisB,
            false);
    }

    void DrawSphereDensityGrid(
        UWorld* World,
        const FVector& Center,
        const float Radius,
        const FQuat& Rotation,
        const int32 GridSteps,
        const FColor& Color)
    {
        const FVector X = RotateLocal(Rotation, FVector::ForwardVector);
        const FVector Y = RotateLocal(Rotation, FVector::RightVector);
        const FVector Z = RotateLocal(Rotation, FVector::UpVector);

        // Latitude bands.
        for (int32 I = 1; I < GridSteps; ++I)
        {
            const float T = -1.0f + 2.0f * (static_cast<float>(I) / static_cast<float>(GridSteps));
            const float LocalZ = Radius * T;
            const float CircleRadius = Radius * FMath::Sqrt(FMath::Max(0.0f, 1.0f - T * T));
            DrawPreviewCircle(World, Center + Z * LocalZ, CircleRadius, X, Y, Color, PreviewThickness);
        }

        // Longitude bands. A half-turn gives all unique great-circle planes.
        for (int32 I = 0; I < GridSteps; ++I)
        {
            const float Angle = PI * static_cast<float>(I) / static_cast<float>(GridSteps);
            const FVector Horizontal = (X * FMath::Cos(Angle) + Y * FMath::Sin(Angle)).GetSafeNormal();
            DrawPreviewCircle(World, Center, Radius, Horizontal, Z, Color, PreviewThickness);
        }
    }

    void DrawCubeDensityGrid(
        UWorld* World,
        const FVector& Center,
        const FVector& Half,
        const FQuat& Rotation,
        const int32 GridSteps,
        const FColor& Color)
    {
        auto Line = [&](const FVector& A, const FVector& B)
        {
            DrawDebugLine(World, ToWorld(Center, Rotation, A), ToWorld(Center, Rotation, B), Color, false, 0.0f, 0, PreviewThickness);
        };

        for (int32 I = 1; I < GridSteps; ++I)
        {
            const float T = -1.0f + 2.0f * (static_cast<float>(I) / static_cast<float>(GridSteps));

            const float Y = Half.Y * T;
            const float Z = Half.Z * T;
            for (const float FaceX : {-Half.X, Half.X})
            {
                Line(FVector(FaceX, Y, -Half.Z), FVector(FaceX, Y, Half.Z));
                Line(FVector(FaceX, -Half.Y, Z), FVector(FaceX, Half.Y, Z));
            }

            const float X = Half.X * T;
            for (const float FaceY : {-Half.Y, Half.Y})
            {
                Line(FVector(X, FaceY, -Half.Z), FVector(X, FaceY, Half.Z));
                Line(FVector(-Half.X, FaceY, Z), FVector(Half.X, FaceY, Z));
            }

            for (const float FaceZ : {-Half.Z, Half.Z})
            {
                Line(FVector(X, -Half.Y, FaceZ), FVector(X, Half.Y, FaceZ));
                Line(FVector(-Half.X, Y, FaceZ), FVector(Half.X, Y, FaceZ));
            }
        }
    }

    void DrawConeDensityGrid(
        UWorld* World,
        const FVector& Center,
        const float Radius,
        const float Height,
        const FQuat& Rotation,
        const int32 GridSteps,
        const FColor& Color)
    {
        const FVector X = RotateLocal(Rotation, FVector::ForwardVector);
        const FVector Y = RotateLocal(Rotation, FVector::RightVector);
        const FVector Z = RotateLocal(Rotation, FVector::UpVector);
        const FVector Apex = Center + Z * (Height * 0.5f);
        const FVector BaseCenter = Center - Z * (Height * 0.5f);

        // Vertical/radial construction lines.
        for (int32 I = 0; I < GridSteps; ++I)
        {
            const float Angle = 2.0f * PI * static_cast<float>(I) / static_cast<float>(GridSteps);
            const FVector Radial = X * FMath::Cos(Angle) + Y * FMath::Sin(Angle);
            DrawDebugLine(World, Apex, BaseCenter + Radial * Radius, Color, false, 0.0f, 0, PreviewThickness);
        }

        // Horizontal rings grow from apex to base.
        for (int32 I = 1; I <= GridSteps; ++I)
        {
            const float Alpha = static_cast<float>(I) / static_cast<float>(GridSteps);
            const FVector RingCenter = Apex - Z * (Height * Alpha);
            DrawPreviewCircle(World, RingCenter, Radius * Alpha, X, Y, Color, PreviewThickness);
        }
    }

    void DrawSpeedBands(
        UWorld* World,
        const FVector& Center,
        const FVector& HalfExtents,
        const FQuat& Rotation,
        const int32 RingCount,
        const FColor& Color)
    {
        if (RingCount <= 0)
        {
            return;
        }

        const FVector X = RotateLocal(Rotation, FVector::ForwardVector);
        const FVector Y = RotateLocal(Rotation, FVector::RightVector);
        const FVector Z = RotateLocal(Rotation, FVector::UpVector);

        const float RadiusAroundZ = FMath::Max(FMath::Sqrt(HalfExtents.X * HalfExtents.X + HalfExtents.Y * HalfExtents.Y) * 1.08f, 12.0f);
        const float RadiusAroundY = FMath::Max(FMath::Sqrt(HalfExtents.X * HalfExtents.X + HalfExtents.Z * HalfExtents.Z) * 1.08f, 12.0f);

        auto OffsetFraction = [RingCount](const int32 Index)
        {
            if (RingCount == 1)
            {
                return 0.0f;
            }
            if (RingCount == 2)
            {
                return Index == 0 ? -0.24f : 0.24f;
            }
            return Index == 0 ? -0.34f : (Index == 1 ? 0.0f : 0.34f);
        };

        for (int32 I = 0; I < RingCount; ++I)
        {
            const float Offset = OffsetFraction(I);

            // Ring around local Z axis (XY plane).
            DrawPreviewCircle(
                World,
                Center + Z * (HalfExtents.Z * Offset),
                RadiusAroundZ,
                X,
                Y,
                Color,
                SpeedRingThickness);

            // Ring around local Y axis (XZ plane).
            DrawPreviewCircle(
                World,
                Center + Y * (HalfExtents.Y * Offset),
                RadiusAroundY,
                X,
                Z,
                Color,
                SpeedRingThickness);
        }
    }
}

TStatId USpellPreviewSubsystem::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(USpellPreviewSubsystem, STATGROUP_Tickables);
}

void USpellPreviewSubsystem::Tick(float DeltaSeconds)
{
    UWorld* World = GetWorld();
    if (!World || !World->IsGameWorld())
    {
        return;
    }

    ULiveSpellSessionSubsystem* Session = World->GetSubsystem<ULiveSpellSessionSubsystem>();
    const UPlayerViewModeSubsystem* Views = World->GetSubsystem<UPlayerViewModeSubsystem>();
    APlayerController* PC = World->GetFirstPlayerController();
    APawn* Pawn = PC ? PC->GetPawn() : nullptr;

    if (!Session || !Views || !PC || !Pawn || !Views->IsTopDown() || !Session->HasConstruction())
    {
        return;
    }

    const FColor EarthGreen(60, 220, 95, 105);
    const FColor SpeedGreen(155, 255, 185, 150);

    if (Session->IsEarthExplicitlySelected())
    {
        const FVector AuraCenter = Pawn->GetActorLocation() + FVector(0.0f, 0.0f, 75.0f);
        DrawDebugSphere(World, AuraCenter, 90.0f, 24, EarthGreen, false, 0.0f, 0, 2.0f);
        DrawDebugSphere(World, AuraCenter, 112.0f, 24, EarthGreen, false, 0.0f, 0, 1.0f);
    }

    if (!Session->HasExplicitShape())
    {
        return;
    }

    const FEarthSpellDefinition Spell = Session->ResolveSpell();
    FVector AimOrigin;
    FVector AimDirection;
    if (!Views->GetTopDownCastRay(AimOrigin, AimDirection))
    {
        AimDirection = Pawn->GetActorForwardVector();
    }

    FResolvedSpellCastPlacement Placement;
    if (!FSpellCastPlacement::Resolve(PC, Spell, AimDirection, Placement))
    {
        return;
    }

    const FQuat ShapeRotation = Placement.SpawnRotation.Quaternion();
    const int32 DensityGridSteps = GetDensityGridSteps(Spell);

    FVector PreviewHalfExtents(50.0f);

    switch (Spell.Shape)
    {
        case EEarthSpellShape::Sphere:
        {
            const float Radius = FMath::Max(Spell.SphereRadiusCm, 1.0f);
            PreviewHalfExtents = FVector(Radius);
            DrawSphereDensityGrid(World, Placement.SpawnLocation, Radius, ShapeRotation, DensityGridSteps, EarthGreen);
            break;
        }

        case EEarthSpellShape::Cube:
        {
            PreviewHalfExtents = FVector(
                FMath::Max(Spell.CubeXcm, 1.0f) * 0.5f,
                FMath::Max(Spell.CubeYcm, 1.0f) * 0.5f,
                FMath::Max(Spell.CubeZcm, 1.0f) * 0.5f);

            DrawDebugBox(
                World,
                Placement.SpawnLocation,
                PreviewHalfExtents,
                ShapeRotation,
                EarthGreen,
                false,
                0.0f,
                0,
                2.5f);

            DrawCubeDensityGrid(World, Placement.SpawnLocation, PreviewHalfExtents, ShapeRotation, DensityGridSteps, EarthGreen);
            break;
        }

        case EEarthSpellShape::Cone:
        default:
        {
            const float Height = FMath::Max(Spell.ConeHeightCm, 1.0f);
            const float Radius = FMath::Max(Spell.ConeRadiusCm, 1.0f);
            PreviewHalfExtents = FVector(Radius, Radius, Height * 0.5f);
            DrawConeDensityGrid(World, Placement.SpawnLocation, Radius, Height, ShapeRotation, DensityGridSteps, EarthGreen);
            break;
        }
    }

    // Speed rings are a live-construction indicator, not a generic readout
    // of a stored/default Speed value. If the Speed modifier has not been
    // explicitly activated in this live spell, render exactly zero rings.
    const int32 SpeedRingCount = Session->IsParameterActive(ELiveSpellParameter::Speed)
        ? GetSpeedRingCount(Spell)
        : 0;

    DrawSpeedBands(
        World,
        Placement.SpawnLocation,
        PreviewHalfExtents,
        ShapeRotation,
        SpeedRingCount,
        SpeedGreen);
}
