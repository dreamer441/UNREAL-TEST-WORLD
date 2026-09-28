# AMADEUS v0.14.1 — Rune Graph Redesign

This patch addresses both issues found after Rune Canvas V1.

## 1. Ready-spell slot interaction

v0.14.0.1 changed the preview overlay to `HitTestInvisible` so the full-screen
preview alignment widget would stop swallowing Canvas clicks.

That also made every child of the preview non-interactive, including the ready
spell slot buttons.

v0.14.1 changes the preview root to:

`EVisibility::SelfHitTestInvisible`

Meaning:

- the full-screen preview root itself does not catch Canvas clicks;
- child controls such as ready-slot buttons remain clickable.

So a Canvas-compiled spell can again be saved into the existing number slots.

## 2. Graph redesign

The sentence/list graph is replaced by a branching sign graph.

### Nodes

Inside the graph, a component displays only its Sign.

Names and descriptions remain in:

- the Codex palette;
- tooltips;
- the selected-parent status text.

### Branching rule

Every Tier I and Tier II node always has one outgoing line with an empty
attachment socket.

When a child is attached, that child becomes a real branch and a fresh empty
socket remains available next to it.

Conceptually:

        [E]
         |
      +--+--+
      |     |
     [O]    o
      |
    +-+-+
    |   |
   [rO] o
    |
   [IV]

`o` = empty attachment socket.

### Tier III

Tier III is terminal.

It has:

- no outgoing line;
- no empty child socket;
- no children.

### Interaction

1. Click a Sign node or its empty socket.
2. It becomes the current attachment parent.
3. Click a Sign in the left Codex palette.
4. The new concept attaches as a child branch.
5. The graph redraws with another empty socket.

The compiler and semantic graph data are unchanged. This is a presentation and
interaction redesign, not a second graph model.
