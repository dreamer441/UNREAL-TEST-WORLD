# AMADEUS v0.13.4.1 — World Codex Compile Fix

The v0.13.4 build failed in the Codex list label because Unreal's checked
`FString::Printf` format string must be a compile-time literal.

This patch splits the selected and unselected labels into two separate
`FString::Printf` calls, each with its own literal format string.

No Codex architecture, spell data, physics, signs, capabilities, or UI layout
is changed.
