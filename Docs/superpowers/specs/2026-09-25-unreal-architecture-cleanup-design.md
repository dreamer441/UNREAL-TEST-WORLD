# Unreal Architecture Cleanup and Consolidation Design

**Status:** Approved architecture direction; implementation specification review pending

**Project:** `D:\TESTUNREALPROJECT\TESTUNREALPROJECT.uproject`
**Engine:** Unreal Engine 5.8 at `D:\UE_5.8`
**Baseline:** Git commit `ecbeb5c` (`chore: capture pre-cleanup Unreal baseline`)

## Goal

Consolidate the working Gameplay v0.12.2.2 prototype into a small set of explicit, replaceable runtime nodes without changing its current Earth-magic, casting, preview, movement, or Inner Realm behavior.

The finished system must make a future element or shape an additive change: add data and a focused executor/realizer rather than editing player movement, editor UI, impact physics, and preview code together.

## Non-goals

- Do not add Water, Fire, Air, new spell shapes, or new gameplay rules.
- Do not change the live-casting grammar, values, input feel, material equations, collision behavior, or visual language.
- Do not replace working systems with a framework, service locator, factory hierarchy, or generic interface that has no current purpose.
- Do not commit generated Unreal build products, local runtime data, editor state, build logs, ZIP archives, or credentials.

## Audit Summary

The project currently contains twelve runtime plugins:

| Area | Current module(s) | Audit result |
| --- | --- | --- |
| Generic material and physical data | `MaterialCore`, `PhysicalBody`, `ImpactSystem` | Already well separated and retained. |
| Earth world response | `EarthFoundation` | Retained as the Earth-specific material/geometry adapter. |
| Earth spell body | `EarthMagic` | Retained; consumes a resolved spell instead of raw editor data. |
| Persistent spell defaults | `SpellCreation` | Retained; becomes the owner of generic spell contracts and derived resolution data. |
| Transient construction state | `LiveSpellCasting` | Retained; remains the explicit stage machine. |
| Keyboard configuration and holds | `SpellCastingBindings` | Retained; remains input semantics only. |
| Preview | `SpellPreview` | Retained as a read-only observer. |
| Meditation/editor | `InnerRealm` | Retained as presentation, camera transition, freeze state, and editor UI. |
| View/movement | `PlayerViewModes` | Retained as third-person/top-down presentation and movement. |
| Production cast invocation | `EarthTestHarness` | Misplaced: it currently owns the live SPACE path. Its runtime behavior moves to `SpellExecution`; the harness plugin is then removed. |

The plugin dependency graph does not currently contain a build-time cycle, but it has two weak boundaries:

1. `EarthTestHarness` is named and categorized as testing infrastructure but contains the shipping SPACE-cast path.
2. Spell data is Earth-named and duplicates generic material/body fields, which makes future elements and shapes unnecessarily expensive.

The root also contains versioned rebuild scripts, old patch scripts, root-level historical documents, stale build logs, ZIP archives, and small orphaned note files. They are not active runtime dependencies.

## Chosen Architecture

### Runtime node graph

```text
                         +--------------------+
                         | PlayerViewModes    |
                         | view + movement +  |
                         | top-down aim       |
                         +----------+---------+
                                    |
        +---------------------------+--------------------------+
        |                           |                          |
        v                           v                          v
+---------------+          +---------------------+   +-------------------+
| InnerRealm    |          | SpellCastingBindings|   | SpellPreview      |
| TAB/editor    |          | key mapping + holds  |   | read-only display |
+-------+-------+          +----------+----------+   +---------+---------+
        |                             |                        |
        |                             v                        |
        |                  +---------------------+             |
        +----------------->| LiveSpellCasting    |<------------+
                           | explicit live state |
                           +----------+----------+
                                      |
                                      v
                           +---------------------+
                           | SpellCreation       |
                           | defaults + contracts|
                           +----------+----------+
                                      |
                                      v
                           +---------------------+
                           | SpellExecution      |
                           | target + dispatch   |
                           +----------+----------+
                                      |
                                      v
                           +---------------------+
                           | EarthMagic          |
                           | physical Earth body |
                           +----------+----------+
                                      |
       +------------------------------+------------------------------+
       |                              |                              |
       v                              v                              v
+---------------+             +---------------+             +----------------+
| EarthFoundation|             | ImpactSystem  |             | PhysicalBody   |
| Earth geometry |             | pure impact   |             | body state     |
+-------+--------+             +-------+-------+             +-------+--------+
        |                              |                             |
        +------------------------------+-----------------------------+
                                       v
                              +----------------+
                              | MaterialCore   |
                              | material data  |
                              +----------------+
```

