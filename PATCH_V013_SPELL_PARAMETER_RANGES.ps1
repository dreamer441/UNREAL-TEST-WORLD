$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$PreviewCpp = Join-Path $Root "Plugins\SpellPreview\Source\SpellPreview\Private\SpellPreviewSubsystem.cpp"

if (!(Test-Path $PreviewCpp)) {
    throw "SpellPreviewSubsystem.cpp not found. Extract this patch into the TESTUNREALPROJECT root."
}

$Text = ([System.IO.File]::ReadAllText($PreviewCpp) -replace "`r`n","`n")

# Desktop GPT's cleanup moved shared spell ranges out of LiveSpellCasting and
# into SpellCreation as SpellParameterRanges.h. Patch 1 was based on the last
# pushed GitHub baseline and accidentally restored the old include/namespace.
$Text = $Text.Replace('#include "LiveSpellRanges.h"', '#include "SpellParameterRanges.h"')
$Text = $Text.Replace('LiveSpellRanges::', 'SpellParameterRanges::')

if ($Text.Contains('LiveSpellRanges')) {
    throw "A LiveSpellRanges reference remains after patching. Please send the current SpellPreviewSubsystem.cpp."
}

[System.IO.File]::WriteAllText(
    $PreviewCpp,
    $Text,
    [System.Text.UTF8Encoding]::new($false)
)

Write-Host "SpellPreview updated to the cleaned SpellParameterRanges API." -ForegroundColor Green
