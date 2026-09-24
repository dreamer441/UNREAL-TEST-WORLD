# Inner Dimension / Spell Creation Architecture v0.6

## Architectural rule
Each module owns one responsibility and communicates through explicit data contracts. No module reaches inside another module's implementation.

## SpellCreation
Owns:
- the player's current projectile spell definition;
- the Inner Dimension state;
- the Inner Dimension editing UI;
- entering/exiting that UI with TAB.

Does NOT own:
- projectile spawning;
- collision or impact calculations;
- Earth geometry;
- physical-body simulation.

Current data contract: `FProjectileSpellDefinition`.

## EarthTestHarness
Owns only disposable prototype execution:
- reads the stored spell definition from `SpellCreation`;
- spawns the test projectile when E is pressed;
- gives the projectile that definition.

It no longer owns sliders or spell state.

## Impact debug filtering
Ordinary non-material collisions (floor / landscape) are left to Chaos rigid-body physics and do not print custom impact messages.
Material-impact events below 0.75 m/s normal speed are treated as resting contacts and ignored by the custom Impact pipeline.

## Flow

    TAB
     |
     v
SpellCreation / Inner Dimension
     |
     | stores FProjectileSpellDefinition
     v
TAB -> Physical World
     |
     | E
     v
EarthTestHarness
     |
     | reads stored definition
     v
Test Projectile
     |
     v
ImpactSystem -> EarthFoundation

## Future direction
The current full-screen blank Inner Dimension is deliberately only a presentation shell. Later the UI can become a spatial spell-construction world without changing the spell-definition contract or Impact/Earth modules.