The arrows indicate allowed knowledge and data flow, not ownership. Higher-level input and presentation nodes may request work from gameplay state. Lower-level material, body, impact, and Earth nodes never inspect UI, keyboard, or camera state.

### Dependency direction

The intended build dependencies after cleanup are:

```text
MaterialCore
└── PhysicalBody
    └── ImpactSystem
        └── EarthFoundation

MaterialCore + PhysicalBody
└── SpellCreation
    └── LiveSpellCasting
        ├── SpellCastingBindings
        ├── SpellPreview
        └── SpellExecution
            └── EarthMagic
                └── EarthFoundation + ImpactSystem

PlayerViewModes ──> SpellPreview, SpellExecution
SpellCastingBindings ──> PlayerViewModes
InnerRealm ───────> PlayerViewModes, SpellCreation, LiveSpellCasting,
                     SpellCastingBindings, SpellExecution
```

`PlayerViewModes` will expose a narrow public outer-world-input suspension API. `InnerRealm` calls it on TAB entry and exit, so `PlayerViewModes` no longer reads `InnerRealm` directly. It will also no longer call into `SpellCastingBindings`; bindings will observe the public view-mode state instead. This removes magic-input knowledge from the player camera/movement node without creating a circular build dependency.

`InnerRealm` may suspend live input and execution while its editor is open, but it never resolves or executes a spell. `SpellExecution` must not read UI state directly.

## Public Data Contracts

The cleanup creates small public structures under `SpellCreation` and uses them across the spell pipeline:

| Contract | Owner | Meaning |
| --- | --- | --- |
| `ESpellElement` | SpellCreation | Current value is `Earth`; the enum is intentionally extensible. |
| `ESpellShape` | SpellCreation | Current values are `Sphere`, `Cube`, and `Cone`; shape identity is independent of an element executor. |
| `FSpellShapeDefinition` | SpellCreation | Shape identity plus the currently supported radius/XYZ/height values. Values not used by the selected shape remain data, not branching logic elsewhere. |
| `FSpellDefinition` | SpellCreation | Persistent TAB defaults: element, shape definition, material definition, distance, and authored speed. |
| `FLiveSpellState` | LiveSpellCasting | Temporary stage, explicit element/shape selections, active modifiers, and generation/reset information. |
| `FResolvedSpell` | LiveSpellCasting | Persistent defaults plus accepted live overrides, with a derived `FPhysicalBodyState`. A new live spell forces speed to zero until Speed is active. |
| `FSpellCastTarget` / `FResolvedSpellCastPlacement` | SpellExecution | Separates camera-derived aim from character-relative spawn origin and rotation. |
| `FSpellExecutionResult` | SpellExecution | Structured success/failure result for a cast request. |
| `FImpactRequest` / `FImpactResult` | ImpactSystem | Existing generic material/body impact contracts; retained without UI or spell knowledge. |

`FMaterialPhysicalProperties` remains the single material representation. `FResolvedSpell` derives `FPhysicalBodyState` from the selected shape volume and material density, so mass, volume, density, contact radius, gravity state, and velocity no longer have competing owners.

`FEarthSpellDefinition` and `EEarthSpellShape` will be replaced in source by the generic contracts. Unreal Core Redirects will preserve loading of serialized project assets that reference the old struct or enum names. The old header paths will be removed only after all active source includes have migrated and a clean editor build has confirmed the redirects.

## Spell Flow and Behavior Preservation

