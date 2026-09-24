# AMADEUS Gameplay v0.12 — Live Casting Session + Preview

## Design law

Persistent configuration and live construction are different states.

- **SpellCreation** owns TAB/editor defaults.
- **SpellCastingBindings** owns key assignments and hold timing only.
- **LiveSpellCasting** owns the transient construction session and shared character-relative cast placement.
- **SpellPreview** owns non-physical visual feedback only.
- **EarthTestHarness** consumes a finished live construction on SPACE.
- **EarthMagic** continues to own physical Earth body realization/impact behavior.

No live key press writes back into the persistent TAB defaults.

## Live state

Every bound value starts formally inactive. Inactive means "use the TAB default", not a physically invalid value such as zero density.

A live value is created only after its key is pressed. Holding it for up to three seconds maps the hold to the authored range. Release freezes that temporary override until the cast is consumed or meditation cancels it.

SPACE with no live construction does nothing. A successful cast resets only the live session; defaults and bindings remain.

## Shape dimensions

Bindings are per dimension:

- Sphere: Radius
- Cube: X, Y, Z
- Cone: Radius, Height

The same physical key may drive multiple compatible value actions. Only dimensions belonging to the currently resolved shape consume their key. This permits:

- A = Sphere Radius, Cube X, Cone Radius (universal primary-size gesture)
- A = Cube X/Y/Z (uniform cube growth)
- A = Cube X while Y/Z remain unbound (wall-thickness style construction)
- different keys for X/Y/Z or Cone Radius/Height

Shape selector bindings remain mutually exclusive with other shape selectors to avoid one tap selecting conflicting shapes.

## Key unassignment

In the TAB editor, selecting a binding box and pressing its already-assigned key clears it back to empty.

## Placement

Spawn placement is never based on camera position.

The shared placement node uses:

1. player/pawn location,
2. a chest-height offset,
3. the horizontal casting direction,
4. shape half-extents for safe clearance,
5. a fixed player safety gap,
6. the authored Distance as additional distance.

Aim direction can still come from the top-down mouse target or the third-person camera, but the spell always appears in front of the character.

## Preview

While top-down and a live construction exists:

- explicitly selecting Earth draws a green aura around the character;
- a green ghost/wireframe Sphere, Cube or Cone appears at the exact shared cast placement;
- active shape-dimension holds resize that preview in real time;
- shape selector taps swap it immediately.

Speed and Density intentionally have no invented visual language yet.
