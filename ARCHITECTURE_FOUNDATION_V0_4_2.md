# Foundation Architecture V0.4.2

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
Owns the pure impact calculation. It now produces **multiple independent outputs** instead of collapsing every collision into one damage number.

### Input
- source volume
- source material properties
- source velocity
- contact radius
- target material properties
- contact position and surface normal

### Output branch A: amount
Energy and target resistance determine:
- source mass
- kinetic/effective energy
- target resistance
- removable volume

### Output branch B: shape
Speed, source/target density, hardness contrast, contact size, and target cohesion independently determine:
- penetration drive
- lateral spread drive
- penetration aspect ratio
- crater radius
- penetration depth
- penetration direction

The amount branch answers **"how much material changes?"**.
The shape branch answers **"how is that change distributed in space?"**.

A small, fast, dense, hard projectile can therefore produce a narrow/deep profile while a large, slower projectile can produce a wide/shallow profile even when their removed volumes are similar.

Forbidden: Earth-specific logic, spell logic, mesh editing, projectile class logic.

## EarthFoundation
Owns the Earth material family and Earth geometry response.

Earth state:
- generic `FMaterialPhysicalProperties` from MaterialCore
- Earth-only properties such as Moisture

Flow:
`FImpactRequest -> ImpactSystem -> FImpactResult -> EarthSubtraction -> mesh + collision update`

`EarthSubtraction` interprets the generic radius/depth/direction result as an oriented ellipsoid boolean subtraction. ImpactSystem never touches the mesh.

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

The impact debug line now prints removed volume plus crater radius, penetration depth, and final shape ratio.

Hardness and Cohesion are already projectile variables but intentionally remain fixed for this UI pass.

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

A spell will eventually provide physical inputs (material, shape, volume, velocity, etc.). ImpactSystem remains responsible for calculating the resulting material interaction.
