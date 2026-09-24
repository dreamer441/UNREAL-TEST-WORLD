# Earth Foundation v0.1

This is deliberately a **foundation**, not a one-off test script.

## Architecture law

**Data describes. Geometry represents. Impacts request. Deformation modifies. The Actor only composes.**

No spell code, input code, player code, or Landscape-specific behavior is allowed inside the Earth runtime module.

## Nodes

### 1. `FEarthPhysicalProperties` — DATA CONTRACT
Owns only material attributes:
- Density kg/m³
- Hardness [0..1]
- Cohesion [0..1]
- Moisture [0..1]
- Temperature °C
- Friction
- Plasticity [0..1]

It contains no mesh logic.

### 2. `UEarthMaterialDefinition` — REUSABLE MATERIAL PROFILE
A Data Asset contract for future Soil / Clay / Sand / Stone / Ore definitions.

### 3. `UEarthMaterialComponent` — MATERIAL STATE NODE
Resolves a material profile or inline prototype properties and exposes material response.
It does not edit geometry.

### 4. `UEarthGeometryComponent` — GEOMETRY NODE
Creates/resets a gridded 3D Earth block and records the deformable top-surface vertex IDs.
It does not decide when or why deformation occurs.

### 5. `FEarthDeformationRequest` — MESSAGE CONTRACT
A system-neutral request:
- world position
- radius
- requested depth

Future magic, explosions, tools, physics, weather, or AI can all generate this same request.

### 6. `UEarthDeformationComponent` — DEFORMATION NODE
Consumes a deformation request + material response + geometry surface IDs.
Edits mesh positions, recomputes normals, then updates collision.
It does not listen for gameplay input or impacts.

### 7. `UEarthImpactResponseComponent` — COLLISION -> REQUEST ADAPTER
Converts collision velocity into a deformation request.
This adapter can later be replaced or complemented by spell/tool/explosion adapters.

### 8. `AEarthBlockActor` — COMPOSITION ROOT
Contains the nodes and wires them together.
It intentionally contains almost no Earth algorithm.

## V0.1 behavior

- Block: 20m x 20m x 3m by default.
- Top surface: 41 x 41 resolution.
- Complex-as-simple dynamic collision follows the deformed triangle surface.
- A radial dent changes real mesh vertices, not a texture/normal-map illusion.
- Collision is rebuilt after deformation.
- Hardness, Cohesion, Moisture and Plasticity influence permanent dent depth.
- Friction is connected to a runtime `UPhysicalMaterial` override.
- Density and Temperature are stored now but intentionally not given fake behavior yet.

## Deliberately NOT implemented yet

- Excavated volume conservation / displaced soil piles.
- Breaking chunks/fracture.
- Voxel volume representation.
- Multiple material layers underground.
- Network replication.
- Save/load of deformed terrain.
- LOD/chunk streaming.
- Spell system.

Those belong in later modules. Keeping them out now is how we avoid turning this first experiment into spaghetti.
