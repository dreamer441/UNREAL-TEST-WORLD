# AMADEUS Gameplay v0.13.1.1 — Ready Slots + Orientation

This replaces the broken v0.13.1.0 patch script.

The previous ZIP failed before changing source because its PowerShell file used
C-style `\"` escaping. This version uses a Python patcher and targets the actual
cleanup architecture, where `SpellExecution` owns production SPACE casting.

## Ready slots
- 10 boxes: 1 2 3 4 5 6 7 8 9 0
- click a box in TAB to save the current complete generic spell
- saved box shows `*`
- press that number in gameplay to load it
- SPACE casts through the existing execution path

## Orientation
- Forward / X
- Right / Y
- Up / Z

Orientation is generic spell data, survives the legacy compatibility adapter,
changes Workbench preview, and changes actual spawn orientation.

Default is Up / Z to preserve current behavior.

Extract into `D:\TESTUNREALPROJECT\` and run:
`APPLY_BUILD_AND_OPEN_V013_1_1.bat`
