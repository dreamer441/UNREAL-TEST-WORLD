from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent

def read(path: Path) -> str:
    if not path.exists():
        raise RuntimeError(f"Expected file missing: {path}")
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")

def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")

def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"Could not find expected block for: {label}")
    return text.replace(old, new, 1)

def add_include(text: str, after: str, include_line: str, label: str) -> str:
    if include_line in text:
        return text
    if after not in text:
        raise RuntimeError(f"Could not add include for {label}; marker missing")
    return text.replace(after, after + "\n" + include_line, 1)

def add_build_dependency(path: Path, module: str) -> None:
    text = read(path)
    token = f'"{module}"'
    if token in text:
        return
    marker = "PublicDependencyModuleNames.AddRange(new string[]\n        {"
    if marker not in text:
        raise RuntimeError(f"Could not locate dependency list in {path}")
    text = text.replace(marker, marker + f'\n            "{module}",', 1)
    write(path, text)

def add_plugin_dependency(path: Path, plugin: str) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    deps = data.setdefault("Plugins", [])
    if not any(d.get("Name") == plugin for d in deps):
        deps.append({"Name": plugin, "Enabled": True})
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

spell_def = ROOT / "Plugins/SpellCreation/Source/SpellCreation/Public/SpellDefinition.h"
earth_def = ROOT / "Plugins/SpellCreation/Source/SpellCreation/Public/EarthSpellDefinition.h"
shape_math = ROOT / "Plugins/SpellCreation/Source/SpellCreation/Private/SpellShapeMath.cpp"
inner_cpp = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Private/InnerRealmSubsystem.cpp"
preview_cpp = ROOT / "Plugins/SpellPreview/Source/SpellPreview/Private/SpellPreviewSubsystem.cpp"
preview_build = ROOT / "Plugins/SpellPreview/Source/SpellPreview/SpellPreview.Build.cs"
preview_plugin = ROOT / "Plugins/SpellPreview/SpellPreview.uplugin"
execution_cpp = ROOT / "Plugins/SpellExecution/Source/SpellExecution/Private/SpellExecutionSubsystem.cpp"
execution_build = ROOT / "Plugins/SpellExecution/Source/SpellExecution/SpellExecution.Build.cs"
execution_plugin = ROOT / "Plugins/SpellExecution/SpellExecution.uplugin"

for required in [
    spell_def, earth_def, shape_math, inner_cpp, preview_cpp,
    preview_build, preview_plugin, execution_cpp, execution_build, execution_plugin
]:
    if not required.exists():
        raise RuntimeError(f"Expected v0.13.1.1 file missing: {required}")

if not (ROOT / "Plugins/SpellLoadout/SpellLoadout.uplugin").exists():
    raise RuntimeError("v0.13.2 expects working v0.13.1.1 Ready Slots + Orientation first.")

if not (ROOT / "Plugins/SpellCreation/Source/SpellCreation/Public/SpellSpatialTypes.h").exists():
    raise RuntimeError("v0.13.2 expects v0.13.1.1 Orientation foundation first.")

print("[1/8] Wiring SpellPattern dependencies...")
add_build_dependency(execution_build, "SpellPattern")
add_build_dependency(preview_build, "SpellPattern")
add_plugin_dependency(execution_plugin, "SpellPattern")
add_plugin_dependency(preview_plugin, "SpellPattern")

print("[2/8] Adding Pattern data to spell definitions...")
text = read(spell_def)
text = add_include(
    text,
    '#include "SpellSpatialTypes.h"',
    '#include "SpellPatternTypes.h"',
    "generic pattern types",
)
if "FSpellPatternDefinition Pattern;" not in text:
    text = replace_once(
        text,
        '    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Spatial") ESpellOrientationAxis Orientation = ESpellOrientationAxis::Up;\n'
        '    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell") float SpeedMps = 30.0f;',
        '    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Spatial") ESpellOrientationAxis Orientation = ESpellOrientationAxis::Up;\n'
        '    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Pattern") FSpellPatternDefinition Pattern;\n'
        '    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell") float SpeedMps = 30.0f;',
        "FSpellDefinition Pattern field",
    )
