$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

$SpellDef = Join-Path $Root "Plugins\SpellCreation\Source\SpellCreation\Public\SpellDefinition.h"
$LiveHeader = Join-Path $Root "Plugins\LiveSpellCasting\Source\LiveSpellCasting\Public\LiveSpellSessionSubsystem.h"
$LiveCpp = Join-Path $Root "Plugins\LiveSpellCasting\Source\LiveSpellCasting\Private\LiveSpellSessionSubsystem.cpp"
$InnerCpp = Join-Path $Root "Plugins\InnerRealm\Source\InnerRealm\Private\InnerRealmSubsystem.cpp"
$InnerBuild = Join-Path $Root "Plugins\InnerRealm\Source\InnerRealm\InnerRealm.Build.cs"
$InnerPlugin = Join-Path $Root "Plugins\InnerRealm\InnerRealm.uplugin"
$EarthCpp = Join-Path $Root "Plugins\EarthTestHarness\Source\EarthTestHarness\Private\EarthTestInputSubsystem.cpp"
$EarthBuild = Join-Path $Root "Plugins\EarthTestHarness\Source\EarthTestHarness\EarthTestHarness.Build.cs"
$EarthPlugin = Join-Path $Root "Plugins\EarthTestHarness\EarthTestHarness.uplugin"
$PreviewCpp = Join-Path $Root "Plugins\SpellPreview\Source\SpellPreview\Private\SpellPreviewSubsystem.cpp"

foreach ($Path in @($SpellDef,$LiveHeader,$LiveCpp,$InnerCpp,$InnerBuild,$InnerPlugin,$EarthCpp,$EarthBuild,$EarthPlugin,$PreviewCpp)) {
    if (!(Test-Path $Path)) {
        throw "Expected file missing: $Path"
    }
}

function Read-Normalized([string]$Path) {
    return ([System.IO.File]::ReadAllText($Path) -replace "`r`n", "`n")
}

function Write-Utf8([string]$Path, [string]$Text) {
    [System.IO.File]::WriteAllText($Path, $Text, [System.Text.UTF8Encoding]::new($false))
}

function Ensure-Contains([string]$Text, [string]$Needle, [string]$Label) {
    if (!$Text.Contains($Needle)) {
        throw "Expected content not found for: $Label"
    }
}

function Add-BuildDependency([string]$Path, [string]$ModuleName) {
    $Text = Read-Normalized $Path
    if ($Text.Contains('"' + $ModuleName + '"')) {
        return
    }
    $Text = $Text.Replace('"SpellPreview"', '"SpellPreview", "' + $ModuleName + '"')
    $Text = $Text.Replace('"LiveSpellCasting"', '"LiveSpellCasting", "' + $ModuleName + '"')
    $Text = $Text.Replace('"SpellCreation"', '"SpellCreation", "' + $ModuleName + '"')
    Write-Utf8 $Path $Text
}

function Add-PluginDependency([string]$Path, [string]$PluginName) {
    $Text = Read-Normalized $Path
    if ($Text.Contains('"Name": "' + $PluginName + '"')) {
        return
    }

    if ($Text.Contains('"Plugins": [')) {
        $Text = $Text.Replace('"Plugins": [', '"Plugins": [' + "`n    { \"Name\": \"$PluginName\", \"Enabled\": true },")
    } else {
        $Text = $Text.TrimEnd()
        if ($Text.EndsWith("}")) {
            $Text = $Text.Substring(0, $Text.Length - 1).TrimEnd()
            if ($Text.EndsWith(',')) {
                $Text += "`n  \"Plugins\": [ { \"Name\": \"$PluginName\", \"Enabled\": true } ]`n}"
            } else {
                $Text += ",`n  \"Plugins\": [ { \"Name\": \"$PluginName\", \"Enabled\": true } ]`n}"
            }
        }
    }
    Write-Utf8 $Path $Text
}

