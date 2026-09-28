# TESTUNREALPROJECT — Architecture V1

Baseline: snapshot commit `58acd09` (`v0.14.2 pre architecture review`)

## Architecture law

**Core routes, Modules execute, Submodules extend.**

Gameplay meaning must not live inside Slate widgets, keyboard handlers, preview
drawing, or Signs.

A feature should plug into the system through explicit data/contracts instead of
requiring edits across unrelated modules.

## Canonical pipeline

```text
DEFINE
  WorldCodex concepts/signs
  FSpellDefinition
        ↓
CONSTRUCT
  Spell Modifier / Live Casting / Rune Graph
        ↓
COMPILE
  SpellGraphCompiler
        ↓
RESOLVE
  SpellCreation normalization
        ↓
EXECUTE
  SpellExecution
        ↓
SIMULATE
  SpellPattern + SpellMotion + elemental realization
        ↓
RESPOND
  PhysicalBody / MaterialCore / ImpactSystem
        ↓
VISUALIZE
  SpellPreview / InnerRealm presentation
```

## Ownership

### WorldCodex
Owns canonical concept vocabulary: stable Concept IDs, Signs, Tier I/II/III,
capabilities, relationships, implementation state and developer documentation.
It does not execute gameplay.

### SpellCreation
Owns canonical `FSpellDefinition` and normalization/resolution into
`FResolvedSpell`.

`FEarthSpellDefinition` is compatibility data only and should gradually stop
being used by new UI.

### SpellGraph
Owns semantic Rune Graph storage and structural validation.

A graph node stores meaning, not screen position:

- NodeId
- ConceptId
- ParentNodeId
- Order

### SpellGraphCompiler
Owns semantic graph -> `FSpellDefinition` interpretation.

This is separated from graph storage so future Fire/Water/Air compilers or
`FSpellProgram` compilation do not turn the graph subsystem into one giant
class.

### SpellLoadout
Owns prepared spell slots. The UI does not own slot data.

### LiveSpellCasting
Owns transient combat construction and prepared-spell loading.

### SpellPattern
Owns instance placement and per-instance facing.

### SpellMotion
Owns per-instance travel direction.

**Orientation and movement are separate concepts.**

### SpellExecution
Owns the final execution boundary:

```text
resolved definition
→ cast placement
→ pattern instances
→ motion direction
→ elemental realization
```

### EarthMagic
Owns Earth-specific realization only.

Future elements should expose their own capabilities and realization rules
instead of being forced through Earth's solid-body model.

## Presentation boundary

### InnerRealm
Long-term responsibility:

- enter/exit meditation realm
- freeze/restore player
- switch camera
- host page/shell presentation

It should not become the implementation home for every UI page.

### InnerRealm Shell
Shared controls that must work regardless of active page:

- page navigation
- prepared spell slots

This prevents page Z-order from breaking shared controls.

### Future page components

The next cleanup steps should extract:

- `SpellWorkbenchUI`
- `CodexUI`
- `RuneCanvasUI`

from `InnerRealmSubsystem.cpp`.

## Allowed dependency direction

```text
WorldCodex
    ↑
SpellGraph
    ↑
SpellGraphCompiler

SpellCreation
    ↑
SpellLoadout
    ↑
LiveSpellCasting
    ↑
SpellExecution

SpellCreation
    ↑
SpellPattern

SpellCreation
    ↑
SpellMotion

Presentation observes/calls gameplay modules.
Gameplay modules must never depend on presentation widgets.
```

## Migration sequence

### Phase 1 — shared shell + compiler boundary
- move ready slots out of Preview UI
- keep them above every InnerRealm page
- extract graph compiler from graph storage

### Phase 2 — generic Workbench — COMPLETE
- Spell Modifier reads/writes `FSpellDefinition` directly
- SpellCreation owns only one stored spell value: `FSpellDefinition`
- `FEarthSpellDefinition` remains only as a compatibility projection/adapter
- no new presentation code may depend on the legacy Earth spell struct

### Phase 3 — presentation split — IN PROGRESS
- `InnerRealmSubsystem.cpp` now contains realm lifecycle/orchestration rather than page implementation
- Spell Workbench helpers moved to `UI/SpellWorkbenchUI.cpp`
- Codex presentation helpers moved to `UI/CodexUI.cpp`
- Rune Canvas rendering/layout moved to `UI/RuneCanvasUI.cpp`
- shared page construction moved to `UI/InnerRealmPageHost.cpp`
- next step: replace the remaining same-class page methods with dedicated page objects/state models

### Phase 4 — compiler registration
- replace growing hard-coded ConceptId chains with explicit compiler handlers
- Codex remains vocabulary; compiler handlers remain behavior

### Phase 5 — Spell Program
Only after the previous boundaries are stable:

```text
FSpellProgram
├── Block 1 : graph/definition
├── Block 2 : graph/definition
└── relationships / anchors / logic
```

A simple spell is a one-block program.

## Non-negotiable rules

1. Sign art never contains gameplay logic.
2. UI position never defines spell meaning.
3. `FSpellDefinition` is the canonical single-spell representation.
4. Pattern facing does not implicitly decide movement.
5. Future element capabilities are explicit; Earth geometry is not universal.
6. Ready slots store data, not widgets.
7. Preview observes spell state; it does not own spell state.
8. No new feature should add another duplicate spell representation.


## Current cleanup status

### v0.15.0
- shared InnerRealm shell
- shared ready-spell bar
- preview made display-only
- graph compiler extracted from graph storage

### v0.15.1
- Spell Modifier migrated to canonical `FSpellDefinition`
- synchronized `StoredSpell` legacy shadow removed from SpellCreation
- legacy Earth definition retained only for compatibility callers


### v0.15.2
- presentation implementation physically separated from realm lifecycle
- no gameplay behavior or spell semantics changed
- Rune Canvas layout is now isolated in its own source file
- Workbench and Codex presentation helpers are isolated for the next page-object migration


### v0.15.3
- Rune Canvas branch creation is manual and one-shot
- a line exists only after the source Sign is double-clicked
- filling a line consumes that pending branch; another line requires another double-click
- Canvas Sign palette is category-first
- categories are UI navigation only, never semantic spell graph nodes
- Shape Parameters are filtered to the active Shape (for example Cube -> X/Y/Z)