write(spell_def, text)

text = read(earth_def)
text = add_include(
    text,
    '#include "SpellSpatialTypes.h"',
    '#include "SpellPatternTypes.h"',
    "legacy pattern types",
)
if "int32 Amount = 1;" not in text:
    text = replace_once(
        text,
        '    ESpellOrientationAxis Orientation = ESpellOrientationAxis::Up;',
        '''    ESpellOrientationAxis Orientation = ESpellOrientationAxis::Up;

    // Legacy shadow of generic Pattern fields. This keeps the current Workbench
    // adapter lossless until the UI edits FSpellDefinition directly.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Pattern")
    int32 Amount = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Pattern")
    ESpellArrangement Arrangement = ESpellArrangement::Line;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Pattern")
    ESpellPatternAxis PatternAxis = ESpellPatternAxis::Right;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Pattern", meta=(Units="cm"))
    float SpacingCm = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Pattern", meta=(Units="cm"))
    float CircleRadiusCm = 220.0f;''',
        "legacy pattern shadow",
    )
write(earth_def, text)

print("[3/8] Normalizing and adapting Pattern data...")
text = read(shape_math)

if "Spell.Pattern.Amount = FMath::Clamp" not in text:
    text = replace_once(
        text,
        '''    Spell.DistanceM = Positive(Spell.DistanceM, 0.0f, Defaults.DistanceM);
    Spell.SpeedMps = Positive(Spell.SpeedMps, 0.0f, Defaults.SpeedMps);''',
        '''    Spell.DistanceM = Positive(Spell.DistanceM, 0.0f, Defaults.DistanceM);
    Spell.Pattern.Amount = FMath::Clamp(
        Spell.Pattern.Amount,
        SpellPatternRanges::MinAmount,
        SpellPatternRanges::MaxAmount);
    Spell.Pattern.SpacingCm = Clamped(
        Spell.Pattern.SpacingCm,
        SpellPatternRanges::MinSpacingCm,
        SpellPatternRanges::MaxSpacingCm,
        Defaults.Pattern.SpacingCm);
    Spell.Pattern.CircleRadiusCm = Clamped(
        Spell.Pattern.CircleRadiusCm,
        SpellPatternRanges::MinCircleRadiusCm,
        SpellPatternRanges::MaxCircleRadiusCm,
        Defaults.Pattern.CircleRadiusCm);
    Spell.SpeedMps = Positive(Spell.SpeedMps, 0.0f, Defaults.SpeedMps);''',
        "pattern normalization",
    )

if "D.Pattern.Amount=L.Amount;" not in text:
    text = replace_once(
        text,
        'D.DistanceM=L.DistanceM; D.Orientation=L.Orientation; D.SpeedMps=L.SpeedMps;',
        'D.DistanceM=L.DistanceM; D.Orientation=L.Orientation; D.Pattern.Amount=L.Amount; D.Pattern.Arrangement=L.Arrangement; D.Pattern.LineAxis=L.PatternAxis; D.Pattern.SpacingCm=L.SpacingCm; D.Pattern.CircleRadiusCm=L.CircleRadiusCm; D.SpeedMps=L.SpeedMps;',
        "legacy -> generic pattern adapter",
    )

if "L.Amount=D.Pattern.Amount;" not in text:
    text = replace_once(
        text,
        'L.DistanceM=D.DistanceM; L.Orientation=D.Orientation; L.SpeedMps=D.SpeedMps;',
        'L.DistanceM=D.DistanceM; L.Orientation=D.Orientation; L.Amount=D.Pattern.Amount; L.Arrangement=D.Pattern.Arrangement; L.PatternAxis=D.Pattern.LineAxis; L.SpacingCm=D.Pattern.SpacingCm; L.CircleRadiusCm=D.Pattern.CircleRadiusCm; L.SpeedMps=D.SpeedMps;',
        "generic -> legacy pattern adapter",
    )

