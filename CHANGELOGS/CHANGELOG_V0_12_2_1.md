# AMADEUS Gameplay v0.12.2.1 — Speed Ring Zero Fix

Tiny presentation-only fix.

- speed = 0 -> 0 rings
- low speed -> 1 ring
- medium speed -> 2 rings
- high speed -> 3 rings

Adds a tiny zero-speed dead-zone so floating-point/slider residue cannot display one ring at nominal zero.

Only `SpellPreviewSubsystem.cpp` changed.