Write-Host "Patching build/plugin dependencies..." -ForegroundColor Cyan
Add-BuildDependency $InnerBuild "SpellLoadout"
Add-BuildDependency $EarthBuild "SpellLoadout"
Add-PluginDependency $InnerPlugin "SpellLoadout"
Add-PluginDependency $EarthPlugin "SpellLoadout"

# -----------------------------------------------------------------------------
# SpellDefinition.h : add orientation enum + property.
# -----------------------------------------------------------------------------
Write-Host "Patching SpellDefinition orientation field..." -ForegroundColor Cyan
$T = Read-Normalized $SpellDef

if (!$T.Contains('EEarthSpellOrientationAxis')) {
    $Marker = @'
UENUM(BlueprintType)
enum class EEarthSpellShape : uint8
{
    Sphere UMETA(DisplayName="Sphere"),
    Cube   UMETA(DisplayName="Cube"),
    Cone   UMETA(DisplayName="Cone")
};
'@
    $Insert = @'
UENUM(BlueprintType)
enum class EEarthSpellShape : uint8
{
    Sphere UMETA(DisplayName="Sphere"),
    Cube   UMETA(DisplayName="Cube"),
    Cone   UMETA(DisplayName="Cone")
};

UENUM(BlueprintType)
enum class EEarthSpellOrientationAxis : uint8
{
    Forward UMETA(DisplayName="Forward / X"),
    Right   UMETA(DisplayName="Right / Y"),
    Up      UMETA(DisplayName="Up / Z")
};
'@
    if ($T.Contains($Marker)) {
        $T = $T.Replace($Marker, $Insert)
    } else {
        throw "Could not locate shape enum block in SpellDefinition.h"
    }
}

if (!$T.Contains('Orientation = EEarthSpellOrientationAxis::Up')) {
    $DistanceLine = '    float DistanceM = 3.0f;'
    $OrientationProperty = @'
    float DistanceM = 3.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Spatial")
    EEarthSpellOrientationAxis Orientation = EEarthSpellOrientationAxis::Up;
'@
    if ($T.Contains($DistanceLine)) {
        $T = $T.Replace($DistanceLine, $OrientationProperty)
    } else {
        throw "Could not locate DistanceM property in SpellDefinition.h"
    }
}
Write-Utf8 $SpellDef $T

# -----------------------------------------------------------------------------
# LiveSpellSessionSubsystem : add prepared-spell import.
# -----------------------------------------------------------------------------
Write-Host "Patching LiveSpellSessionSubsystem prepared load..." -ForegroundColor Cyan
$T = Read-Normalized $LiveHeader
if (!$T.Contains('LoadPreparedSpell')) {
    $Needle = '    void SelectShape(EEarthSpellShape Shape);'
    Ensure-Contains $T $Needle 'SelectShape declaration'
    $T = $T.Replace($Needle, $Needle + "`n    void LoadPreparedSpell(const FEarthSpellDefinition& Spell);")
    Write-Utf8 $LiveHeader $T
}