write(shape_math, text)

print("[4/8] Expanding SpellExecution into multi-instance realization...")
text = read(execution_cpp)
text = add_include(
    text,
    '#include "SpellLoadoutSubsystem.h"',
    '#include "SpellPatternResolver.h"',
    "pattern execution include",
)

if "ResolvedLocations" not in text:
    text = replace_once(
        text,
        '''    bool bSpawned = false;
    switch (ResolvedSpell.Definition.Element)
    {
    case ESpellElement::Earth:
        bSpawned = FEarthSpellSpawner::SpawnAndLaunch(
            World,
            Controller,
            ResolvedSpell,
            Placement.SpawnLocation,
            Placement.SpawnRotation,
            Placement.LaunchDirection) != nullptr;
        break;
    default:
        return FSpellExecutionResult::ForOutcome(ESpellExecutionOutcome::UnsupportedElement);
    }

    if (!bSpawned)
    {
        return FSpellExecutionResult::ForOutcome(ESpellExecutionOutcome::SpawnFailed);
    }''',
        '''    TArray<FVector> ResolvedLocations;
    FSpellPatternResolver::ResolveLocations(
        ResolvedSpell.Definition.Pattern,
        Placement.SpawnLocation,
        Placement.LaunchDirection,
        ResolvedLocations);

    int32 SpawnedCount = 0;
    switch (ResolvedSpell.Definition.Element)
    {
    case ESpellElement::Earth:
        for (const FVector& SpawnLocation : ResolvedLocations)
        {
            if (FEarthSpellSpawner::SpawnAndLaunch(
                World,
                Controller,
                ResolvedSpell,
                SpawnLocation,
                Placement.SpawnRotation,
                Placement.LaunchDirection))
            {
                ++SpawnedCount;
            }
        }
        break;

    default:
        return FSpellExecutionResult::ForOutcome(ESpellExecutionOutcome::UnsupportedElement);
    }

    if (SpawnedCount <= 0)
    {
        return FSpellExecutionResult::ForOutcome(ESpellExecutionOutcome::SpawnFailed);
    }''',
        "multi-instance execution",
    )

write(execution_cpp, text)

print("[5/8] Adding Workbench MULTIPLE OBJECTS editor...")
text = read(inner_cpp)

if "auto MakeArrangementControl" not in text:
    marker = '''    auto MakeReadySlot = [this, BlackText](const int32 SlotIndex, const TCHAR* Label) -> TSharedRef<SWidget>'''
    helpers = r'''    auto MakeArrangementControl = [this, BlackText](
        const ESpellArrangement Arrangement,
        const TCHAR* Label) -> TSharedRef<SWidget>
    {
        return SNew(SButton)
            .IsFocusable(false)
            .OnClicked_Lambda([this, Arrangement]()
            {
                FEarthSpellDefinition Spell = ReadSpell();
                Spell.Arrangement = Arrangement;
                WriteSpell(Spell);
                return FReply::Handled();
            })
            [
                SNew(STextBlock)
                .ColorAndOpacity(BlackText)
                .Text_Lambda([this, Arrangement, Label]()
                {
                    return FText::FromString(ReadSpell().Arrangement == Arrangement
                        ? FString::Printf(TEXT("[ %s ]"), Label)
                        : FString(Label));
                })
            ];
    };

    auto MakePatternAxisControl = [this, BlackText](
        const ESpellPatternAxis Axis,
        const TCHAR* Label) -> TSharedRef<SWidget>
    {
        return SNew(SButton)
            .IsFocusable(false)
            .OnClicked_Lambda([this, Axis]()
            {
                FEarthSpellDefinition Spell = ReadSpell();
                Spell.PatternAxis = Axis;
                WriteSpell(Spell);
                return FReply::Handled();
            })
            [
                SNew(STextBlock)
                .ColorAndOpacity(BlackText)
                .Text_Lambda([this, Axis, Label]()
                {
                    return FText::FromString(ReadSpell().PatternAxis == Axis
                        ? FString::Printf(TEXT("[ %s ]"), Label)
                        : FString(Label));
                })
            ];
    };

'''
    if marker not in text:
        raise RuntimeError("Could not locate MakeReadySlot lambda; apply v0.13.1.1 first.")
    text = text.replace(marker, helpers + marker, 1)

