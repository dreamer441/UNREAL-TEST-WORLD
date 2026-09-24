# AMADEUS Gameplay v0.11 — Live Casting Rebuild

## Source of truth
v0.10 live-slider behavior is discarded. v0.11 uses semantic actions with two input types:

1. **Selector/toggle action** — tap once to select an element or shape.
2. **Continuous/charge action** — hold from 0 to 3 seconds; each new press starts again at minimum, release stores the reached value.

Approximate feel:
- 1 second = low
- 2 seconds = medium
- 3 seconds = maximum

The value is calculated from hold duration, not by repeatedly incrementing the old slider value.

## Default playable chord
- `Q` = Earth selector
- `A` = Size charge
- `S` = Speed charge
- `D` = Density charge
- `SPACE` = cast

Sphere is the default shape, therefore `Q + hold A/S/D + SPACE` produces an Earth ball projectile.

## Bindable semantic options

### Element selectors
- Earth

### Shape selectors
- Sphere
- Cube
- Cone

### Continuous attributes
- Size
- Speed
- Density
- Hardness
- Toughness
- Elasticity

### Spatial continuous control
- Distance

Every option has its own key selector in the Inner Realm. Reusing a key transfers that key to the newly assigned option, so one physical key has one spell meaning.

## Size semantics
`Size` is intentionally generic instead of separate Sphere Radius / Cube X / Cone Height combat keys.
It sets representative dimensions for all supported shapes at once. This makes construction order-independent:

`hold Size -> select Cube` == `select Cube -> hold Size`

For detailed non-combat construction, a later precision editor can expose per-axis dimensions separately without changing this live-casting node.

## Density and mass
Density is now a first-class authored Earth property. Total body mass is derived automatically:

`mass = density * realized shape volume`

This prevents the player from specifying contradictory size/mass/density values and lets the existing Earth impact solver receive physically coherent bodies.

## Key assignment
The Inner Realm now uses Unreal Slate's dedicated `SInputKeySelector` instead of polling PlayerController key presses while a UI button has focus. This is specifically intended to remove the v0.10 binding-capture bug.

Reserved: TAB, SHIFT, SPACE, Escape, mouse buttons/wheel. They continue to own realm switching, camera switching, casting, cancellation, movement/camera and sprint behavior.

## Module ownership
- **SpellCreation** — constructed spell data; normalizes values and derives mass.
- **SpellCastingBindings** — key -> semantic action bindings, selector taps, 0-3 s hold sessions.
- **InnerRealm** — fixed meditation camera and key-binding UI only.
- **PlayerViewModes** — enables live casting only while top-down mode is active.
- **EarthMagic** — realizes the finished Earth definition as a physical body.
- **ImpactSystem / EarthFoundation** — unchanged impact/deformation behavior.