$T = Read-Normalized $LiveCpp
if (!$T.Contains('void ULiveSpellSessionSubsystem::LoadPreparedSpell')) {
    $InsertAfter = @'
void ULiveSpellSessionSubsystem::SelectShape(const EEarthSpellShape Shape)
{
    ShapeOverride = Shape;
    bHasShapeOverride = true;
    bHasConstruction = true;
}
'@
    Ensure-Contains $T $InsertAfter 'SelectShape implementation'
    $LoadPrepared = @'
void ULiveSpellSessionSubsystem::LoadPreparedSpell(const FEarthSpellDefinition& Spell)
{
    ResetSession();

    bEarthExplicitlySelected = true;
    bHasConstruction = true;
    bHasShapeOverride = true;
    ShapeOverride = Spell.Shape;

    auto AddNormalized = [this](const ELiveSpellParameter Parameter, const float Value, const float MinValue, const float MaxValue)
    {
        ParameterOverrides01.Add(Parameter, SpellParameterRanges::Normalize(Value, MinValue, MaxValue));
    };

    switch (Spell.Shape)
    {
        case EEarthSpellShape::Sphere:
            AddNormalized(ELiveSpellParameter::SphereRadius, Spell.SphereRadiusCm, SpellParameterRanges::MinSphereRadiusCm, SpellParameterRanges::MaxSphereRadiusCm);
            break;

        case EEarthSpellShape::Cube:
            AddNormalized(ELiveSpellParameter::CubeX, Spell.CubeXcm, SpellParameterRanges::MinCubeSideCm, SpellParameterRanges::MaxCubeSideCm);
            AddNormalized(ELiveSpellParameter::CubeY, Spell.CubeYcm, SpellParameterRanges::MinCubeSideCm, SpellParameterRanges::MaxCubeSideCm);
            AddNormalized(ELiveSpellParameter::CubeZ, Spell.CubeZcm, SpellParameterRanges::MinCubeSideCm, SpellParameterRanges::MaxCubeSideCm);
            break;

        case EEarthSpellShape::Cone:
        default:
            AddNormalized(ELiveSpellParameter::ConeRadius, Spell.ConeRadiusCm, SpellParameterRanges::MinConeRadiusCm, SpellParameterRanges::MaxConeRadiusCm);
            AddNormalized(ELiveSpellParameter::ConeHeight, Spell.ConeHeightCm, SpellParameterRanges::MinConeHeightCm, SpellParameterRanges::MaxConeHeightCm);
            break;
    }

    AddNormalized(ELiveSpellParameter::Speed, Spell.SpeedMps, SpellParameterRanges::MinSpeedMps, SpellParameterRanges::MaxSpeedMps);
    AddNormalized(ELiveSpellParameter::Density, Spell.DensityKgPerM3, SpellParameterRanges::MinDensityKgPerM3, SpellParameterRanges::MaxDensityKgPerM3);
    AddNormalized(ELiveSpellParameter::Distance, Spell.DistanceM, SpellParameterRanges::MinDistanceM, SpellParameterRanges::MaxDistanceM);

    ParameterOverrides01.Add(ELiveSpellParameter::Hardness, FMath::Clamp(Spell.Hardness, 0.0f, 1.0f));
    ParameterOverrides01.Add(ELiveSpellParameter::Toughness, FMath::Clamp(Spell.Toughness, 0.0f, 1.0f));
    ParameterOverrides01.Add(ELiveSpellParameter::Elasticity, FMath::Clamp(Spell.Elasticity, 0.0f, 1.0f));

    ++Generation;
}
'@
    $T = $T.Replace($InsertAfter, $InsertAfter + "`n" + $LoadPrepared)
    $T = $T.Replace('#include "SpellCreationSubsystem.h"', '#include "SpellCreationSubsystem.h"`n#include "SpellParameterRanges.h"')
    Write-Utf8 $LiveCpp $T
}

# -----------------------------------------------------------------------------
# EarthTestInputSubsystem : number keys load prepared slots.
# -----------------------------------------------------------------------------
Write-Host "Patching EarthTestInputSubsystem number-key loadouts..." -ForegroundColor Cyan
$T = Read-Normalized $EarthCpp
if (!$T.Contains('#include "SpellLoadoutSubsystem.h"')) {
    $T = $T.Replace('#include "PlayerViewModeSubsystem.h"', '#include "PlayerViewModeSubsystem.h"`n#include "SpellLoadoutSubsystem.h"')
}