if 'Section(TEXT("MULTIPLE OBJECTS"))' not in text:
    marker = '''                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
                        [ Section(TEXT("SIZE / SHAPE DIMENSIONS")) ]'''

    block = r'''                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
                        [ Section(TEXT("MULTIPLE OBJECTS")) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        [
                            SNew(STextBlock)
                            .ColorAndOpacity(BlackText)
                            .Text_Lambda([this]()
                            {
                                return FText::FromString(FString::Printf(
                                    TEXT("Amount: %d   (1 = single object; pattern activates above 1)"),
                                    ReadSpell().Amount));
                            })
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,9)
                        [
                            SNew(SSlider)
                            .IsFocusable(false)
                            .Value_Lambda([this]()
                            {
                                return static_cast<float>(ReadSpell().Amount - SpellPatternRanges::MinAmount)
                                    / static_cast<float>(SpellPatternRanges::MaxAmount - SpellPatternRanges::MinAmount);
                            })
                            .OnValueChanged_Lambda([this](float V)
                            {
                                FEarthSpellDefinition Spell = ReadSpell();
                                Spell.Amount = FMath::Clamp(
                                    FMath::RoundToInt(FMath::Lerp(
                                        static_cast<float>(SpellPatternRanges::MinAmount),
                                        static_cast<float>(SpellPatternRanges::MaxAmount),
                                        V)),
                                    SpellPatternRanges::MinAmount,
                                    SpellPatternRanges::MaxAmount);
                                WriteSpell(Spell);
                            })
                        ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        .Visibility_Lambda([this]()
                        {
                            return ReadSpell().Amount > 1
                                ? EVisibility::Visible
                                : EVisibility::Collapsed;
                        })
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,12,0)
                            [
                                SNew(STextBlock)
                                .ColorAndOpacity(BlackText)
                                .Text(FText::FromString(TEXT("Arrangement:")))
                            ]
                            + SHorizontalBox::Slot().AutoWidth().Padding(0,0,10,0)
                            [ MakeArrangementControl(ESpellArrangement::Line, TEXT("Line")) ]
                            + SHorizontalBox::Slot().AutoWidth()
                            [ MakeArrangementControl(ESpellArrangement::Circle, TEXT("Circle")) ]
                        ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        .Visibility_Lambda([this]()
                        {
                            const FEarthSpellDefinition Spell = ReadSpell();
                            return Spell.Amount > 1 && Spell.Arrangement == ESpellArrangement::Line
                                ? EVisibility::Visible : EVisibility::Collapsed;
                        })
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,12,0)
                            [
                                SNew(STextBlock)
                                .ColorAndOpacity(BlackText)
                                .Text(FText::FromString(TEXT("Line axis:")))
                            ]
                            + SHorizontalBox::Slot().AutoWidth().Padding(0,0,10,0)
                            [ MakePatternAxisControl(ESpellPatternAxis::Forward, TEXT("Forward")) ]
                            + SHorizontalBox::Slot().AutoWidth().Padding(0,0,10,0)
                            [ MakePatternAxisControl(ESpellPatternAxis::Right, TEXT("Right")) ]
                            + SHorizontalBox::Slot().AutoWidth()
                            [ MakePatternAxisControl(ESpellPatternAxis::Up, TEXT("Up")) ]
                        ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        .Visibility_Lambda([this]()
                        {
                            const FEarthSpellDefinition Spell = ReadSpell();
                            return Spell.Amount > 1 && Spell.Arrangement == ESpellArrangement::Line
                                ? EVisibility::Visible : EVisibility::Collapsed;
                        })
                        [
                            SNew(STextBlock)
                            .ColorAndOpacity(BlackText)
                            .Text_Lambda([this]()
                            {
                                return FText::FromString(FString::Printf(
                                    TEXT("Spacing: %.0f cm"),
                                    ReadSpell().SpacingCm));
                            })
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,9)
                        .Visibility_Lambda([this]()
                        {
                            const FEarthSpellDefinition Spell = ReadSpell();
                            return Spell.Amount > 1 && Spell.Arrangement == ESpellArrangement::Line
                                ? EVisibility::Visible : EVisibility::Collapsed;
                        })
                        [
                            SNew(SSlider)
                            .IsFocusable(false)
                            .Value_Lambda([this]()
                            {
                                return SpellParameterRanges::Normalize(
                                    ReadSpell().SpacingCm,
                                    SpellPatternRanges::MinSpacingCm,
                                    SpellPatternRanges::MaxSpacingCm);
                            })
                            .OnValueChanged_Lambda([this](float V)
                            {
                                FEarthSpellDefinition Spell = ReadSpell();
                                Spell.SpacingCm = SpellParameterRanges::Denormalize(
                                    V,
                                    SpellPatternRanges::MinSpacingCm,
                                    SpellPatternRanges::MaxSpacingCm);
                                WriteSpell(Spell);
                            })
                        ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        .Visibility_Lambda([this]()
                        {
                            const FEarthSpellDefinition Spell = ReadSpell();
                            return Spell.Amount > 1 && Spell.Arrangement == ESpellArrangement::Circle
                                ? EVisibility::Visible : EVisibility::Collapsed;
                        })
                        [
                            SNew(STextBlock)
                            .ColorAndOpacity(BlackText)
                            .Text_Lambda([this]()
                            {
                                return FText::FromString(FString::Printf(
                                    TEXT("Circle radius: %.0f cm"),
                                    ReadSpell().CircleRadiusCm));
                            })
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,9)
                        .Visibility_Lambda([this]()
                        {
                            const FEarthSpellDefinition Spell = ReadSpell();
                            return Spell.Amount > 1 && Spell.Arrangement == ESpellArrangement::Circle
                                ? EVisibility::Visible : EVisibility::Collapsed;
                        })
                        [
                            SNew(SSlider)
                            .IsFocusable(false)
                            .Value_Lambda([this]()
                            {
                                return SpellParameterRanges::Normalize(
                                    ReadSpell().CircleRadiusCm,
                                    SpellPatternRanges::MinCircleRadiusCm,
                                    SpellPatternRanges::MaxCircleRadiusCm);
                            })
                            .OnValueChanged_Lambda([this](float V)
                            {
                                FEarthSpellDefinition Spell = ReadSpell();
                                Spell.CircleRadiusCm = SpellParameterRanges::Denormalize(
                                    V,
                                    SpellPatternRanges::MinCircleRadiusCm,
                                    SpellPatternRanges::MaxCircleRadiusCm);
                                WriteSpell(Spell);
                            })
                        ]

''' + marker
    text = replace_once(text, marker, block, "MULTIPLE OBJECTS Workbench section")