```text
TAB defaults (FSpellDefinition)
          +
live choices (FLiveSpellState)
          |
          v
LiveSpellCasting resolves FResolvedSpell
          |
          +--> SpellPreview reads it; never changes it
          |
          v
SpellExecution resolves character origin + view aim
          |
          v
EarthMagic realizes AEarthSpellBody
          |
          v
PhysicalBody / MaterialCore state
          |
          v
ImpactSystem computes FImpactResult
          |
          v
EarthFoundation applies Earth geometry response
```

The following behavior is invariant through the migration:

- Live construction remains `Empty → ElementSelected → ShapeSelected → ModifierActive → Cast → Reset`.
- Shape and modifier input before valid earlier stages remains inert.
- A valid cast still requires Element, Shape, and at least one Modifier.
- TAB defaults persist through live casts; a cast only resets live state.
- Speed begins at exactly zero for each new live construction, and no Speed modifier means zero preview rings.
- Earth aura, ghost shape, density grid, shape size updates, and one/two/three speed-ring thresholds retain their current behavior.
- The spawn point remains character-relative with shape clearance; aim can remain camera/top-down-ray-derived.
- Earth bodies retain gravity, pawn/body collision, Earth-to-Earth collision, deformation, source damage, and material propagation.

## Element and Shape Extension Points

`SpellExecution` will contain one explicit, small element dispatch point. In the current release, the only branch calls `EarthMagic` for `ESpellElement::Earth`. A future Water/Fire/Air implementation adds its own focused runtime module and one dispatch branch; it does not alter `LiveSpellCasting`, `SpellPreview`, `PlayerViewModes`, `ImpactSystem`, or `InnerRealm`.

Shape math is centralized in `FSpellShapeMath`. `EarthMagic` owns the Earth-specific realization mapping from generic `ESpellShape` data to a physical mesh and editable damage mesh. New shapes add a definition branch and an Earth realization branch, not changes throughout input, UI, impact, or placement code.

No runtime registry, service locator, or factory framework will be introduced. The current one-element system does not justify one.

## Module-Specific Responsibilities

| Module | Public responsibility after cleanup | Explicit exclusions |
| --- | --- | --- |
| MaterialCore | `FMaterialPhysicalProperties` only | Input, actors, Earth geometry, UI, preview. |
| PhysicalBody | `FPhysicalBodyState` and pure mass/density helpers | Spell rules, collision response, Earth behavior. |
| ImpactSystem | Pure request-to-result contact, energy, target, source, and motion calculation | Actor movement, mesh edits, controls. |
| EarthFoundation | Earth material adapter, static Earth geometry, and applying an `FImpactResult` to Earth meshes | Input, casting, camera. |
| SpellCreation | Persistent defaults, generic spell structures, normalization, shape/body derivation | UI widgets, key polling, spawning. |
| LiveSpellCasting | Explicit temporary construction stage and resolver | UI, key mapping, spawning, preview rendering. |
| SpellCastingBindings | Rebind/unbind policy and hold-to-value input interpretation | Earth physics, actor spawning, UI layout. |
| SpellExecution | Fixed cast request, targeting/placement, element dispatch, execution result | Editing persistent defaults, input rebinding, impact equations. |
| EarthMagic | Realize `FResolvedSpell` as an Earth body and apply Earth-body collision outcomes | TAB, SHIFT, input timing, preview ownership. |
| SpellPreview | Visualize accepted live state and shared cast placement | Mutating live state or physical data. |
| InnerRealm | TAB state, freeze/restore, fixed realm camera, slate editor | Physics, spawn logic, material equations. |
| PlayerViewModes | Third-person/top-down transitions, cursor movement, orbit, sprint, cast aim | Spell value logic, preview, material/impact work. |

## Migration Sequence

1. Add generic spell contracts and pure shape/body helpers, then redirect old serialized names.
2. Convert `SpellCreation`, `LiveSpellCasting`, bindings, preview, and EarthMagic to the contracts while preserving every current numeric range and default.
3. Add `SpellExecution`, move the production SPACE path from `EarthTestHarness`, and expose a structured execution result.
4. Invert the `PlayerViewModes → InnerRealm` and `PlayerViewModes → SpellCastingBindings` relationships: InnerRealm requests outer-input suspension from the player-view node, while bindings observe the public top-down state.
5. Enable every active runtime plugin explicitly in the `.uproject`; remove `EarthTestHarness` only after references and a clean build confirm it is unused.
6. Add focused Unreal Automation tests for pure spell resolution, stage gating, speed zero-state, placement, and impact contracts.
7. Replace versioned scripts with one `AMADEUS_DEV.bat`; archive historical docs; delete obsolete scripts, logs, ZIPs, and orphan notes after reference checks.
8. Produce the five authoritative project documents and a cleanup report based on the actual resulting file changes.
9. Perform a genuine clean UE 5.8 rebuild, launch validation, automated tests, and manual gameplay regression pass.

