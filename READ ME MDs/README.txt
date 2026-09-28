AMADEUS Runtime Compile Fix 2

Problem:
Unreal Engine 5.8 cannot find:
    Widgets/Layout/SVerticalBox.h

Fix:
Replace it with:
    Widgets/SBoxPanel.h

SVerticalBox is declared through SBoxPanel in UE5.

This patch only edits:
D:\TESTUNREALPROJECT\Plugins\AmadeusRuntime\Source\AmadeusRuntime\Private\AmadeusInteractionSubsystem.cpp

It backs up the original file before editing and clears only generated AmadeusRuntime build products plus project build-rule intermediates.
