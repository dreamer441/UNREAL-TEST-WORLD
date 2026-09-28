# v0.11 Live Casting Rebuild

- Removed v0.10 slider-increment binding semantics.
- Replaced UI key capture with Slate `SInputKeySelector`.
- Added selector actions for Earth / Sphere / Cube / Cone.
- Added deterministic 0-3 second charge actions for Size, Speed, Density, Distance, Hardness, Toughness and Elasticity.
- Every new hold starts from that option's minimum; release preserves the reached value.
- Multiple charge keys can be held simultaneously.
- Added default Q/A/S/D bindings matching the target combat chord.
- Made Density an explicit spell/material property.
- Spell mass is now derived automatically from density and realized volume.
- Size is a generic combat attribute that scales all supported shape templates coherently.
- Existing Earth collision, deformation, camera modes, sprint, TAB realm and SPACE casting remain separate modules.
