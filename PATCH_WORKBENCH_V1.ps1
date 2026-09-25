$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Header = Join-Path $Root "Plugins\InnerRealm\Source\InnerRealm\Public\InnerRealmSubsystem.h"
$Cpp = Join-Path $Root "Plugins\InnerRealm\Source\InnerRealm\Private\InnerRealmSubsystem.cpp"

if (!(Test-Path $Header) -or !(Test-Path $Cpp)) {
    throw "Patch 1 must be extracted into the TESTUNREALPROJECT root."
}

function Read-Normalized([string]$Path) {
    return ([System.IO.File]::ReadAllText($Path) -replace "`r`n", "`n")
}

function Write-Utf8([string]$Path, [string]$Text) {
    [System.IO.File]::WriteAllText($Path, $Text, [System.Text.UTF8Encoding]::new($false))
}

function Replace-Required([string]$Text, [string]$Old, [string]$New, [string]$Label) {
    if ($Text.Contains($New)) {
        return $Text
    }
    if (!$Text.Contains($Old)) {
        throw "Could not find expected source block for: $Label"
    }
    return $Text.Replace($Old, $New)
}

# --- Header: store the separate transparent preview frame widget.
$H = Read-Normalized $Header
$H = Replace-Required $H `
    "    TSharedPtr<SWidget> EditorWidget;" `
    "    TSharedPtr<SWidget> EditorWidget;`n    TSharedPtr<SWidget> PreviewFrameWidget;" `
    "PreviewFrameWidget member"
Write-Utf8 $Header $H

# --- CPP
$C = Read-Normalized $Cpp

$C = Replace-Required $C `
    '#include "SpellCreationSubsystem.h"' `
    "#include `"SpellCreationSubsystem.h`"`n#include `"SpellPreviewSubsystem.h`"" `
    "SpellPreview include"

# Enable shared Workbench preview when the meditation scene has been positioned.
$OldEnter = @'
    PositionRealmNearPlayer(Realm, PC);
    ApplyPlayerInputState(true);
'@
$NewEnter = @'
    PositionRealmNearPlayer(Realm, PC);

    if (USpellPreviewSubsystem* Preview = World->GetSubsystem<USpellPreviewSubsystem>())
    {
        Preview->SetWorkbenchPreviewContext(true, Realm->GetPreviewReferenceTransform());
    }

    ApplyPlayerInputState(true);
'@
$C = Replace-Required $C $OldEnter $NewEnter "Workbench preview enable"

# Disable the preview before returning to the outer world.
$OldExit = @'
    APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;

    RemoveEditorWidget();
'@
$NewExit = @'
    APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;

    if (World)
    {
        if (USpellPreviewSubsystem* Preview = World->GetSubsystem<USpellPreviewSubsystem>())
        {
            Preview->SetWorkbenchPreviewContext(false, FTransform::Identity);
        }
    }

    RemoveEditorWidget();
'@
$C = Replace-Required $C $OldExit $NewExit "Workbench preview disable"

# Move the existing editor to the left so the world-backed preview has room.
$C = Replace-Required $C `
    "    EditorWidget = SNew(SBox)`n        .HAlign(HAlign_Center)" `
    "    EditorWidget = SNew(SBox)`n        .HAlign(HAlign_Left)" `
    "Workbench editor left alignment"

# Add a transparent right-hand frame. The actual mannequin and spell are in the
# Inner Realm world behind this Slate frame, so the same SpellPreview node is
# used instead of duplicating a second rendering implementation.
$OldAdd = '    GEngine->GameViewport->AddViewportWidgetContent(EditorWidget.ToSharedRef(), 5000);'
$NewAdd = @'
    GEngine->GameViewport->AddViewportWidgetContent(EditorWidget.ToSharedRef(), 5000);

    PreviewFrameWidget = SNew(SBox)
        .HAlign(HAlign_Right)
        .VAlign(VAlign_Center)
        [
            SNew(SBox)
            .WidthOverride(520.0f)
            .HeightOverride(760.0f)
            [
                SNew(SBorder)
                .Padding(FMargin(16.0f))
                .BorderBackgroundColor(FLinearColor(0.05f, 0.08f, 0.05f, 0.12f))
                [
                    SNew(SVerticalBox)

                    + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0, 0, 0, 8)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(FSlateColor(FLinearColor(0.86f, 0.96f, 0.87f, 1.0f)))
                        .Text(FText::FromString(TEXT("SPELL WORKBENCH / 3D PREVIEW")))
                    ]

                    + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(FSlateColor(FLinearColor(0.72f, 0.88f, 0.74f, 1.0f)))
                        .Text_Lambda([this]() { return GetCurrentSpellSummary(); })
                    ]

                    + SVerticalBox::Slot().FillHeight(1.0f)
                    [
                        SNew(SBox)
                    ]

                    + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0, 8, 0, 0)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(FSlateColor(FLinearColor(0.78f, 0.90f, 0.80f, 1.0f)))
                        .Text(FText::FromString(TEXT("Reference mannequin shows spell scale, distance, density grid and speed rings.")))
                    ]
                ]
            ]
        ];

    GEngine->GameViewport->AddViewportWidgetContent(PreviewFrameWidget.ToSharedRef(), 4999);
'@
$C = Replace-Required $C $OldAdd $NewAdd "Workbench preview frame"

# Remove the second widget on exit.
$OldRemove = @'
    if (EditorWidget.IsValid() && GEngine && GEngine->GameViewport)
    {
        GEngine->GameViewport->RemoveViewportWidgetContent(EditorWidget.ToSharedRef());
    }
    EditorWidget.Reset();
'@
$NewRemove = @'
    if (EditorWidget.IsValid() && GEngine && GEngine->GameViewport)
    {
        GEngine->GameViewport->RemoveViewportWidgetContent(EditorWidget.ToSharedRef());
    }
    if (PreviewFrameWidget.IsValid() && GEngine && GEngine->GameViewport)
    {
        GEngine->GameViewport->RemoveViewportWidgetContent(PreviewFrameWidget.ToSharedRef());
    }

    EditorWidget.Reset();
    PreviewFrameWidget.Reset();
'@
$C = Replace-Required $C $OldRemove $NewRemove "Workbench preview frame removal"

Write-Utf8 $Cpp $C

Write-Host ""
Write-Host "Patch 1 source integration complete." -ForegroundColor Green
Write-Host "InnerRealm now hosts the Workbench frame and reference mannequin."
Write-Host "SpellPreview now renders both live casting and persistent Workbench definitions."
