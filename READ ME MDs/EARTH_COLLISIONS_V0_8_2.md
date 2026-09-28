# Gameplay v0.8.2 — Shared Earth collision integration

## Scope

Fix only the two reported gameplay defects. This is a small source patch applied
**on top of v0.8 and v0.8.1**. The Inner Realm, editor, and spell definition UI
are untouched.

1. Constructed forms must block player Pawn collision, rather than explicitly ignoring it.
2. Constructed forms must RECEIVE the same generic impact request and undergo
   the same Earth Boolean subtraction as the original 4m Earth test block.

## Ownership / dependency graph

```text
SpellCreation -> FEarthSpellDefinition (data only)
  |
  v
EarthMagic::AEarthSpellBody (adapter / composition root)
  |-- UEarthMaterialComponent    [from EarthFoundation]
  |       \-- FMaterialPhysicalProperties [from MaterialCore]
  |-- IImpactProvider / IImpactReceiver [from ImpactSystem]
  |       \-- UImpactSolver (UNCHANGED)
  |-- UEarthSubtractionComponent [from EarthFoundation, UNCHANGED]
  |-- FEarthSpellDamageGeometry [EarthMagic, shape geometry only]
  |-- Chaos simple physical mesh proxy [moving collision / Pawn blocking]
  \-- DynamicMesh editable surface [real subtraction / settled exact collision]
```

- No physics equations were copied into EarthMagic.
- No geometry Boolean code was copied into EarthMagic.
- EarthFoundation does not depend on EarthMagic.
- The source and target use the same Earth material state, including user-edited
  hardness, toughness, elasticity, cohesion and body-derived density.
- A single impact transaction is processed per pair: the receiver requests
  target subtraction, and the source reads the existing source/motion result.
- Default unmodified Earth bodies persist: no 60-second disappearance timer.

## Collision implementation and honest limitation

Unreal/Chaos cannot simulate an arbitrary newly Boolean-cut triangle mesh as a
moving rigid body with *exact* concave collision using this simple setup.
This v0.8.2 prototype deliberately has TWO collision representations:

**Moving / falling**: an engine primitive collision proxy blocks players and
other bodies; a separate editable DynamicMesh displays actual impact holes and
follows the moving body. Mass is reduced after successful target subtraction,
but moving collision remains an approximation of the original outer shape.

**Damaged and fully asleep**: after a short settled interval, this particular
Earth body is converted to a static, complex-as-simple DynamicMesh collider.
The player and subsequent projectiles can then collide against the *cut* mesh.
It is no longer a simulated free rigid body in this state. A separate future
'fracture / detach / resume physics' system must handle reactivating stationary
cut chunks; this patch does not fake dynamic concave rigid-body physics.

Target volume/mass reduction uses the existing solver's **estimated** removed
volume; exact post-Boolean volume integration is deferred.

For two moving bodies, relative source velocity is evaluated by ImpactSystem,
then the source's post-impact motion is converted back to world velocity. Chaos
handles physical target motion; this isn't a fully coupled two-body impulse
solver yet. That enhancement belongs in ImpactSystem rather than in EarthMagic.

## Test plan

1. Press E to create a cube (speed 0, e.g. 1.5m dimensions) above the ground.
   Walk into it: the player should stop against it.
2. Create another Earth object (speed 15-35 m/s) aimed at the first. Check
   that the target visibly loses material and the on-screen message says
   TARGET DEFORMED. Both must obey gravity while moving.
3. Repeat with Sphere, Cube and Cone as targets. Repeat at different hardness,
   toughness, elasticity, size, and mass settings.
4. Allow a damaged Earth object to fully settle before checking cut-hole
   player collision. During motion its simple physics proxy is intentionally
   approximate. The original Earth test cube should continue working.

## Build status

The patch was source-reviewed and packaged here but **cannot be compiled against
an actual UE 5.8 install in this environment**. The local Unreal build is the
first true validation. If it fails, upload the first compiler error and log;
do not delete your prior backup or the whole project.
