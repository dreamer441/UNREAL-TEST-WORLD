# Material Interaction + Earth V0.3.1

## Runtime flow

`Impact Source -> FMaterialImpactRequest -> IMaterialImpactReceiver -> MaterialInteraction Solver -> Material Response -> Geometry Adapter`

### MaterialInteraction owns
- generic material physical state
- generic impact body/request/result data
- `IMaterialImpactProvider`: how a source describes itself
- `IMaterialImpactReceiver`: how a target accepts a generic impact
- the interaction solver

It does **not** know Earth, spells, projectiles, weapons, meshes, or rendering.

### EarthFoundation owns
- Earth material data adapter
- Earth block geometry
- Earth implementation of `IMaterialImpactReceiver`
- conversion of a solved removed volume into a Boolean cutter
- collision refresh after topology changes

It does **not** know the Earth test projectile class.

### EarthTestHarness owns
- temporary E-key projectile
- test input
- on-hit diagnostics

It may be deleted later without changing the material or Earth architecture.

## V0.3.1 bug fix

V0.3 relied on the Earth mesh's `OnComponentHit` callback to discover the source. Unreal can report contact normals with opposite orientation depending on which side's callback is being handled. The solver expected an outward target normal, so a reversed normal could make incidence zero. That yielded no removal and also skipped the old debug message.

V0.3.1 dispatches the request from the source callback that is already known to fire, through the generic receiver interface. Both source and receiver canonicalize the surface normal so it opposes the incoming velocity. Diagnostics are emitted for every projectile collision, including rejected or failed interactions.
