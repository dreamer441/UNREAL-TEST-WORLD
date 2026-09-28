# AMADEUS v0.13.2.1 — Slate Visibility Fix

The v0.13.2 data/pattern patch applied successfully. The compile failure is
isolated to the new InnerRealm Slate UI.

`SVerticalBox::Slot()` does not expose `.Visibility_Lambda(...)`.
Visibility must be applied to a child widget.

This patch changes the six conditional MULTIPLE OBJECTS rows to wrap their
contents in `SBox` and puts `.Visibility_Lambda(...)` on that `SBox`.

No Pattern data, resolver, casting, ready slots, orientation, preview logic, or
physics behavior is changed.

Extract over the existing project and run:

`APPLY_BUILD_AND_OPEN_V013_2_1.bat`
