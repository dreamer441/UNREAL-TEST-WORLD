# AMADEUS Gameplay v0.13 — Spell Workbench V1

Base inspected on GitHub:
- repository: dreamer441/UNREAL-TEST-WORLD
- current main: 5b37b51
- playable code baseline is still the pre-cleanup v0.12.2.2 state (`ecbeb5c`)
- Desktop GPT's pushed changes after that baseline are documentation/planning only.

## Patch 1 scope

This patch intentionally does NOT add Orientation, Amount, patterns, ready-spell slots, or the future node graph yet.

It adds the foundation we agreed on first:

1. TAB's existing sliders/key boxes stay intact.
2. The editor is moved to the left.
3. A separate Workbench preview frame appears on the right.
4. A presentation-only Manny model is placed in the Inner Realm as a scale/placement reference.
5. The existing SpellPreview node is extended into a shared renderer:
   - live casting still uses it;
   - the Workbench persistent/default spell now uses it too.
6. Workbench preview visual language:
   - Sphere/Cube/Cone construction grid;
   - density controls grid density;
   - stored Speed shows 0/1/2/3 speed-ring levels;
   - stored Distance moves the spell relative to the mannequin.
7. No physics, EarthMagic, ImpactSystem, LiveSpellCasting hierarchy, or actual casting behavior is changed.

## Architecture rule

Workbench UI does not own spell physics.
It edits SpellCreation data and SpellPreview observes that data.

Current flow:

    SpellCreation persistent defaults
               |
               v
        Shared SpellPreview
          /           \
    Workbench        Live Cast
      view             view

The mannequin is a presentation-only reference actor. It is NOT the gameplay pawn.

## Install

1. Close Unreal.
2. Extract this ZIP into `D:\TESTUNREALPROJECT\`.
3. Allow replacement of the included InnerRealm / SpellPreview source files.
4. Run `APPLY_AND_REBUILD_WORKBENCH_V1.bat`.
5. If prompted by Unreal, choose YES to rebuild.

## First test

- Enter Play.
- Press TAB.
- Existing controls should appear on the left.
- Right side should show `SPELL WORKBENCH / 3D PREVIEW`.
- Manny + the stored spell should be visible in the world behind that frame.
- Change Sphere/Cube/Cone and dimensions.
- Change Density and confirm the grid changes.
- Set Speed to zero: no speed rings.
- Raise Speed: rings appear.
- Change Distance and confirm spell preview moves relative to Manny.
- Exit TAB and confirm the Workbench preview disappears.
- Re-enter Top Down and confirm live casting behaves exactly as before.

If the preview scene is functionally correct but its framing needs visual tuning,
that is a small follow-up patch rather than an architecture change.
