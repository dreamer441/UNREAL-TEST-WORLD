> Superseded for runtime dispatch details by `ARCHITECTURE_MATERIAL_INTERACTION_V0_3_1.md`.

# Material Interaction / Earth Subtraction V0.3

## Goal
Replace fake vertex dents and pre-written projectile damage with a reusable material/material interaction pipeline.

The projectile does **not** say "deal 50 damage" and Earth does **not** contain projectile-specific branches.

## Runtime graph

```text
Impact source
  physical data only
  - volume
  - density
  - hardness
  - cohesion
  - velocity
        |
        v
MaterialImpactProvider interface
        |
        v
MaterialInteractionSolver
  - mass = density * volume
  - kinetic energy = 1/2 m v^2
  - uses normal incidence
  - source/target hardness coupling
  - target density/hardness/cohesion resistance
        |
        v
MaterialImpactResult
  - mass
  - kinetic energy
  - effective energy
  - resistance
  - removable volume
  - geometry request scale
        |
        v
EarthSubtractionComponent
  - creates temporary cutter geometry
  - Boolean Difference against Earth Dynamic Mesh
  - updates collision
```

## Module boundaries

### MaterialInteraction plugin
Generic. It MUST NOT know about Earth, spells, player input, or Dynamic Mesh implementation.

Owns:
- `FMaterialPhysicalState`
- `FMaterialImpactBody`
- `FMaterialImpactRequest`
- `FMaterialImpactResult`
- `FMaterialInteractionTuning`
- `IMaterialImpactProvider`
- `UMaterialInteractionSolver`

### EarthFoundation plugin
Earth adapter. It owns Earth material state and Earth geometry.

Owns:
- Earth-specific extended material metadata
- Earth Dynamic Mesh block
- conversion from Earth properties to generic material state
- realizing solved removal through topology subtraction
- collision recook after topology changes

It MUST NOT know which concrete projectile/spell/tool caused an impact.

### EarthTestHarness plugin
Temporary prototype client of the public contracts.

Owns:
- E-key test input
- disposable spherical projectile
- projectile physical values

It MUST NOT contain Earth damage formulas or edit Earth geometry directly.

## Current prototype formula

Source mass:
`mass = density * volume`

Kinetic energy:
`KE = 0.5 * mass * speed^2`

Only velocity into the surface contributes to impact energy. A glancing hit therefore transfers less energy than a perpendicular hit.

Source hardness controls transfer efficiency against target hardness. Target density, hardness, and cohesion create a resistance expressed as energy per cubic meter.

Finally:
`removable volume = effective impact energy / target resistance`

The constants in this response model are prototype tuning data, not claimed real-world geotechnical values. They are isolated in `FMaterialInteractionTuning` so the model can be replaced without changing projectiles or geometry code.

## Geometry representation in V0.3

The solver outputs a *quantity* of material to remove. It does not prescribe mesh vertices.

The Earth adapter currently represents that removal with a spherical Boolean cutter intersecting the surface. This is deliberately replaceable. Later implementations can use projectile/spell shape strategies, fracture, voxel/SDF terrain, chunks, or volume conservation without rewriting the interaction solver.

## Important V0.3 behavior change

Ordinary player movement no longer deforms Earth. Player weight/foot pressure is a different physical phenomenon and should later enter through a dedicated pressure/contact system rather than being treated as a projectile impact.

## Long-term extension points

- New materials implement/produce the same `FMaterialPhysicalState` contract.
- New impact sources implement `IMaterialImpactProvider`.
- Spell construction can produce source body data without owning target response logic.
- Shape becomes a separate geometry/interaction strategy rather than an enum with a fixed list.
- Thermal, chemical, fluid, elastic, fracture, and phase-state interactions can become parallel solver nodes instead of being embedded into Earth.