if (!$T.Contains('Prepared spell slot hotkeys')) {
    $OldTickBlock = @'
    if (PC->WasInputKeyJustPressed(EKeys::SpaceBar))
    {
        ExecuteLiveEarthSpell();
    }
'@
    $NewTickBlock = @'
    // Prepared spell slot hotkeys.
    struct FLoadoutKeyPair { FKey Key; int32 SlotIndex; };
    static const FLoadoutKeyPair LoadoutKeys[] =
    {
        { EKeys::One,   0 },
        { EKeys::Two,   1 },
        { EKeys::Three, 2 },
        { EKeys::Four,  3 },
        { EKeys::Five,  4 },
        { EKeys::Six,   5 },
        { EKeys::Seven, 6 },
        { EKeys::Eight, 7 },
        { EKeys::Nine,  8 },
        { EKeys::Zero,  9 }
    };

    if (ULiveSpellSessionSubsystem* LiveSession = World->GetSubsystem<ULiveSpellSessionSubsystem>())
    {
        if (USpellLoadoutSubsystem* Loadout = World->GetSubsystem<USpellLoadoutSubsystem>())
        {
            for (const FLoadoutKeyPair& Pair : LoadoutKeys)
            {
                if (PC->WasInputKeyJustPressed(Pair.Key))
                {
                    FEarthSpellDefinition PreparedSpell;
                    if (Loadout->GetSlotSpell(Pair.SlotIndex, PreparedSpell))
                    {
                        Loadout->EquipSlot(Pair.SlotIndex);
                        LiveSession->LoadPreparedSpell(PreparedSpell);
                        if (GEngine)
                        {
                            GEngine->AddOnScreenDebugMessage(-1, 1.0f, FColor::Green,
                                FString::Printf(TEXT("Prepared spell slot %d loaded."), Pair.SlotIndex == 9 ? 0 : Pair.SlotIndex + 1));
                        }
                    }
                }
            }
        }
    }

    if (PC->WasInputKeyJustPressed(EKeys::SpaceBar))
    {
        ExecuteLiveEarthSpell();
    }
'@
    Ensure-Contains $T $OldTickBlock 'SpaceBar tick block'
    $T = $T.Replace($OldTickBlock, $NewTickBlock)
}
Write-Utf8 $EarthCpp $T

# -----------------------------------------------------------------------------
# InnerRealmSubsystem : orientation row + slot buttons + summary.
# -----------------------------------------------------------------------------
Write-Host "Patching InnerRealmSubsystem workbench UI..." -ForegroundColor Cyan
$T = Read-Normalized $InnerCpp
if (!$T.Contains('#include "SpellLoadoutSubsystem.h"')) {
    $T = $T.Replace('#include "SpellCastingBindingSubsystem.h"', '#include "SpellCastingBindingSubsystem.h"`n#include "SpellLoadoutSubsystem.h"')
}

# Summary string.
$OldSummary = @'
FText UInnerRealmSubsystem::GetCurrentSpellSummary() const
{
    const FEarthSpellDefinition Spell = ReadSpell();
    return FText::FromString(FString::Printf(
        TEXT("EARTH / %s   |   speed %.0f m/s   |   density %.0f kg/m3   |   mass %.0f kg   |   distance %.1f m"),
        *GetShapeName().ToString(),
        Spell.SpeedMps,
        Spell.DensityKgPerM3,
        UEarthSpellMath::CalculateMassKg(Spell),
        Spell.DistanceM));
}
'@
$NewSummary = @'
FText UInnerRealmSubsystem::GetCurrentSpellSummary() const
{
    const FEarthSpellDefinition Spell = ReadSpell();

    FString OrientationText = TEXT("UP / Z");
    switch (Spell.Orientation)
    {
        case EEarthSpellOrientationAxis::Forward: OrientationText = TEXT("FORWARD / X"); break;
        case EEarthSpellOrientationAxis::Right:   OrientationText = TEXT("RIGHT / Y"); break;
        case EEarthSpellOrientationAxis::Up:
        default:                                  OrientationText = TEXT("UP / Z"); break;
    }

    return FText::FromString(FString::Printf(
        TEXT("EARTH / %s / %s   |   speed %.0f m/s   |   density %.0f kg/m3   |   mass %.0f kg   |   distance %.1f m"),
        *GetShapeName().ToString(),
        *OrientationText,
        Spell.SpeedMps,
        Spell.DensityKgPerM3,
        UEarthSpellMath::CalculateMassKg(Spell),
        Spell.DistanceM));
}
'@
if ($T.Contains($OldSummary)) {
    $T = $T.Replace($OldSummary, $NewSummary)
}

