# v0.12

- Restored/kept the v0.11.1 TAB slider editor and changed its text/key labels to black on a light panel.
- Live key input no longer mutates the persistent TAB spell definition.
- SPACE is now a no-op until a live construction has actually started.
- Added `LiveSpellCasting` runtime plugin with transient session state and shared character-relative cast placement.
- Added `SpellPreview` runtime plugin with Earth aura + live ghost shape visualization.
- Casts now spawn in front of the character, never from the camera position. Distance is additional spacing after safe character/shape clearance.
- Replaced generic Size binding with per-shape/per-dimension bindings: Sphere Radius, Cube X/Y/Z, Cone Radius/Height.
- Duplicate compatible value bindings are allowed, enabling one key to scale several dimensions together.
- Default A binding is shared across Sphere Radius, Cube X and Cone Radius; Cube Y/Z and Cone Height start unbound.
- Re-selecting the same key in a binding box now clears/unassigns it.
- A successful cast clears only the transient live session; persistent TAB defaults and bindings remain.
- Held construction keys are required to release after a cast before they can start the next live session, preventing accidental immediate recasting state.
