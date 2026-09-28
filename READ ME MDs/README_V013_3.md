# AMADEUS Gameplay v0.13.3
## Pattern Orientation / Resolved Instance Transforms

Requires the working **v0.13.2.1** project.

### New modes

- Shared
- Outward
- Inward
- Tangent

Default is **Shared**, preserving the current behavior.

### Architecture

`SpellPattern` now resolves `FResolvedPatternInstance[]` instead of only a list
of positions.

Each instance contains:

- world-space Location
- PatternRotation delta

The final shape rotation is:

`FinalRotation = PatternRotation * BaseSpellRotation`

This keeps two layers separate:

1. Spell Orientation — Forward / Right / Up
2. Pattern Orientation — Shared / Outward / Inward / Tangent

### Circle

- Shared: all copies keep the same frame
- Outward: each faces away from the center
- Inward: each faces toward the center
- Tangent: each follows the circumference

### Line

- Shared: all copies keep the same frame
- Outward: copies face away from line center
- Inward: copies face toward line center
- Tangent: copies face along the chosen line axis

### Important separation

Pattern Orientation changes **facing only**.

Projectile velocity still follows the normal spell execution direction.

A later Pattern Motion patch can independently add Shared / Outward / Inward /
Tangent movement without overloading Orientation.

### Workbench

When Amount > 1, a new section appears:

`INSTANCE ORIENTATION`

with:

`Shared | Outward | Inward | Tangent`

### Ready spells

No special ready-slot rewrite is needed because SpellLoadout already stores the
full `FSpellDefinition`.

### Modifier contract

`PatternOrientation` is registered as a normal modifier:

- persistent default: yes
- optional live binding supported: yes
- value kind: Choice

No key box is added yet; that belongs to Universal Modifier Bindings.

### Best visual test

Use:

- Earth
- Cone
- Spell Orientation = Forward / X
- Amount = 8
- Circle

Then switch Shared → Outward → Inward → Tangent.

With an axially symmetric cone using Orientation = Up, horizontal pattern yaw
can look visually unchanged. That is expected composition behavior.
