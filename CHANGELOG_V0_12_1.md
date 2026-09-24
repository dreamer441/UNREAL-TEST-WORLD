# AMADEUS Gameplay v0.12.1 — Casting Hierarchy

This patch makes live spell construction a strict ordered grammar:

`Element -> Shape -> Modifier -> Cast`

## Rules

- Empty session: only an Element key can begin construction.
- Element selected: Shape keys work; modifier keys and SPACE are inert.
- Shape selected: modifier keys become active; SPACE is still inert.
- First valid modifier activation moves the session to the cast-ready stage.
- Cast-ready: SPACE casts the resolved spell and resets the live session.

## Restart behavior

- Selecting Earth again restarts construction from the Element stage and clears the current shape/modifiers.
- Selecting/changing a shape after Earth clears current live modifiers and returns to the Shape stage. A modifier must then be applied again before casting.
- TAB defaults remain untouched. Unmodified properties still resolve from the TAB editor once the ordered live construction reaches cast-ready state.

## Preview behavior

- Element stage: Earth aura only.
- Shape stage: aura + ghost shape.
- Modifier stage: ghost shape updates live as dimension modifiers are held.

No material, deformation, collision, camera, TAB-editor, or Earth physics equations were changed.
