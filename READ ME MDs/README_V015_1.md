# AMADEUS Gameplay v0.15.1
## Architecture Cleanup Phase 2 — Generic Workbench

Requires working **v0.15.0 Architecture Cleanup Phase 1**.

This patch removes the biggest remaining duplicate spell-data path from the
InnerRealm editor.

### Before

The canonical runtime spell was:

`FSpellDefinition`

but the Spell Modifier UI still edited:

`FEarthSpellDefinition`

through an adapter on every read/write.

SpellCreation also kept a synchronized private legacy shadow:

`StoredSpell`

alongside:

`StoredGenericSpell`

That meant every new property had two representations to keep in sync.

### After

The main editing path is now:

```text
Spell Modifier
      ↓
FSpellDefinition
      ↓
SpellCreation.StoredGenericSpell
```

Rune Canvas, ready slots and Spell Modifier now all converge on the same
single-spell representation.

### Generic fields used directly

- `Shape`
- `ShapeDefinition`
- `Material`
- `DistanceM`
- `Orientation`
- `Pattern`
- `MotionDirection`
- `SpeedMps`

The Workbench mass readout now uses generic `FSpellShapeMath`.

### Legacy Earth type

`FEarthSpellDefinition` is NOT deleted yet.

It remains as a compatibility adapter/projection for older systems such as the
current preview renderer and any reflected Blueprint callers.

What was removed is the duplicate stored state.

SpellCreation now stores only:

`FSpellDefinition StoredGenericSpell`

### Next

Presentation separation:

- `SpellWorkbenchUI`
- `CodexUI`
- `RuneCanvasUI`

out of the oversized `InnerRealmSubsystem.cpp`.
