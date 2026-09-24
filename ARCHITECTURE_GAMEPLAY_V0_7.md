# Gameplay Architecture v0.7 — Inner Realm + Earth Forms

## Architectural law

**Each module owns one responsibility and communicates through explicit data/contracts.**

No UI code edits Earth geometry. No spell-creation code solves impacts. No test input owns spell data.

## Runtime flow

```text
PLAYER INPUT
   TAB
    ↓
SpellCreation
   ├─ Inner Realm presentation state
   └─ FEarthSpellDefinition (stored construction data)

PLAYER INPUT
    E
    ↓
EarthTestHarness
    ↓ reads stored definition only
EarthMagic
   ├─ EarthSpellShapeBuilder
   └─ AEarthSpellBody
        ↓ collision request
ImpactSystem
        ↓ ImpactResult
Target Material / EarthFoundation
```

## SpellCreation

Owns only:
- Inner Dimension / meditation state
- spell construction data
- shape editor data
- distance / speed / mass values
- Earth material parameters exposed to the player

It does not spawn bodies or call ImpactSystem.

### Current Earth form definition

Shape:
- Sphere: radius
- Cube: X / Y / Z dimensions
- Cone: radius + length
- Pyramid: base X / base Y / height
- Wall: thickness / width / height

Spatial/body:
- Distance: creation position in front of the player's view
- Speed: initial forward velocity; 0 means no launch velocity
- Mass

Player-facing Earth material:
- Hardness
- Toughness
- Elasticity

Internal Earth defaults retained for physics but hidden from the current UI:
- Cohesion
- Rigidity

Density is derived from `mass / selected-shape volume`.

## Inner Realm

v0.7 deliberately treats meditation as a separate gameplay state rather than an in-world HUD.

While active:
- the physical world is fully covered by an opaque realm presentation layer
- the player pawn is hidden
- movement and look input are disabled
- the mouse is released for construction controls
- E-casting is disabled

TAB returns to the physical state without losing the stored spell definition.

The current visual realm is intentionally minimal. A future 3D meditation environment can replace the presentation layer without changing the SpellCreation data contract.

## EarthMagic

EarthMagic is the bridge from *spell definition* to *physical Earth body*.

It owns:
- procedural shape realization
- body mass / collision / gravity
- applying Earth material values to the source body
- producing generic ImpactRequests on collisions
- consuming the source half of ImpactResults

It does not own:
- the spell editor
- target-material response
- crater calculations
- Earth terrain subtraction

## Shape geometry

`FEarthSpellShapeBuilder` converts the definition into a convex procedural mesh.
All current shapes use convex collision so they can remain movable Chaos bodies.

This lets shape become real runtime geometry instead of a visual label.

## Speed = 0

Speed zero means **zero initial launch velocity**, not "ignore physics".
Gravity still applies to every free Earth body. Therefore a zero-speed form created in mid-air will fall; a form created on supporting ground can remain at rest.

This preserves the global gravity rule instead of creating a special spell exception.

## Future expansion points

The current definition is intentionally extensible. Future modules can add:
- rotation/orientation construction
- shape composition
- hollow/solid structure
- density as a deliberate magic variable
- anchoring/support rules
- multiple stored spells
- discovery/knowledge gates
- non-Earth material implementations

Those additions should extend data/contracts rather than add named hard-coded spells.
