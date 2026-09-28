# AMADEUS Gameplay v0.13.5
## Codex Grammar + Motion Direction

Requires the working **v0.13.4.1 World Codex** project.

This is the final grammar/motion foundation before Rune Canvas V1.

### 1. Codex Tier grammar

Every Codex concept now has one structural Tier:

- **Tier I / Foundation** — starts a construction; cannot be attached beneath another concept.
- **Tier II / Operator** — modifier/operator/reference; can have a parent and can accept children.
- **Tier III / Terminal** — value/leaf; can attach to something but cannot accept children.

Tier is structural grammar only. Capability and relationship rules remain the
semantic compatibility layer.

Examples:

- Earth = Tier I
- Speed = Tier II
- Motion Direction = Tier II
- Amount = Tier II
- Magnitude 0..5 = Tier III
- Forward / Outward / Tangent = Tier III

### 2. Magnitude vocabulary

The Codex now contains six terminal signs:

- 0 — None / minimum
- 1 — Very Low
- 2 — Low
- 3 — Medium
- 4 — High
- 5 — Maximum

These are normalized semantic levels for the future Rune Canvas. The parent
modifier decides the exact physical mapping.

Examples:

- Speed + 5 -> maximum allowed speed
- Speed + 0 -> 0 m/s
- Density + 0 -> minimum valid density, not impossible zero-density Earth

Current Workbench sliders remain numeric. This patch adds the language, not a
forced five-step quantization of current gameplay.

### 3. Airborne semantics

The ambiguous Codex entry `In Air` is replaced by **Airborne**.

Airborne means:

> A boolean state of a referenced physical object. It is true while that object
> has no valid supporting ground/surface contact.

It is explicitly not an event and not a repeat command.

Future grammar distinctions are documented:

- `IF Person -> Airborne` = check a state
- `WHILE Person -> Airborne` = sustain behavior while state remains true
- `WHEN Person -> Became Airborne` = react to a transition event
- `WHEN Person -> Landed` = react to landing

The event execution system itself is still future work.

### 4. Orientation vs Motion Direction

These are now fully separate:

- **Orientation** = which way an object faces
- **Motion Direction** = which way an object travels

Motion Direction choices:

- Forward
- Backward
- Up
- Down
- Outward
- Inward
- Tangent

`Outward`, `Inward`, and `Tangent` resolve separately for each pattern instance. `Tangent` is an initial straight-line tangent direction; it does not create an orbit.

Examples:

`Circle + Orientation Up + Direction Outward`

- every object remains visually Up
- every object launches radially away from the circle center

`Circle + Orientation Outward + Direction Forward`

- every object faces outward
- every object still travels together in the cast direction

This fixes the v0.13.3 behavior where Pattern Orientation changed facing but all
objects always inherited one forward launch direction.

For a single centered object, pattern-relative Outward/Inward/Tangent have no
meaningful pattern vector and deliberately fall back to Forward.

### 5. New SpellMotion module

Pipeline:

`Pattern -> instance locations/orientations`

and independently:

`Motion Direction -> per-instance launch vector`

then:

`SpellExecution -> elemental realization`

`SpellMotion` knows no Earth physics, UI, damage, or key bindings.

### 6. Ready slots

Motion Direction is stored in the full `FSpellDefinition`, so prepared spell
slots preserve it automatically.

### Not included yet

- Rune Canvas
- stacking / multiple spell roots
- IF/WHEN/WHILE execution
- drawing recognition
- player-discovery filtering
- universal modifier key boxes
