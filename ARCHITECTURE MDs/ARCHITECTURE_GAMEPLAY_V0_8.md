# ProjectX Gameplay Architecture v0.8

## Goal
Stabilize the first playable Earth-magic loop while keeping the system modular enough to expand later.

## Runtime nodes

### SpellCreation
Owns **data only**.

- Stored Earth spell definition
- Shape selection: Sphere / Cube / Cone
- Shape dimensions
- Distance
- Speed
- Mass
- Earth material values: Hardness / Toughness / Elasticity
- Internal Earth defaults: Cohesion / Rigidity

Forbidden responsibilities:
- camera switching
- UI presentation
- spawning bodies
- physics
- impact solving
- target geometry changes

### InnerRealm
Owns the **meditation / creation presentation**.

- TAB enter/exit
- fixed realm camera
- blank realm plane
- mouse/input mode while editing
- spell editor UI
- reads/writes SpellCreation through its public contract

Forbidden responsibilities:
- spell execution
- Earth body physics
- impact formulas
- terrain mutation

### EarthMagic
Owns **runtime realization of Earth spell data**.

- maps Sphere/Cube/Cone definitions to stable physical meshes
- applies requested dimensions
- applies mass and Earth physical material
- gravity always enabled for dynamic Earth spell bodies
- applies launch velocity when Speed > 0
- packages source data for ImpactSystem
- applies source-side ImpactResult

The current prototype uses Unreal Engine BasicShapes behind a shape-realization node. This is intentionally replaceable later without changing SpellCreation or ImpactSystem.

### EarthTestHarness
Temporary execution adapter.

- E reads the stored spell definition
- spawns an EarthMagic body at the configured distance
- gives it the configured initial speed
- blocks E while InnerRealm is active

This module may be deleted/replaced later without changing SpellCreation, InnerRealm, EarthMagic, ImpactSystem, or EarthFoundation.

### ImpactSystem
Unchanged ownership:

Contact -> Energy -> Target -> Source -> Motion -> ImpactResult

### EarthFoundation
Unchanged ownership:

Earth material target + subtractive target geometry/collision response.

## Player loop

Physical world
  TAB
    -> InnerRealm fixed camera + blank plane
    -> edit Earth form
  TAB
    -> return to previous physical-world camera
  E
    -> EarthTestHarness reads stored SpellCreation data
    -> EarthMagic realizes physical body
    -> gravity + optional initial speed
    -> collisions flow through ImpactSystem

## Shape contract

Sphere
- Radius

Cube
- X
- Y
- Z

Cone
- Radius
- Height

Shape is independent from motion. A cone remains an upright cone; Speed only gives the body translational velocity. Rotation/orientation can become its own future spell modifier.

## Earth defaults

- Hardness: 0.25
- Toughness: 0.40
- Elasticity: 0.08
- Cohesion: 0.35 (internal)
- Rigidity: 0.55 (internal)

## Architectural law
Each node receives explicit data, performs one responsibility, and outputs data or a result. No node reaches into another node's internal implementation.
