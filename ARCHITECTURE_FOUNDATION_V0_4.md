# Foundation Architecture V0.4

## Core rule
Modules communicate through explicit data contracts and request/result objects. No module reaches inside another module's implementation.

## MaterialCore
Owns generic physical material data only:
- Density
- Hardness
- Cohesion
- Plasticity
- Friction
- Temperature

Forbidden: impacts, Earth-only state, projectiles, spells, geometry, rendering.

## ImpactSystem
Owns the pure impact function.

Input:
- source volume
- source material properties
- source velocity
- contact radius
- target material properties
- contact position and surface normal

Output:
- source mass
- impact speed
- kinetic energy
- energy coupling
- effective energy
- target resistance
- removable volume
- temporary geometry-adapter cutter values

Forbidden: Earth-specific logic, spell logic, mesh editing, projectile class logic.

## EarthFoundation
Owns the Earth material family and Earth geometry response.

Earth state:
- generic `FMaterialPhysicalProperties` from MaterialCore
- Earth-only properties such as Moisture

Flow:
`FImpactRequest -> ImpactSystem -> FImpactResult -> EarthSubtraction -> mesh + collision update`

Forbidden: test input, projectile UI, spell construction.

## EarthTestHarness
Temporary prototype layer. It can be deleted later without changing the three foundation modules.

Owns:
- E-key test projectile
- runtime projectile settings
- runtime slider panel
- impact diagnostics

Controls:
- `F1` or `TAB`: enter/leave slider editing mode
- `E`: fire when in gameplay mode
- sliders: Speed / Size / Density

Hardness and Cohesion are already projectile variables but intentionally remain fixed for this first UI pass.

## Dependency direction
```text
MaterialCore
     ^
ImpactSystem
     ^
EarthFoundation
     ^
EarthTestHarness
```
EarthFoundation also reads MaterialCore directly. Dependencies never point upward.

## Future magic rule
The future spell system may create/configure physical bodies and material states, but it must not bypass ImpactSystem with hard-coded spell damage.
