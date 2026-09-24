# Earth Foundation v0.2 — Projectile Physics Test

## Architecture law

**Data describes. Geometry represents. Requests describe change. Deformation applies it. Adapters translate external events. Test code never becomes Earth code.**

## Why the player movement looked strange in v0.1

V0.1 used the **actor's total speed** for collision deformation. That means fast sideways movement at an edge could count as a strong impact, while CharacterMovement could report little or no useful velocity during some landings.

V0.2 changes the generic collision adapter to use **normal approach speed**:

`impact speed = velocity component pointing into the contacted surface`

So running tangentially across a flat surface should not be interpreted as a downward hit. Player footsteps/weight are NOT solved yet; they deserve a separate contact/pressure system later rather than abusing collision speed.

## Core Earth nodes

### `FEarthPhysicalProperties` — material data
Density, Hardness, Cohesion, Moisture, Temperature, Friction, Plasticity.

### `UEarthMaterialComponent` — material response
Converts material data into normalized Earth responses. No geometry or input code.

### `UEarthGeometryComponent` — geometry
Creates a gridded closed block. V0.2 adds independent vertical resolution so the sides of a cube can deform as well as its top.

### `FEarthDeformationRequest` — message contract
Contains:
- world position
- outward surface normal
- radius
- requested inward depth

The surface normal makes the request orientation-independent. Top impacts dent downward; side impacts dent inward from the side.

### `UEarthDeformationComponent` — deformation algorithm
Consumes the request, applies material resistance, moves nearby surface vertices inward, recomputes normals, then rebuilds collision.

### `IEarthImpactProvider` — optional impact-source contract
Allows an external source to describe a precise deformation request without Earth knowing its concrete class. If an impact source implements this contract, Earth consumes that request; otherwise it falls back to the generic collision adapter.

### `UEarthImpactResponseComponent` — generic collision adapter
Converts ordinary collision approach velocity into a deformation request. Uses the velocity component normal to the surface, not total speed.

### `AEarthBlockActor` — composition root
Wires the Earth nodes together. No spell/input/projectile algorithm belongs here.

## Test-only nodes

The `EarthTestHarness` plugin is intentionally separate from `EarthFoundation`.

### `UEarthTestInputSubsystem`
During Play only, detects `E` and launches a test projectile from the player's view. It does not modify the character Blueprint or input assets.

### `AEarthTestProjectile`
A simple physics sphere used to hit Earth. It implements `IEarthImpactProvider`, supplying radius/depth/impact-normal data through the generic Earth impact contract.

The dependency direction remains:

`TEST HARNESS -> EARTH CONTRACT`

Never:

`EARTH -> TEST PROJECTILE TYPE`

The test projectile is disposable later. EarthFoundation is not.

## 4m target

Editor command:

`Tools -> AMADEUS -> Create 4m Earth Projectile Target`

Creates:
- 4m x 4m x 4m block
- 25 x 25 x 25 edge surface resolution
- same Earth material/state system
- all faces deformable
- collision rebuilt after every deformation

Play, aim at a face, press `E`.

## Still intentionally unsolved

- conservation of displaced volume
- chunks/fracture
- pressure/weight/footprints as a distinct system
- elastic rebound over time
- underground volumetric material
- spell construction
- replication/save/load

Those remain separate modules so the test does not quietly become permanent spaghetti.