Each source-changing phase receives a build check before the next phase. The refactor will stop at the first meaningful compiler or linker error, fix that error, and rebuild before continuing.

## Documentation and Tooling Layout

```text
Docs/
  CURRENT_ARCHITECTURE.md
  MODULE_GRAPH.md
  SPELL_SYSTEM.md
  CURRENT_CONTROLS.md
  CLEANUP_REPORT.md
  Archive/
    Architecture/
    Changelog/
    Migration/
  superpowers/
    specs/
    plans/

AMADEUS_DEV.bat
```

`AMADEUS_DEV.bat` will support a menu and named arguments for:

1. Launch project
2. Clean and rebuild project
3. Clean plugin build products
4. Full clean
5. Open the UnrealBuildTool log
6. Collect the UnrealBuildTool log
7. Exit

The rebuild command calls `D:\UE_5.8\Engine\Build\BatchFiles\Build.bat` directly. It never invokes a system `dotnet` executable. Full clean removes generated build/cache products only; it does not delete `Content`, `Config`, source plugins, or user-authored assets.

## Git and Security Rules

- Git is initialized directly in `D:\TESTUNREALPROJECT` with `origin` set to `https://github.com/dreamer441/UNREAL-TEST-WORLD.git`.
- The baseline commit has been pushed before refactoring starts.
- Generated Unreal folders, local logs, ZIP backups, bytecode caches, and IDE state are ignored.
- `Config/DefaultEngine.ini` contains a machine-specific Android File Server credential and remains untracked. `Config/DefaultEngine.template.ini` is the safe versioned template.
- Every cleanup change is committed in focused, reviewable checkpoints and pushed after validation.

## Validation Plan

### Automated and build validation

- Run the new Unreal Automation tests for pure contracts and state transitions.
- Run `AMADEUS_DEV.bat rebuild` from a clean state, which forces UnrealHeaderTool, all plugins, and linker outputs to rebuild with UE 5.8.
- Confirm build output contains no UHT, compiler, linker, module-load, or plugin dependency errors.
- Launch the project with UE 5.8 and confirm the editor opens with all runtime modules available.

### Gameplay regression validation

The implementation report will record an explicit result for each current behavior:

- third-person and SHIFT top-down switching;
- top-down right-click movement, left-drag orbit, vertical orbit, distant camera, and wheel sprint;
- TAB realm entry/exit, frozen terrain-safe player, readable black editor text, binding changes/unbinding/shared compatible bindings;
- Earth selection, three shapes, hierarchy gates, SPACE no-op before a valid spell, reset after cast;
- zero/low/medium/high speed preview rings, density grids, size updates, Earth aura, and character-relative origin;
- gravity/collision for Earth bodies; Earth-to-Earth impact/deformation; material values entering the spawned body.

Where an interaction cannot be asserted by Unreal Automation alone, it will be exercised in the running editor and recorded as a manual verification result rather than inferred from a successful compile.

## Acceptance Criteria

The cleanup is complete only when all of the following are true:

1. The project has one clear public data flow from definition to resolution, execution, simulation, response, and visualization.
2. `EarthTestHarness` no longer contains production runtime behavior and is removed after a reference audit.
3. No active module includes another module's private implementation headers or introduces a circular build dependency.
4. `AMADEUS_DEV.bat` replaces all versioned rebuild, patch, and build-log scripts.
5. Root documentation clutter is archived and the five current documents are authoritative.
6. A clean UE 5.8 rebuild succeeds, the project launches, and the regression checklist has recorded results.
7. Git status is clean apart from intentionally ignored local/generated files, and all approved commits are pushed to `origin/main`.
