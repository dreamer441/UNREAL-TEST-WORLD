# Live Casting Hierarchy v0.12.1

The live casting session is an explicit state machine rather than a loose collection of active keys.

```text
Empty
  |
  | Element
  v
ElementSelected
  |
  | Shape
  v
ShapeSelected
  |
  | any valid Modifier
  v
ModifierActive / CastReady
  |
  | SPACE
  v
Cast -> Reset -> Empty
```

## Ownership

- `LiveSpellCasting` owns the transient stage/state and validates transitions.
- `SpellCastingBindings` reads physical keys and asks the session to transition or modify.
- `SpellPreview` renders only the states already accepted by the live session.
- `EarthTestHarness` executes SPACE only when `LiveSpellSession::CanCast()` is true.
- `SpellCreation` remains the persistent TAB-default source.

## Invalid input

Inputs from a later stage are inert until the required earlier stage exists. This prevents accidental constructions such as Speed -> Earth -> Cast or Shape -> Modifier without an element.

## Downstream reset law

Changing an earlier construction decision invalidates everything downstream:

- choosing/re-choosing an element clears shape + modifiers;
- choosing/changing shape clears modifiers;
- casting clears the entire transient session.

This rule keeps future multi-element and more complex spell grammars deterministic.
