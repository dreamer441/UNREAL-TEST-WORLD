# AMADEUS Gameplay v0.14.0
## Rune Canvas V1 / Semantic Spell Graph

Requires working **v0.13.5 Codex Grammar + Motion Direction**.

### What this patch does

The reserved TAB Canvas page becomes the first usable Rune Canvas.

Top navigation remains one clean space:

`SPELL MODIFIER | CODEX | RUNE CANVAS`

The Canvas uses the canonical signs from `WorldCodex`.

For V1, interaction is deliberately **click-to-place** rather than physical
drag/drop:

1. click a graph node to select it;
2. click a Sign in the Codex palette;
3. the Sign is attached beneath the selected semantic node.

This is easier to validate and debug while preserving the important part:
the graph data is completely independent from its UI position. A later freeform
drag/drop canvas can therefore replace the interaction without replacing saved
spell meaning.

### Semantic graph

New module:

`SpellGraph`

Each node stores:

- Node ID
- canonical Codex Concept ID
- Parent Node ID
- stable insertion order

The graph does not store button names or UI widgets as spell meaning.

### Tier grammar is enforced

- Tier I: root/foundation
- Tier II: operator/modifier/reference
- Tier III: terminal/value

V1 allows one Tier-I root. This deliberately postpones stacking until the graph
compiler is proven.

### Capability validation

The Canvas asks WorldCodex whether an attached concept's required capabilities
are present along its branch.

Example:

`Earth -> Sphere`

works because Earth provides bounded-solid geometry.

A shape parameter such as Sphere Radius only becomes meaningful on a branch
that already contains Sphere.

### Terminal/value validation

V1 also validates terminal families:

- Magnitude 0..5 -> numeric modifiers
- Direction values -> Motion Direction
- Orientation Forward/Right/Up -> Orientation
- Axis Forward/Right/Up -> Line Axis
- Shared/Outward/Inward/Tangent -> Instance Orientation

Selecting a new terminal beneath the same operator replaces the old terminal.

### Compiler

A valid Rune Graph compiles into the existing:

`FSpellDefinition`

So the new path is:

`Codex Signs -> Semantic Graph -> Spell Compiler -> FSpellDefinition`

and then the existing pipeline continues:

`Resolve -> Pattern -> Motion -> Execution -> Physics`

No second spell engine is introduced.

### V1 compiled concepts

- Earth
- Sphere / Cube / Cone
- shape dimensions
- Density / Hardness / Toughness / Elasticity
- Distance
- Orientation
- Amount
- Line / Circle
- Line Axis
- Spacing
- Circle Radius
- Instance Orientation
- Speed
- Motion Direction
- Magnitude 0..5

### Magnitude mapping

Magnitude signs are normalized language, not literal physical units.

For numeric range `[min, max]`:

`physical value = lerp(min, max, magnitude / 5)`

Examples:

- Speed 0 -> minimum speed (currently 0)
- Speed 5 -> maximum current speed
- Density 0 -> minimum valid Earth density
- Amount 0 -> one instance / no multiplicity
- Amount 5 -> current maximum instance count

### Preview + old Workbench

When a Rune Graph becomes valid, the compiler writes through the canonical
SpellCreation subsystem.

Therefore:

- the existing 3D spell preview updates;
- switching back to SPELL MODIFIER shows the compiled values;
- the old editor is not discarded;
- ready-spell and execution foundations keep using the same spell definition.

### Extra Codex terminals added

For Canvas completeness:

- Face Forward / Face Right / Face Up
- Axis Forward / Axis Right / Axis Up

These are Tier III signs.

### V1 scope limits

Not yet:

- multiple Tier-I roots / stacking
- FSpellProgram
- block anchoring
- IF / WHEN / WHILE execution
- world-reference execution
- hand-drawn rune recognition
- free-position drag/drop
- player discovery filtering

The graph model was designed so those features can extend it rather than replace
it.