if 'TEXT("EARTH / %s / %s   |   x%d %s' not in text:
    text = replace_once(
        text,
        '''        TEXT("EARTH / %s / %s   |   speed %.0f m/s   |   density %.0f kg/m3   |   mass %.0f kg   |   distance %.1f m"),
        *GetShapeName().ToString(),
        Orientation,
        Spell.SpeedMps,
        Spell.DensityKgPerM3,
        UEarthSpellMath::CalculateMassKg(Spell),
        Spell.DistanceM));''',
        '''        TEXT("EARTH / %s / %s   |   x%d %s   |   speed %.0f m/s   |   density %.0f kg/m3   |   mass %.0f kg   |   distance %.1f m"),
        *GetShapeName().ToString(),
        Orientation,
        Spell.Amount,
        Spell.Amount > 1
            ? (Spell.Arrangement == ESpellArrangement::Circle ? TEXT("CIRCLE") : TEXT("LINE"))
            : TEXT("SINGLE"),
        Spell.SpeedMps,
        Spell.DensityKgPerM3,
        UEarthSpellMath::CalculateMassKg(Spell),
        Spell.DistanceM));''',
        "Workbench summary amount/pattern",
    )

write(inner_cpp, text)

print("[6/8] Making Workbench and live preview pattern-aware...")
text = read(preview_cpp)
text = add_include(
    text,
    '#include "SpellCreationSubsystem.h"',
    '#include "SpellPatternResolver.h"',
    "pattern preview include",
)

