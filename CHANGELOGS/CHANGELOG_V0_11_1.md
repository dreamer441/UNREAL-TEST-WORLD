# Gameplay v0.11.1 — editor + live casting feel patch

This patch keeps the v0.11 live-casting architecture and restores the precise meditation editor.

## Meditation realm
- Restored manual sliders for active shape dimensions, speed, density, hardness, toughness, elasticity and distance.
- Restored direct Sphere / Cube / Cone buttons.
- Added live-casting key selectors beside the same options instead of replacing the editor with a key-only screen.
- The live `Size` binding is intentionally shared by the active shape's dimension rows. Manual sliders may still create non-uniform cube/cone proportions; holding the Size key scales the live form as one combat gesture.
- Mass remains derived from density × volume; there is no contradictory manual mass slider.

## Hold scaling
- Full charge remains 3 seconds.
- Hold response now uses a quadratic curve: 1 s ≈ 11%, 2 s ≈ 44%, 3 s = 100% of the configured range.
- Size ranges are much wider (sphere radius up to 300 cm, cube side up to 600 cm, cone radius up to 300 cm / height up to 800 cm).
- Speed range is now 0–180 m/s.
- Density range is now 500–4500 kg/m³.
- Distance range is now 1–25 m.
- Shared tuning lives in `LiveSpellTuning.h` so the live input node and meditation sliders use the same values.

## Top-down camera
- Orbit distance: 1680 cm -> 2200 cm.
- Horizontal drag sensitivity: 0.85 -> 1.25 deg/pixel.
- Vertical drag sensitivity: 0.50 -> 0.75 deg/pixel.

No Earth collision/deformation, impact solver, or spell spawning logic was changed.