# Orientation row inserted after SHAPE controls.
if (!$T.Contains('Section(TEXT("ORIENTATION"))')) {
    $OldShapeBlock = @'
                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
                        [ Section(TEXT("SIZE / SHAPE DIMENSIONS")) ]
'@
    $NewShapeBlock = @'
                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
                        [ Section(TEXT("ORIENTATION")) ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0, 4, 0, 4)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().Padding(0,0,14,0)
                            [
                                SNew(SButton)
                                .Text(FText::FromString(TEXT("Forward / X")))
                                .OnClicked_Lambda([this]()
                                {
                                    FEarthSpellDefinition Spell = ReadSpell();
                                    Spell.Orientation = EEarthSpellOrientationAxis::Forward;
                                    WriteSpell(Spell);
                                    return FReply::Handled();
                                })
                            ]
                            + SHorizontalBox::Slot().AutoWidth().Padding(0,0,14,0)
                            [
                                SNew(SButton)
                                .Text(FText::FromString(TEXT("Right / Y")))
                                .OnClicked_Lambda([this]()
                                {
                                    FEarthSpellDefinition Spell = ReadSpell();
                                    Spell.Orientation = EEarthSpellOrientationAxis::Right;
                                    WriteSpell(Spell);
                                    return FReply::Handled();
                                })
                            ]
                            + SHorizontalBox::Slot().AutoWidth()
                            [
                                SNew(SButton)
                                .Text(FText::FromString(TEXT("Up / Z")))
                                .OnClicked_Lambda([this]()
                                {
                                    FEarthSpellDefinition Spell = ReadSpell();
                                    Spell.Orientation = EEarthSpellOrientationAxis::Up;
                                    WriteSpell(Spell);
                                    return FReply::Handled();
                                })
                            ]
                        ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
                        [ Section(TEXT("SIZE / SHAPE DIMENSIONS")) ]
'@
    Ensure-Contains $T $OldShapeBlock 'Shape-to-size transition block'
    $T = $T.Replace($OldShapeBlock, $NewShapeBlock)
}

