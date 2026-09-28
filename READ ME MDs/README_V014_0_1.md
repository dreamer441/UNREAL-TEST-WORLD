# AMADEUS v0.14.0.1 — Rune Canvas Input Fix

## Root cause

The Rune Canvas itself was built correctly, but the existing 3D Preview widget
is added to the viewport at a higher Z-order than the Canvas.

For v0.14.0 we intentionally made that Preview visible on both:

- SPELL MODIFIER
- RUNE CANVAS

Its root Slate widget spans the viewport for alignment. With normal `Visible`
hit testing, that display-only overlay could sit in the mouse hit-test path
above the Canvas and prevent the Canvas buttons from receiving clicks.

## Fix

When visible, the Preview root now uses:

`EVisibility::HitTestInvisible`

instead of:

`EVisibility::Visible`

The preview still renders normally, but mouse input passes through it to the
Rune Canvas underneath.

No SpellGraph, compiler, Codex, spell values, physics, or execution logic is
changed.
