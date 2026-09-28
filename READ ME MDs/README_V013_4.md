# AMADEUS Gameplay v0.13.4
## World Codex + Sign Vocabulary + TAB Navigation

Requires the working **v0.13.3 Pattern Orientation** project.

### New WorldCodex module

The Codex is the canonical dictionary of world concepts. Each entry has:

- permanent Concept ID
- display name
- description
- category
- temporary Sign / glyph
- provided capabilities
- required capabilities
- relationships
- implementation status
- owning system
- developer notes

The Sign is presentation metadata only. It contains no physics or spell logic.

### Earth is capability-based

Earth currently provides solid-matter capabilities such as:

- bounded solid geometry
- solid material properties
- rigid-body physics
- placement / orientation / movement
- instance patterns

Shapes such as Sphere/Cube/Cone require bounded-solid geometry.

This deliberately does **not** make Shape a universal Element rule. Future Water,
Air and Fire entries can expose fundamentally different capabilities and therefore
accept different rune vocabularies.

### Initial Codex vocabulary

The browser includes current implemented concepts such as:

- Earth
- Sphere / Cube / Cone and their dimensions
- Density / Hardness / Toughness / Elasticity
- Distance / Orientation / Direction
- Amount / Line / Circle / Axis / Spacing / Circle Radius
- Shared / Outward / Inward / Tangent instance orientation
- Speed
- Create / Launch
- Mass / Gravity / Collision / Momentum

It also seeds future world-language concepts:

- Person
- Ground
- In Air
- Impact
- When / If / Repeat / While

Those future concepts are clearly marked Codex Only or Planned; they are not
silently treated as implemented spell behavior.

### TAB navigation

The Meditation Realm now has persistent top navigation:

`SPELL MODIFIER | CODEX | CANVAS / LATER`

- **SPELL MODIFIER**: the existing Workbench/editor and 3D preview
- **CODEX**: developer Codex browser in the same clean space
- **CANVAS / LATER**: reserved placeholder for v0.14 Rune Canvas

The 3D spell preview is hidden while Codex or Canvas is selected.

### Rune Canvas preparation

`UWorldCodexSubsystem` already exposes capability validation helpers so the
future semantic graph can accumulate capabilities from connected Signs and ask
whether another Sign's requirements are satisfied without hardcoding Earth rules
into the Canvas.

### Explicitly not in this patch

- no Rune Canvas graph yet
- no Sign drawing recognition
- no stacking/program execution
- no IF/WHEN/WHILE execution
- no player discovery/knowledge filtering
- no Fire/Water/Air implementation
- no changes to existing spell execution or Earth physics
