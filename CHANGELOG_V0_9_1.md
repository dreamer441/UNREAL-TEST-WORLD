# Gameplay v0.9.1 — Orbit sensitivity, scrolling sprint, Space casting

**Patch against:** AMADEUS Gameplay v0.9 (including v0.8.2 Earth collisions). Extract into `D:\TESTUNREALPROJECT\` and replace only the included plugin source files. No material, Earth, world, shape or collision logic changed.

## Controls

- **Shift:** switch third person / top down, unchanged.
- **TAB:** Inner Realm, unchanged.
- **Top down LMB drag:** orbit sensitivity increased ~2.5x horizontally and vertically. Adjust `OrbitYawDegreesPerMousePixel` / `OrbitPitchDegreesPerMousePixel` in `PlayerViewModeSubsystem.cpp` as needed.
- **Top down RMB:** hold to move, unchanged.
- **Top down RMB + repeated upward wheel movement:** sprint during active scrolling; each wheel pulse refreshes a 0.45-second sprint window. Releasing RMB, rolling downward, meditating, or stopping scroll pulses causes return to walk speed automatically. A physical wheel emits pulses, not a holdable up key; a short grace window approximates continuous scrolling without sticky sprint.
- **Space:** create/cast stored Earth spell in **both** outer-world views; **E** no longer casts.
- **Space jump:** normal `ACharacter` template jump disabled at runtime by setting `JumpMaxCount=0` on the possessed character; original count restored when subsystem is destroyed or pawn changes. This does not edit your Third Person Blueprint or mapping context. If you later introduce a custom jump implementation that ignores `JumpMaxCount`, remove that Blueprint Jump binding separately.

## Ownership and unchanged architecture

- `PlayerViewModes`: orbit sensitivity, scroll sprint, template jump suppression, camera modes.
- `EarthTestHarness`: Space casting input only.
- `InnerRealm`: editor's on-screen key hint only.
- `SpellCreation / EarthMagic / EarthFoundation / ImpactSystem`: unchanged.

## Manual test checklist (requires Unreal 5.8 on user's PC)

1. After a successful rebuild, enter Play in third person: **Space** casts an Earth form, does not jump, **E** does nothing.
2. Press Shift into top-down: RMB moves, LMB orbit moves faster, **Space** casts toward the cursor without jumping.
3. Hold RMB and repeatedly scroll up: sprint persists while scrolling; stop scrolling and observe walk speed return after about 0.45 seconds, without scrolling down.
4. Press TAB, then TAB again: sprint does not stick; previous outer-world camera mode returns.

Compilation against the user's Unreal installation is still required; this patch has been checked structurally but not compiled in this environment.
