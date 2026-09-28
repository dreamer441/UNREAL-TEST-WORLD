# AMADEUS v0.13.0.3 — Current Cleanup Branch Compatibility

Authoritative base inspected:
`codex/unreal-architecture-cleanup @ 960313be12c4b0206865ac728ad93f3a2393c3f8`

This patch is intentionally small. It does not reapply old GitHub-baseline code.

## Why it is needed

The partial Desktop GPT cleanup changed `FSpellCastPlacement::Resolve(...)` to accept:

`const FResolvedSpell&`

The Workbench/live preview patch was still passing:

`FEarthSpellDefinition`

The preview now:
1. resolves the canonical `FResolvedSpell` through `ResolveGenericSpell()`;
2. passes that generic result into SpellExecution placement;
3. converts the resolved definition through the explicit legacy adapter only for the existing preview drawing functions.

This preserves the cleanup boundary:

`LiveSpellCasting -> FResolvedSpell -> SpellExecution placement`

while allowing the current Earth-specific visual renderer to remain unchanged for Patch 1.

## Install

Extract into `D:\TESTUNREALPROJECT\` and run:

`APPLY_BUILD_AND_OPEN_V013_0_3.bat`

Unlike the earlier scripts, this one runs the UE 5.8 build directly and only opens Unreal if compilation succeeds.
