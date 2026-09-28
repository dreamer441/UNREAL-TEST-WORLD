# AMADEUS Gameplay v0.13.1.0 — Ready Spell Slots + Orientation

Base target:
- repository branch: `codex/unreal-architecture-cleanup`
- assumes the current Workbench/preview patch is already present and working
- intended follow-up to the current `v0.13.0.3` state

## What this patch adds

### A. Ready-to-cast spell slots
- Adds **10 slot buttons** to the right-side Workbench preview panel:
  `1 2 3 4 5 6 7 8 9 0`
- Clicking a slot in TAB/Workbench:
  - saves the **current stored spell** into that slot
  - equips that slot immediately
- In gameplay:
  - pressing **1–0** loads the slot into the live construction session
  - then **SPACE** casts it through the existing live-casting path
- This keeps a clean modular boundary:
  - `SpellCreation` = persistent editor spell
  - `SpellLoadout` = prepared spell slots
  - `LiveSpellCasting` = transient active construction

### B. Orientation foundation
- Adds a new stored spell property:
  - `Forward / X`
  - `Right / Y`
  - `Up / Z`
- Adds an **ORIENTATION** section in TAB / Workbench.
- The preview uses that orientation so shapes can read differently:
  - `Up / Z` = spike / pillar style
  - `Forward / X` = projectile style
  - `Right / Y` = sideways lateral style

## Important note

This patch is designed as a **current-branch follow-up patch**.
It uses PowerShell source edits instead of dropping giant replacement files, because your local branch is ahead of the old GitHub baseline.

## Install

1. Close Unreal Editor.
2. Extract this ZIP into `D:\TESTUNREALPROJECT\`.
3. Run:

`APPLY_BUILD_AND_OPEN_V013_1_0.bat`

## First test

1. Enter Play.
2. Press `TAB`.
3. On the right preview frame, click one of the slot buttons (`1..0`).
   - it should save the current workbench spell into that slot.
4. Exit TAB.
5. In top-down gameplay, press that number key.
   - the live preview should appear from the loaded prepared spell.
6. Press `SPACE`.
   - the spell should cast normally through the existing live-casting route.
7. Re-enter TAB and change **Orientation**.
8. Check the preview rotates accordingly.

If compilation fails, send the newest:
- `%LOCALAPPDATA%\UnrealBuildTool\Log.txt`
