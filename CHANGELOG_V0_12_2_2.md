# AMADEUS Gameplay v0.12.2.2 — Live Speed Zero-State Fix

Small live-casting correction.

- A newly constructed live spell now always starts at **0 m/s**, regardless of the Speed value saved in the TAB editor.
- Speed is only applied after the live **Speed modifier key** is explicitly pressed/held.
- SpellPreview now requires the live Speed parameter to be active before drawing any speed rings.
- Therefore the preview mapping is strict:
  - no Speed modifier / 0 speed -> 0 rings
  - low speed -> 1 ring
  - medium speed -> 2 rings
  - high speed -> 3 rings
- TAB Speed remains stored as authored data; this patch changes only how **live casting** resolves Speed.

Changed modules only:
- `LiveSpellCasting`
- `SpellPreview`