old_workbench = '''            DrawSpellVisual(
                World,
                Spell,
                PreviewCenter,
                GetWorkbenchOrientationRotation(Spell, WorkbenchReferenceTransform.GetRotation()),
                Spell.SpeedMps > 0.1f);'''
new_workbench = '''            TArray<FVector> PreviewLocations;
            FSpellPatternResolver::ResolveLocations(
                SpellCreation->GetStoredGenericSpellDefinition().Pattern,
                PreviewCenter,
                Forward,
                PreviewLocations);

            for (const FVector& InstanceLocation : PreviewLocations)
            {
                DrawSpellVisual(
                    World,
                    Spell,
                    InstanceLocation,
                    GetWorkbenchOrientationRotation(Spell, WorkbenchReferenceTransform.GetRotation()),
                    Spell.SpeedMps > 0.1f);
            }'''

if old_workbench in text:
    text = text.replace(old_workbench, new_workbench, 1)
elif "TArray<FVector> PreviewLocations;" not in text:
    raise RuntimeError("Could not locate v0.13.1.1 Workbench preview block")

old_live_a = '''    DrawSpellVisual(
        World,
        Spell,
        Placement.SpawnLocation,
        GetWorkbenchOrientationRotation(Spell, Placement.SpawnRotation.Quaternion()),
        bLiveSpeedActive);'''

old_live_b = '''    DrawSpellVisual(
        World,
        Spell,
        Placement.SpawnLocation,
        Placement.SpawnRotation.Quaternion(),
        bLiveSpeedActive);'''

new_live = '''    TArray<FVector> LivePreviewLocations;
    FSpellPatternResolver::ResolveLocations(
        ResolvedSpell.Definition.Pattern,
        Placement.SpawnLocation,
        AimDirection,
        LivePreviewLocations);

    for (const FVector& InstanceLocation : LivePreviewLocations)
    {
        DrawSpellVisual(
            World,
            Spell,
            InstanceLocation,
            Placement.SpawnRotation.Quaternion(),
            bLiveSpeedActive);
    }'''

if old_live_a in text:
    text = text.replace(old_live_a, new_live, 1)
elif old_live_b in text:
    text = text.replace(old_live_b, new_live, 1)
elif "TArray<FVector> LivePreviewLocations;" not in text:
    raise RuntimeError("Could not locate live preview block")

write(preview_cpp, text)

print("[7/8] Verifying ready slots store complete generic spell definitions...")
loadout_h = ROOT / "Plugins/SpellLoadout/Source/SpellLoadout/Public/SpellLoadoutSubsystem.h"
loadout_cpp = ROOT / "Plugins/SpellLoadout/Source/SpellLoadout/Private/SpellLoadoutSubsystem.cpp"
loadout_text = read(loadout_h) + "\n" + read(loadout_cpp)
if "FSpellDefinition" not in loadout_text:
    raise RuntimeError("SpellLoadout is not storing FSpellDefinition.")
print("      Pattern will be included automatically in ready slots.")

print("[8/8] Verifying modifier-contract foundation...")
contract_h = ROOT / "Plugins/SpellCreation/Source/SpellCreation/Public/SpellModifierContract.h"
if not contract_h.exists():
    raise RuntimeError("SpellModifierContract.h was not extracted.")

print()
print("v0.13.2 applied successfully.")
print("All instances share the spell's current Orientation in V1.")
