# AMADEUS Gameplay v0.10 — Live Spell Slider Bindings

## Goal
Top-down mode becomes the fast/live casting workspace. The Inner Realm remains the place where controls are configured.

## Ownership

- **SpellCreation** owns the Earth spell definition and stored values.
- **SpellCastingBindings** owns key -> slider assignments and hold-to-increase live input.
- **InnerRealm** owns the binding UI and key-capture presentation.
- **PlayerViewModes** decides whether live binding input is enabled (top-down only).
- **EarthTestHarness / EarthMagic** continue to execute the stored spell; they do not know which keys created its values.

## Binding behavior
Every visible slider has a small key box on its left.

1. Click a key box in the Inner Realm.
2. The box shows `...`.
3. Press a free keyboard key.
4. The box displays that key.
5. Return to top-down mode.
6. Hold the assigned key: that slider rises continuously.
7. Release the key: the current value remains stored.
8. SPACE casts the current stored spell.

A physical key may own only one slider. Assigning the same key elsewhere transfers it to the new slider.

## Shape-specific slider IDs
Dimension bindings are semantic, not positional:

- Sphere Radius
- Cube X / Y / Z
- Cone Radius / Height

This prevents a Sphere Radius binding from silently becoming Cube X after changing shape.

## Reserved controls
TAB, Left/Right Shift, SPACE and mouse-wheel controls remain reserved because they already own realm switching, view switching, casting and sprint. Mouse/gamepad inputs are not captured as slider keys in this first version.

## Live adjustment
The live node changes slider values in normalized space, so different physical ranges feel comparable. Current rate: ~35% of a slider's full range per second of holding.
