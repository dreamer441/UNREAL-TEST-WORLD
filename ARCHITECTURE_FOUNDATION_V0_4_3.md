# ProjectX Foundation v0.4.3

## Architecture law

**Modules exchange requests/results. They do not reach inside one another.**

The runtime path is intentionally node-like:

```text
MaterialCore
    |
    v
ImpactSystem
    |
    +-- Energy Node
    |     input: source body + target material + contact
    |     output: energy accounting
    |
    +-- Target Response Node
    |     input: energy accounting
    |     output: removed volume + crater radius/depth/direction
    |
    +-- Source Response Node
          input: energy accounting + target response
          output: integrity + remaining volume + residual energy/speed

EarthFoundation
    input: generic Target Response
    output: Earth geometry/collision change

EarthTestHarness
    input: generic Source Response
    output: temporary projectile remnant behavior + diagnostics
```

## MaterialCore

Owns generic material data only:
- density
- hardness
- cohesion
- plasticity
- friction
- temperature

It has no Earth, projectile, spell, geometry, or collision-result knowledge.

## ImpactSystem

Owns collision calculations only. It does not edit meshes or destroy actors.

### Energy Node
Calculates:
- source mass
- full and normal impact speed
- kinetic energy
- normal/tangential energy
- target coupling
- target effective energy
- target resistance

### Target Response Node
Calculates:
- target absorbed energy
- removed volume
- contact area
- penetration drive
- lateral spread
- crater radius
- penetration depth
- penetration direction

### Source Response Node
Calculates:
- blocked energy
- source fracture capacity
- source damage energy
- source integrity
- remaining source volume fraction
- residual kinetic energy
- residual speed
- whether the source survives
- whether continued travel is physically possible

These are descriptive results, not actor commands.

## EarthFoundation

Earth consumes only the generic ImpactResult.Target data.

Earth owns:
- Earth material specialization
- Earth block geometry
- boolean subtraction
- Earth collision rebuild

Earth does **not** decide projectile survival.

## EarthTestHarness

Prototype-only layer.

It owns:
- E-key firing
- projectile sliders
- debug text
- visual realization of projectile survival

A destroyed source disappears. A surviving source becomes a smaller physical remnant. If the generic impact result says continuation is possible and the carved channel can fit it, the test projectile attempts to continue through the new channel.

This behavior is intentionally outside ImpactSystem and EarthFoundation so it can later be replaced by the real spell/projectile implementation without changing the physics foundation.

## Dependency direction

```text
MaterialCore
   ^
   |
ImpactSystem
   ^
   |
EarthFoundation
   ^
   |
EarthTestHarness
```

No reverse dependency is allowed.

## Next safe expansion points

- impact VFX can consume ImpactResult without changing physics
- fracture/chunk generation can consume SourceResponse/TargetResponse
- future materials can implement ImpactReceiver without changing projectile code
- spell-created bodies can implement ImpactProvider without changing Earth
