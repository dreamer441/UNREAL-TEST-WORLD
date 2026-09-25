$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

$InnerBuild = Join-Path $Root "Plugins\InnerRealm\Source\InnerRealm\InnerRealm.Build.cs"
$InnerPlugin = Join-Path $Root "Plugins\InnerRealm\InnerRealm.uplugin"
$InnerCpp = Join-Path $Root "Plugins\InnerRealm\Source\InnerRealm\Private\InnerRealmSubsystem.cpp"

$PreviewBuild = Join-Path $Root "Plugins\SpellPreview\Source\SpellPreview\SpellPreview.Build.cs"
$PreviewPlugin = Join-Path $Root "Plugins\SpellPreview\SpellPreview.uplugin"
$PreviewHeader = Join-Path $Root "Plugins\SpellPreview\Source\SpellPreview\Public\SpellPreviewSubsystem.h"
$PreviewCpp = Join-Path $Root "Plugins\SpellPreview\Source\SpellPreview\Private\SpellPreviewSubsystem.cpp"

$All = @($InnerBuild,$InnerPlugin,$InnerCpp,$PreviewBuild,$PreviewPlugin,$PreviewHeader,$PreviewCpp)
foreach ($P in $All) {
    if (!(Test-Path $P)) { throw "Missing expected file: $P" }
}

function ReadText([string]$Path) {
    return ([System.IO.File]::ReadAllText($Path) -replace "`r`n","`n")
}
function WriteText([string]$Path,[string]$Text) {
    [System.IO.File]::WriteAllText($Path,$Text,[System.Text.UTF8Encoding]::new($false))
}

Write-Host "Fixing plugin dependency direction..." -ForegroundColor Cyan

# InnerRealm must NOT depend on SpellPreview.
$T = ReadText $InnerBuild
$T = $T.Replace(', "SpellPreview"','')
$T = $T.Replace('"LiveSpellCasting", "SpellPreview"','"LiveSpellCasting"')
WriteText $InnerBuild $T

$T = ReadText $InnerPlugin
$T = $T -replace ',\s*\{\s*"Name"\s*:\s*"SpellPreview"\s*,\s*"Enabled"\s*:\s*true\s*\}', ''
WriteText $InnerPlugin $T

$T = ReadText $InnerCpp
$T = $T.Replace("#include `"SpellPreviewSubsystem.h`"`n","")

$EnableBlock = @'
    if (USpellPreviewSubsystem* Preview = World->GetSubsystem<USpellPreviewSubsystem>())
    {
        Preview->SetWorkbenchPreviewContext(true, Realm->GetPreviewReferenceTransform());
    }

'@
$T = $T.Replace($EnableBlock,"")

$DisableBlock = @'
    if (World)
    {
        if (USpellPreviewSubsystem* Preview = World->GetSubsystem<USpellPreviewSubsystem>())
        {
            Preview->SetWorkbenchPreviewContext(false, FTransform::Identity);
        }
    }

'@
$T = $T.Replace($DisableBlock,"")
WriteText $InnerCpp $T

# SpellPreview observes InnerRealm instead.
$T = ReadText $PreviewBuild
if (!$T.Contains('"InnerRealm"')) {
    $T = $T.Replace('"PlayerViewModes"', '"PlayerViewModes", "InnerRealm"')
}
WriteText $PreviewBuild $T

$T = ReadText $PreviewPlugin
if (!$T.Contains('"Name": "InnerRealm"')) {
    $T = $T.Replace(
        '{ "Name": "PlayerViewModes", "Enabled": true }',
        "{ `"Name`": `"PlayerViewModes`", `"Enabled`": true },`n    { `"Name`": `"InnerRealm`", `"Enabled`": true }"
    )
}
WriteText $PreviewPlugin $T

$Header = @'
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "SpellPreviewSubsystem.generated.h"

/**
 * Shared presentation-only spell preview.
 *
 * Live casting and the meditation Workbench both use this node. It observes
 * spell/realm state and renders it; it never owns or mutates gameplay values.
 */
UCLASS()
class SPELLPREVIEW_API USpellPreviewSubsystem : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual void Tick(float DeltaSeconds) override;
    virtual TStatId GetStatId() const override;
};
'@
WriteText $PreviewHeader $Header

$T = ReadText $PreviewCpp

if (!$T.Contains('#include "InnerRealmActor.h"')) {
    $T = $T.Replace(
        '#include "EarthSpellDefinition.h"',
        "#include `"EarthSpellDefinition.h`"`n#include `"EngineUtils.h`"`n#include `"InnerRealmActor.h`"`n#include `"InnerRealmSubsystem.h`""
    )
}

$SetterPattern = '(?s)void USpellPreviewSubsystem::SetWorkbenchPreviewContext\(\s*const bool bEnabled,\s*const FTransform& ReferenceTransform\)\s*\{\s*bWorkbenchPreviewActive = bEnabled;\s*WorkbenchReferenceTransform = ReferenceTransform;\s*\}\s*'
$T = [regex]::Replace($T,$SetterPattern,'')

$OldStart = @'
    /*
     * Workbench preview.
     *
     * This reads the persistent TAB definition directly from SpellCreation.
     * It deliberately does not touch the live-casting state machine.
     */
    if (bWorkbenchPreviewActive)
    {
        if (const USpellCreationSubsystem* SpellCreation = World->GetSubsystem<USpellCreationSubsystem>())
        {
            const FEarthSpellDefinition Spell = SpellCreation->GetStoredSpellDefinition();

            FVector Forward = WorkbenchReferenceTransform.GetRotation().GetForwardVector();
'@

$NewStart = @'
    /*
     * Workbench preview.
     *
     * SpellPreview OBSERVES InnerRealm instead of InnerRealm calling back into
     * SpellPreview. This preserves one-way module dependencies and avoids a
     * circular plugin graph.
     */
    const UInnerRealmSubsystem* InnerRealm = World->GetSubsystem<UInnerRealmSubsystem>();
    if (InnerRealm && InnerRealm->IsActive())
    {
        const USpellCreationSubsystem* SpellCreation = World->GetSubsystem<USpellCreationSubsystem>();
        AInnerRealmActor* RealmActor = nullptr;
        for (TActorIterator<AInnerRealmActor> It(World); It; ++It)
        {
            RealmActor = *It;
            break;
        }

        if (SpellCreation && RealmActor)
        {
            const FEarthSpellDefinition Spell = SpellCreation->GetStoredSpellDefinition();
            const FTransform WorkbenchReferenceTransform = RealmActor->GetPreviewReferenceTransform();

            FVector Forward = WorkbenchReferenceTransform.GetRotation().GetForwardVector();
'@

if ($T.Contains($OldStart)) {
    $T = $T.Replace($OldStart,$NewStart)
} elseif (!$T.Contains('SpellPreview OBSERVES InnerRealm')) {
    throw "Could not locate Workbench preview block in SpellPreviewSubsystem.cpp"
}

WriteText $PreviewCpp $T

Write-Host ""
Write-Host "Dependency cycle fix applied." -ForegroundColor Green
Write-Host "New direction: SpellPreview -> InnerRealm; InnerRealm does not depend on SpellPreview."
