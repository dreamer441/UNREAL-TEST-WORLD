$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$PreviewCpp = Join-Path $Root "Plugins\SpellPreview\Source\SpellPreview\Private\SpellPreviewSubsystem.cpp"
$Ranges = Join-Path $Root "Plugins\SpellCreation\Source\SpellCreation\Public\SpellParameterRanges.h"
$SpellDef = Join-Path $Root "Plugins\SpellCreation\Source\SpellCreation\Public\SpellDefinition.h"
$Placement = Join-Path $Root "Plugins\SpellExecution\Source\SpellExecution\Public\SpellCastPlacement.h"

foreach ($Path in @($PreviewCpp, $Ranges, $SpellDef, $Placement)) {
    if (!(Test-Path $Path)) {
        throw "Expected current cleanup-branch file is missing: $Path"
    }
}

function Read-Normalized([string]$Path) {
    return ([System.IO.File]::ReadAllText($Path) -replace "`r`n", "`n")
}

function Write-Utf8([string]$Path, [string]$Text) {
    [System.IO.File]::WriteAllText($Path, $Text, [System.Text.UTF8Encoding]::new($false))
}

$Text = Read-Normalized $PreviewCpp

# Sanity: this patch is specifically for the cleaned architecture.
if (!$Text.Contains('#include "SpellParameterRanges.h"')) {
    throw "SpellPreview is not on the expected cleaned API (SpellParameterRanges.h missing)."
}
if (!$Text.Contains('#include "SpellCastPlacement.h"')) {
    throw "SpellPreview does not use current SpellExecution placement API."
}

# Explicitly include the generic spell contract used by the adapter/result.
if (!$Text.Contains('#include "SpellDefinition.h"')) {
    $Text = $Text.Replace(
        '#include "SpellCastPlacement.h"',
        "#include `"SpellCastPlacement.h`"`n#include `"SpellDefinition.h`""
    )
}

$OldResolve = '    const FEarthSpellDefinition Spell = Session->ResolveSpell();'
$NewResolve = @'
    // The cleanup architecture made SpellExecution consume FResolvedSpell.
    // Keep the preview renderer on the legacy visual adapter for now, but pass
    // the canonical generic resolved spell into placement.
    const FResolvedSpell ResolvedSpell = Session->ResolveGenericSpell();
    const FEarthSpellDefinition Spell =
        FSpellDefinitionAdapter::ToLegacyEarth(ResolvedSpell.Definition);
'@

if ($Text.Contains($OldResolve)) {
    $Text = $Text.Replace($OldResolve, $NewResolve)
} elseif (!$Text.Contains('const FResolvedSpell ResolvedSpell = Session->ResolveGenericSpell();')) {
    throw "Could not find the expected live preview resolve line."
}

$OldPlacement = '    if (!FSpellCastPlacement::Resolve(PC, Spell, AimDirection, Placement))'
$NewPlacement = '    if (!FSpellCastPlacement::Resolve(PC, ResolvedSpell, AimDirection, Placement))'

if ($Text.Contains($OldPlacement)) {
    $Text = $Text.Replace($OldPlacement, $NewPlacement)
} elseif (!$Text.Contains('FSpellCastPlacement::Resolve(PC, ResolvedSpell, AimDirection, Placement)')) {
    throw "Could not find the expected SpellCastPlacement call."
}

# Fail if the obsolete signature survived in this file.
if ($Text.Contains('FSpellCastPlacement::Resolve(PC, Spell, AimDirection, Placement)')) {
    throw "Old FEarthSpellDefinition placement call still remains."
}

Write-Utf8 $PreviewCpp $Text

Write-Host ""
Write-Host "Current-branch SpellPreview compatibility patch applied." -ForegroundColor Green
Write-Host "Live preview now resolves canonical FResolvedSpell for SpellExecution placement."
