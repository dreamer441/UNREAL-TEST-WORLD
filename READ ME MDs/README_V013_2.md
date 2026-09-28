# AMADEUS Gameplay v0.13.2
## Multiplicity + Pattern Resolver + Modifier Contract Foundation

Requires the working **v0.13.1.1 Ready Slots + Orientation** patch.

### Adds

- Amount, default `1`
- Arrangement: `Line` / `Circle`
- Line axis: `Forward` / `Right` / `Up`
- Line spacing
- Circle radius
- immediate multi-object Workbench preview
- actual multi-object spell realization
- ready-spell slots automatically preserve the complete pattern
- generic `SpellPattern` resolver module
- `SpellModifierContract` foundation for future default-value + optional-key behavior

### Architecture

`FResolvedSpell`
→ `SpellPattern`
→ world-space instance locations
→ `SpellExecution`
→ Earth realization

`SpellPattern` contains no Earth-specific logic.

### Defaults / future live keys

Every new pattern property is stored persistently in the spell definition.

`SpellModifierContract` now provides stable semantic IDs and marks authored
modifiers as supporting an optional live binding. This patch does not yet add
key boxes for Orientation / Amount / Arrangement / Pattern Axis / Spacing /
Circle Radius; it makes the architecture ready for that later binding pass.

### V1 rule

All objects share the spell's current Orientation.

Deferred:
- outward / inward / tangent instance orientation
- random cluster
- grid arrangement
- per-instance rotation
- live key binding UI for the new modifiers

### Install

Extract into `D:\TESTUNREALPROJECT\` and run:

`APPLY_BUILD_AND_OPEN_V013_2.bat`
