#pragma once

#include "CoreMinimal.h"

/** Shared authored ranges for both TAB defaults and temporary live overrides. */
namespace LiveSpellRanges
{
    constexpr float MinSphereRadiusCm = 10.0f;
    constexpr float MaxSphereRadiusCm = 300.0f;
    constexpr float MinCubeSideCm = 20.0f;
    constexpr float MaxCubeSideCm = 600.0f;
    constexpr float MinConeRadiusCm = 10.0f;
    constexpr float MaxConeRadiusCm = 300.0f;
    constexpr float MinConeHeightCm = 30.0f;
    constexpr float MaxConeHeightCm = 800.0f;

    constexpr float MinSpeedMps = 0.0f;
    constexpr float MaxSpeedMps = 180.0f;
    constexpr float MinDensityKgPerM3 = 500.0f;
    constexpr float MaxDensityKgPerM3 = 4500.0f;
    constexpr float MinDistanceM = 0.0f;
    constexpr float MaxDistanceM = 25.0f;

    inline float Normalize(const float Value, const float Min, const float Max)
    {
        return FMath::Clamp((Value - Min) / FMath::Max(Max - Min, KINDA_SMALL_NUMBER), 0.0f, 1.0f);
    }

    inline float Denormalize(const float Normalized, const float Min, const float Max)
    {
        return FMath::Lerp(Min, Max, FMath::Clamp(Normalized, 0.0f, 1.0f));
    }
}
