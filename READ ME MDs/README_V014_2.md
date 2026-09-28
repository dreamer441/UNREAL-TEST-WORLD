# AMADEUS Gameplay v0.14.2
## Radial Rune Canvas + Ready-Slot Fix

### Spell Modifier ready-slot fix

The Spell Modifier editor root is a full-screen alignment widget at a higher
viewport Z-order than the preview. Its visible editor panel is only on the left,
but normal hit testing on the root could still block the ready-slot buttons on
the right.

The editor root is now `SelfHitTestInvisible` while active:

- editor sliders and buttons remain interactive;
- empty editor-root space no longer blocks the preview;
- ready-spell number slots can receive clicks again.

### Larger Canvas

The Rune Canvas is now 1700 x 920 and intentionally sits above the reference
preview/model. The top TAB navigation remains above the Canvas.

### Element + Shape = one visual node

The semantic compiler still stores:

`Earth -> Shape`

but the Canvas visually merges them into one central construction node.

Start:

1. choose Earth;
2. choose Sphere / Cube / Cone;
3. one central node appears containing only the two Signs.

Changing Shape later replaces only the Shape portion of that construction.

### Double-click radial expansion

A node initially has no empty line.

Double-click a non-terminal node to open one attachment branch.

Branch direction order begins:

1. Down
2. Up
3. Left
4. Right
5. Down-left
6. Down-right
7. Up-left
8. Up-right
9. additional in-between radial directions

When a branch is filled, another empty branch remains available around that
same expanded node.

For a Tier-II node, the side already occupied by its incoming parent connection
is skipped so new branches do not immediately run back through the existing
line.

Tier III signs remain terminal and never receive outgoing branches.

### Graph labels

The graph itself displays Signs only.

Names and descriptions remain in the Codex palette and tooltips.

### Note

This is still a layout experiment. The radial line renderer is intentionally
lightweight so the spatial grammar can be tested before building a custom
painted graph widget.
