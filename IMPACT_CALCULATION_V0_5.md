# Impact calculation v0.5 — readable model

This is a game-physics model, not a finite-element simulator. The goal is consistent emergent behavior from reusable properties.

## 1. Contact
Input velocity is split into:
- normal speed: movement into the surface
- tangential speed: movement across the surface

Incidence = dot(incoming_direction, -surface_normal)

## 2. Energy
Mass is now an explicit body property.

KineticEnergy = 0.5 * Mass * Speed^2
NormalEnergy = 0.5 * Mass * NormalSpeed^2
TangentialEnergy = KineticEnergy - NormalEnergy

Hardness pairing determines how much normal energy couples into the target.
Target density/hardness/cohesion determine resistance per cubic meter.

## 3. Target response
RemovedVolume = EffectiveTargetEnergy / TargetResistance

The amount and shape stay separate.
Speed + relative density + relative hardness increase penetration drive.
Contact size + target cohesion increase lateral spread.

The same removed volume can therefore become narrow/deep or wide/shallow.

## 4. Source structural response
The projectile does not automatically disappear.

Toughness is the main resistance to fracture.
Cohesion helps it remain one body.
High rigidity with low toughness creates brittleness.
Hard targets punish softer sources more strongly.

Output:
- Integrity
- RemainingVolumeFraction
- Survives / destroyed

## 5. Motion / energy transfer
Restitution controls bounce tendency.
Rigidity controls how efficiently rebound transfers through the material pair.
Friction removes tangential motion.

If the target opens a large enough channel, a surviving projectile can continue forward.
If no channel exists, remaining normal motion can return as reflection/rebound.
If too little motion energy remains, the projectile stops and gravity takes over.

Impulse transferred to the target is approximated from momentum change:

TransferredImpulse = InitialMomentum - FinalProjectileMomentum
EstimatedAverageForce = |TransferredImpulse| / EstimatedContactDuration

The target is currently static Earth, so the impulse is reported but not yet used to move the whole block. Future dynamic targets can consume it.
