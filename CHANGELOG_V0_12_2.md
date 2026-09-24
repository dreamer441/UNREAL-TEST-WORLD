# AMADEUS Gameplay v0.12.2 — Density Grid + Speed Rings

Small presentation-only patch for live spell construction.

## Density

The ghost construction grid now reflects the resolved density value:

- minimum density -> sparse grid (about 4 steps)
- middle density -> medium grid
- maximum density -> dense grid (up to 15 steps)

This works on sphere, cube, and cone previews. It does not alter physics or the actual density calculation.

## Speed

The preview now shows speed bands around the constructed shape:

- 0 speed -> no bands
- low speed -> 1 band on each Y/Z-oriented ring family
- medium speed -> 2 bands
- high speed -> 3 bands

Speed bands are intentionally a visual language only. Actual speed remains owned by the live spell definition and EarthMagic execution.

## Architecture

Only `SpellPreview` changed. No changes to LiveSpellCasting state, EarthMagic, ImpactSystem, SpellCreation, movement, or the casting hierarchy.
