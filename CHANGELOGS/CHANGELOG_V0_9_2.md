# AMADEUS Gameplay v0.9.2 — view recovery and smoother orbit

**Install over:** v0.9.1 Controls Patch (which itself installs over v0.9 / v0.8.2).
Only `PlayerViewModes` files change; no InnerRealm, SpellCreation, Earth, Impact or casting code changes.

## Fix: WASD after TAB while using top-down
Unreal Engine's `AController::SetIgnoreMoveInput()` and `SetIgnoreLookInput()` are **stacked** operations.

Previously, entering top-down acquired one input lock; entering TAB acquired an independent InnerRealm lock; leaving TAB released the InnerRealm lock but `ReapplyTopDownInput()` incorrectly acquired another top-down lock. Shift then released just one, leaving WASD/looking permanently ignored during that Play session.

Now, `PlayerViewModes` owns exactly one top-down pair of input locks, tracks the controller on which they were applied, and never duplicates them when restoring the mouse/camera after TAB. `ExitTopDown` releases that one owned pair; the InnerRealm's separate lock acquisition/release is left unchanged.

Normal successful sequence: `top-down +1` -> `TAB +1` -> `TAB exit -1` -> `top-down resume +0` -> `Shift exit -1` -> zero locks.

## Orbit feel and camera distance
- Spring-arm length **1350 cm -> 1680 cm** (roughly 24% farther).
- Camera follow lag eased (**12 -> 9**) for smoother character tracking.
- Spring-arm camera **rotation lag enabled** (speed 14) to smooth LMB orbit drag while preserving v0.9.1 mouse sensitivity (yaw 0.85 deg/pixel, pitch 0.50 deg/pixel).
- Vertical angle range expanded from **40°–82° to 16°–84°**, allowing much lower camera angles.
- Pivot raised slightly from **110 -> 130 cm** above the player.
- Original third-person camera and movement bindings remain untouched.

## Test in Unreal
1. From third person, Shift to top-down; LMB drag (horizontal and vertical) to test orbit and lowered angles, RMB to move.
2. Press TAB, then TAB to return to top-down; RMB should still move.
3. Shift to third person; WASD and camera look should work again.
4. Repeat steps 2–3 several times, including changing camera modes between meditations. WASD must always recover.

**Environment:** Changes were structurally checked against v0.9.1 source; compile and gameplay verification require the user's Unreal 5.8 installation.