# Slot row inserted into right-side preview frame.
if (!$T.Contains('Click a slot to save the current spell')) {
    $OldPreviewTitleToSummary = @'
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
'@
    $NewPreviewTitleToSummary = @'
                    + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0, 0, 0, 8)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(FSlateColor(FLinearColor(0.86f, 0.96f, 0.87f, 1.0f)))
                        .Text(FText::FromString(TEXT("SPELL WORKBENCH / 3D PREVIEW")))
                    ]

                    + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0, 0, 0, 6)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(FSlateColor(FLinearColor(0.78f, 0.92f, 0.80f, 1.0f)))
                        .Text(FText::FromString(TEXT("Click a slot to save the current spell. Press that number in gameplay to load it.")))
                    ]

                    + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0, 0, 0, 8)
                    [
                        SNew(SHorizontalBox)

                        + SHorizontalBox::Slot().AutoWidth().Padding(2)
                        [ SNew(SButton).Text(FText::FromString(TEXT("1"))).OnClicked_Lambda([this]() { if (UWorld* World = GetWorld()) { if (USpellLoadoutSubsystem* Loadout = World->GetSubsystem<USpellLoadoutSubsystem>()) { Loadout->SaveSlot(0, ReadSpell()); Loadout->EquipSlot(0); } } return FReply::Handled(); }) ]
                        + SHorizontalBox::Slot().AutoWidth().Padding(2)
                        [ SNew(SButton).Text(FText::FromString(TEXT("2"))).OnClicked_Lambda([this]() { if (UWorld* World = GetWorld()) { if (USpellLoadoutSubsystem* Loadout = World->GetSubsystem<USpellLoadoutSubsystem>()) { Loadout->SaveSlot(1, ReadSpell()); Loadout->EquipSlot(1); } } return FReply::Handled(); }) ]
                        + SHorizontalBox::Slot().AutoWidth().Padding(2)
                        [ SNew(SButton).Text(FText::FromString(TEXT("3"))).OnClicked_Lambda([this]() { if (UWorld* World = GetWorld()) { if (USpellLoadoutSubsystem* Loadout = World->GetSubsystem<USpellLoadoutSubsystem>()) { Loadout->SaveSlot(2, ReadSpell()); Loadout->EquipSlot(2); } } return FReply::Handled(); }) ]
                        + SHorizontalBox::Slot().AutoWidth().Padding(2)
                        [ SNew(SButton).Text(FText::FromString(TEXT("4"))).OnClicked_Lambda([this]() { if (UWorld* World = GetWorld()) { if (USpellLoadoutSubsystem* Loadout = World->GetSubsystem<USpellLoadoutSubsystem>()) { Loadout->SaveSlot(3, ReadSpell()); Loadout->EquipSlot(3); } } return FReply::Handled(); }) ]
                        + SHorizontalBox::Slot().AutoWidth().Padding(2)
                        [ SNew(SButton).Text(FText::FromString(TEXT("5"))).OnClicked_Lambda([this]() { if (UWorld* World = GetWorld()) { if (USpellLoadoutSubsystem* Loadout = World->GetSubsystem<USpellLoadoutSubsystem>()) { Loadout->SaveSlot(4, ReadSpell()); Loadout->EquipSlot(4); } } return FReply::Handled(); }) ]
                        + SHorizontalBox::Slot().AutoWidth().Padding(2)
                        [ SNew(SButton).Text(FText::FromString(TEXT("6"))).OnClicked_Lambda([this]() { if (UWorld* World = GetWorld()) { if (USpellLoadoutSubsystem* Loadout = World->GetSubsystem<USpellLoadoutSubsystem>()) { Loadout->SaveSlot(5, ReadSpell()); Loadout->EquipSlot(5); } } return FReply::Handled(); }) ]
                        + SHorizontalBox::Slot().AutoWidth().Padding(2)
                        [ SNew(SButton).Text(FText::FromString(TEXT("7"))).OnClicked_Lambda([this]() { if (UWorld* World = GetWorld()) { if (USpellLoadoutSubsystem* Loadout = World->GetSubsystem<USpellLoadoutSubsystem>()) { Loadout->SaveSlot(6, ReadSpell()); Loadout->EquipSlot(6); } } return FReply::Handled(); }) ]
                        + SHorizontalBox::Slot().AutoWidth().Padding(2)
                        [ SNew(SButton).Text(FText::FromString(TEXT("8"))).OnClicked_Lambda([this]() { if (UWorld* World = GetWorld()) { if (USpellLoadoutSubsystem* Loadout = World->GetSubsystem<USpellLoadoutSubsystem>()) { Loadout->SaveSlot(7, ReadSpell()); Loadout->EquipSlot(7); } } return FReply::Handled(); }) ]
                        + SHorizontalBox::Slot().AutoWidth().Padding(2)
                        [ SNew(SButton).Text(FText::FromString(TEXT("9"))).OnClicked_Lambda([this]() { if (UWorld* World = GetWorld()) { if (USpellLoadoutSubsystem* Loadout = World->GetSubsystem<USpellLoadoutSubsystem>()) { Loadout->SaveSlot(8, ReadSpell()); Loadout->EquipSlot(8); } } return FReply::Handled(); }) ]
                        + SHorizontalBox::Slot().AutoWidth().Padding(2)
                        [ SNew(SButton).Text(FText::FromString(TEXT("0"))).OnClicked_Lambda([this]() { if (UWorld* World = GetWorld()) { if (USpellLoadoutSubsystem* Loadout = World->GetSubsystem<USpellLoadoutSubsystem>()) { Loadout->SaveSlot(9, ReadSpell()); Loadout->EquipSlot(9); } } return FReply::Handled(); }) ]
                    ]

                    + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(FSlateColor(FLinearColor(0.72f, 0.88f, 0.74f, 1.0f)))
                        .Text_Lambda([this]() { return GetCurrentSpellSummary(); })
                    ]
