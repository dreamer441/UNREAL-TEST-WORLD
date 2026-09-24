# ProjectX Foundation v0.5 — Physics Architecture Contract

## Core law
Each runtime module owns one responsibility and communicates through explicit data contracts. No module reaches into another module's implementation.

## Module graph

MaterialCore
  -> PhysicalBody
  -> ImpactSystem
  -> EarthFoundation

EarthTestHarness depends on the foundation only for experiments and can be deleted later.

## MaterialCore — WHAT a substance is
Owns generic material properties only:
- Density
- Hardness
- Cohesion
- Plasticity
- Friction
- Restitution
- Toughness
- Rigidity
- Temperature

Forbidden: actor movement, collision callbacks, Earth geometry, spells.

## PhysicalBody — WHAT a particular body is doing
Owns the generic body-state contract:
- Material
- Mass
- Volume
- Velocity
- Contact radius
- Gravity flag

Mass belongs to the body. Density belongs to the material.
For a known closed shape, density may be derived from mass / volume. Large static objects do not need a globally measured total mass just to expose local material density.

Forbidden: impact outcome, target geometry, spell logic.

## ImpactSystem — WHAT a collision means
Pure solver nodes:
1. ContactSolver — direction, normal/tangent speed, incidence, contact area.
2. EnergySolver — kinetic energy and target coupling/resistance.
3. TargetSolver — removed volume and crater/penetration shape.
4. SourceSolver — source fracture, integrity, remaining body fraction.
5. MotionSolver — restitution, residual velocity, impulse and estimated average force.
6. ImpactSolver — orchestrator only.

ImpactSystem never moves an actor and never edits a mesh.

## EarthFoundation — HOW Earth realizes a response
Owns:
- Earth-specific material state (generic material + moisture)
- Earth geometry
- Boolean subtraction
- Collision rebuild

Earth receives FImpactResult and realizes the target response. It does not decide projectile motion.

## EarthTestHarness — temporary experiment layer
Owns:
- E key test projectile
- Runtime slider UI
- Mapping the generic solver result back onto an Unreal physics sphere
- Debug text

Gravity is enabled on the projectile from launch and remains enabled after collisions.

## Data flow

Projectile/Test Body
  -> FPhysicalBodyState
  -> FImpactRequest
  -> ContactSolver
  -> EnergySolver
  -> TargetSolver
  -> SourceSolver
  -> MotionSolver
  -> FImpactResult
       -> EarthFoundation uses Target branch
       -> Projectile uses Source + Motion branches

## Non-negotiable separation
- MaterialCore does not know Earth.
- PhysicalBody does not know damage.
- ImpactSystem does not edit geometry or move actors.
- Earth does not calculate projectile recoil.
- TestHarness does not contain world physics rules.
