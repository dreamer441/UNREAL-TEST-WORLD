# AMADEUS Gameplay v0.15.0
## Architecture Cleanup — Phase 1

Baseline: `58acd09` / `snapshot/v0142-pre-architecture-review`

This patch intentionally avoids adding new spell features. It stabilizes the
architecture before stacking, logic, new elements, and further Rune Canvas work.

### 1. Shared InnerRealm shell

Prepared spell slots are no longer children of the 3D preview panel.

The shared shell now owns:

- `SPELL MODIFIER | CODEX | RUNE CANVAS`
- `[1][2][3][4][5][6][7][8][9][0]` prepared spell slots

This fixes the architectural cause of the recent input bugs: page widgets and
preview overlays no longer decide whether the slot bar can receive mouse input.

The shell is rendered above all page content.

### 2. Preview becomes display-only

The preview root uses `EVisibility::HitTestInvisible` because it no longer owns
interactive controls.

### 3. SpellGraph compiler boundary

Before:

`USpellGraphSubsystem = storage + validation + compilation + apply`

After:

`USpellGraphSubsystem = storage + validation + apply orchestration`

`FSpellGraphCompiler = graph -> FSpellDefinition`

The compiler is still inside the SpellGraph module for now, but its behavioral
responsibility is separated from graph-state ownership.

### 4. Architecture document

`Docs/ARCHITECTURE_V1.md` records:

- module ownership
- dependency direction
- canonical pipeline
- presentation boundary
- migration sequence
- non-negotiable architecture rules

### What this patch deliberately does NOT do yet

- no new Canvas behavior
- no stacking
- no IF / WHEN / WHILE execution
- no Fire / Water / Air
- no removal of `FEarthSpellDefinition` yet
- no full split of Workbench/Codex/Canvas UI yet

Those are later cleanup phases after this stabilization patch is verified.