'@
    if ($T.Contains($OldPreviewTitleToSummary)) {
        $T = $T.Replace($OldPreviewTitleToSummary, $NewPreviewTitleToSummary)
    }
}
Write-Utf8 $InnerCpp $T

# -----------------------------------------------------------------------------
# SpellPreviewSubsystem : orientation-aware preview.
# -----------------------------------------------------------------------------
Write-Host "Patching SpellPreviewSubsystem orientation-aware preview..." -ForegroundColor Cyan
$T = Read-Normalized $PreviewCpp
if (!$T.Contains('GetOrientedPreviewRotation')) {
    $InsertPoint = @'
    float GetShapeForwardClearanceCm(const FEarthSpellDefinition& Spell)
    {
        switch (Spell.Shape)
        {
            case EEarthSpellShape::Sphere:
                return FMath::Max(Spell.SphereRadiusCm, 1.0f);

            case EEarthSpellShape::Cube:
                return FMath::Max(
                    FMath::Max(Spell.CubeXcm, Spell.CubeYcm),
                    Spell.CubeZcm) * 0.5f;

            case EEarthSpellShape::Cone:
            default:
                return FMath::Max(
                    FMath::Max(Spell.ConeRadiusCm, Spell.ConeHeightCm * 0.5f),
                    1.0f);
        }
    }
'@
    $InsertOrientation = @'
    float GetShapeForwardClearanceCm(const FEarthSpellDefinition& Spell)
    {
        switch (Spell.Shape)
        {
            case EEarthSpellShape::Sphere:
                return FMath::Max(Spell.SphereRadiusCm, 1.0f);

            case EEarthSpellShape::Cube:
                return FMath::Max(
                    FMath::Max(Spell.CubeXcm, Spell.CubeYcm),
                    Spell.CubeZcm) * 0.5f;

            case EEarthSpellShape::Cone:
            default:
                return FMath::Max(
                    FMath::Max(Spell.ConeRadiusCm, Spell.ConeHeightCm * 0.5f),
                    1.0f);
        }
    }

    FQuat GetOrientedPreviewRotation(const FEarthSpellDefinition& Spell, const FQuat& BaseRotation)
    {
        FVector DesiredAxis = BaseRotation.RotateVector(FVector::UpVector).GetSafeNormal();

        switch (Spell.Orientation)
        {
            case EEarthSpellOrientationAxis::Forward:
                DesiredAxis = BaseRotation.RotateVector(FVector::ForwardVector).GetSafeNormal();
                break;
            case EEarthSpellOrientationAxis::Right:
                DesiredAxis = BaseRotation.RotateVector(FVector::RightVector).GetSafeNormal();
                break;
            case EEarthSpellOrientationAxis::Up:
            default:
                DesiredAxis = BaseRotation.RotateVector(FVector::UpVector).GetSafeNormal();
                break;
        }

        if (DesiredAxis.IsNearlyZero())
        {
            DesiredAxis = FVector::UpVector;
        }

        return FQuat::FindBetweenNormals(FVector::UpVector, DesiredAxis);
    }
'@
    if ($T.Contains($InsertPoint)) {
        $T = $T.Replace($InsertPoint, $InsertOrientation)
    }

    $T = $T.Replace('                WorkbenchReferenceTransform.GetRotation(),', '                GetOrientedPreviewRotation(Spell, WorkbenchReferenceTransform.GetRotation()),')
    $T = $T.Replace('        Placement.SpawnRotation.Quaternion(),', '        GetOrientedPreviewRotation(Spell, Placement.SpawnRotation.Quaternion()),')
}
Write-Utf8 $PreviewCpp $T

Write-Host "" 
Write-Host "Ready spell slots + orientation patch applied." -ForegroundColor Green
