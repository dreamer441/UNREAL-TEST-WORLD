# AMADEUS Gameplay v0.15.3
## Rune Canvas — Manual Branches + Category Palette

Requires working **v0.15.2 Presentation Split**.

This update intentionally changes only Rune Canvas interaction.

## 1. No automatic new lines

Old behavior:

```text
double-click node
      ↓
empty line
      ↓
attach Sign
      ↓
another empty line appears automatically
```

New behavior:

```text
double-click node
      ↓
ONE empty line
      ↓
attach Sign
      ↓
line is consumed
      ↓
nothing else appears

double-click again
      ↓
next empty line
```

So the Canvas never creates a new attachment line simply because the previous
one was filled.

## 2. Category-first Sign selection

The Canvas palette is no longer a long direct list of Signs.

Selection is now:

```text
CATEGORY
   ↓
SIGN
```

Example:

```text
SHAPE PARAMETERS
      ↓
Cube X
Cube Y
Cube Z
```

For the active Shape, Shape Parameters are filtered:

- Sphere -> Sphere Radius
- Cube -> Cube X / Cube Y / Cube Z
- Cone -> Cone Radius / Cone Height

## Architecture rule

Categories are **not** spell graph nodes.

They are only UI/navigation folders for finding Signs.

That means:

```text
Earth + Cube
      |
    Cube X
      |
  Magnitude
```

remains the semantic graph.

We do not pollute it with:

```text
Earth + Cube
      |
[Shape Parameters category]
      |
    Cube X
```

because "Shape Parameters" is organizational metadata, not a magical operation.
