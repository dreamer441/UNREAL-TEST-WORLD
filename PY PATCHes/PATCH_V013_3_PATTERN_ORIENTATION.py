from pathlib import Path

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

earth_def = ROOT / "Plugins/SpellCreation/Source/SpellCreation/Public/EarthSpellDefinition.h"
shape_math = ROOT / "Plugins/SpellCreation/Source/SpellCreation/Private/SpellShapeMath.cpp"
inner_cpp = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Private/InnerRealmSubsystem.cpp"
preview_cpp = ROOT / "Plugins/SpellPreview/Source/SpellPreview/Private/SpellPreviewSubsystem.cpp"
execution_cpp = ROOT / "Plugins/SpellExecution/Source/SpellExecution/Private/SpellExecutionSubsystem.cpp"

for required in [earth_def, shape_math, inner_cpp, preview_cpp, execution_cpp]:
    if not required.exists():
        raise RuntimeError(f"Expected v0.13.2.1 file missing: {required}")

if not (ROOT / "Plugins/SpellPattern/SpellPattern.uplugin").exists():
    raise RuntimeError("v0.13.3 requires working v0.13.2.1 first.")

print("[1/5] Adding legacy Workbench PatternOrientation field...")
text = read(earth_def)

if "ESpellPatternOrientation PatternOrientation" not in text:
    text = replace_once(
        text,
        '''    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Pattern")
    ESpellPatternAxis PatternAxis = ESpellPatternAxis::Right;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Pattern", meta=(Units="cm"))
    float SpacingCm = 100.0f;''',
        '''    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Pattern")
    ESpellPatternAxis PatternAxis = ESpellPatternAxis::Right;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Pattern")
    ESpellPatternOrientation PatternOrientation = ESpellPatternOrientation::Shared;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Pattern", meta=(Units="cm"))
    float SpacingCm = 100.0f;''',
        "legacy PatternOrientation field",
    )

write(earth_def, text)

print("[2/5] Updating adapter and normalization...")
text = read(shape_math)

normalize_start = text.find("static FSpellDefinition Normalize")
normalize_end = text.find("return Spell;", normalize_start)
normalize_chunk = text[normalize_start:normalize_end]

if "Spell.Pattern.InstanceOrientation" not in normalize_chunk:
    marker = '''    Spell.Pattern.CircleRadiusCm = Clamped(
        Spell.Pattern.CircleRadiusCm,
        SpellPatternRanges::MinCircleRadiusCm,
        SpellPatternRanges::MaxCircleRadiusCm,
        Defaults.Pattern.CircleRadiusCm);
    Spell.SpeedMps = Positive(Spell.SpeedMps, 0.0f, Defaults.SpeedMps);'''

    replacement = '''    Spell.Pattern.CircleRadiusCm = Clamped(
        Spell.Pattern.CircleRadiusCm,
        SpellPatternRanges::MinCircleRadiusCm,
        SpellPatternRanges::MaxCircleRadiusCm,
        Defaults.Pattern.CircleRadiusCm);

    switch (Spell.Pattern.InstanceOrientation)
    {
        case ESpellPatternOrientation::Shared:
        case ESpellPatternOrientation::Outward:
        case ESpellPatternOrientation::Inward:
        case ESpellPatternOrientation::Tangent:
            break;
        default:
            Spell.Pattern.InstanceOrientation = ESpellPatternOrientation::Shared;
            break;
    }

    Spell.SpeedMps = Positive(Spell.SpeedMps, 0.0f, Defaults.SpeedMps);'''

    text = replace_once(
        text,
        marker,
        replacement,
        "PatternOrientation normalization",
    )

if "D.Pattern.InstanceOrientation=L.PatternOrientation;" not in text:
    text = replace_once(
        text,
        '''D.Pattern.Amount=L.Amount; D.Pattern.Arrangement=L.Arrangement; D.Pattern.LineAxis=L.PatternAxis; D.Pattern.SpacingCm=L.SpacingCm; D.Pattern.CircleRadiusCm=L.CircleRadiusCm;''',
        '''D.Pattern.Amount=L.Amount; D.Pattern.Arrangement=L.Arrangement; D.Pattern.LineAxis=L.PatternAxis; D.Pattern.InstanceOrientation=L.PatternOrientation; D.Pattern.SpacingCm=L.SpacingCm; D.Pattern.CircleRadiusCm=L.CircleRadiusCm;''',
        "legacy -> generic PatternOrientation adapter",
    )

if "L.PatternOrientation=D.Pattern.InstanceOrientation;" not in text:
    text = replace_once(
        text,
        '''L.Amount=D.Pattern.Amount; L.Arrangement=D.Pattern.Arrangement; L.PatternAxis=D.Pattern.LineAxis; L.SpacingCm=D.Pattern.SpacingCm; L.CircleRadiusCm=D.Pattern.CircleRadiusCm;''',
        '''L.Amount=D.Pattern.Amount; L.Arrangement=D.Pattern.Arrangement; L.PatternAxis=D.Pattern.LineAxis; L.PatternOrientation=D.Pattern.InstanceOrientation; L.SpacingCm=D.Pattern.SpacingCm; L.CircleRadiusCm=D.Pattern.CircleRadiusCm;''',
        "generic -> legacy PatternOrientation adapter",
    )

write(shape_math, text)

print("[3/5] Adding Workbench INSTANCE ORIENTATION UI...")
text = read(inner_cpp)

if "auto MakePatternOrientationControl" not in text:
    marker = '''    auto MakeReadySlot = [this, BlackText](const int32 SlotIndex, const TCHAR* Label) -> TSharedRef<SWidget>'''

    helper = r'''    auto MakePatternOrientationControl = [this, BlackText](
        const ESpellPatternOrientation Mode,
        const TCHAR* Label) -> TSharedRef<SWidget>
    {
        return SNew(SButton)
            .IsFocusable(false)
            .OnClicked_Lambda([this, Mode]()
            {
                FEarthSpellDefinition Spell = ReadSpell();
                Spell.PatternOrientation = Mode;
                WriteSpell(Spell);
                return FReply::Handled();
            })
            [
                SNew(STextBlock)
                .ColorAndOpacity(BlackText)
                .Text_Lambda([this, Mode, Label]()
                {
                    return FText::FromString(
                        ReadSpell().PatternOrientation == Mode
                            ? FString::Printf(TEXT("[ %s ]"), Label)
                            : FString(Label));
                })
            ];
    };

'''

    if marker not in text:
        raise RuntimeError("Could not locate MakeReadySlot in Workbench.")

    text = text.replace(marker, helper + marker, 1)

if 'Section(TEXT("INSTANCE ORIENTATION"))' not in text:
    marker = '''                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
                        [ Section(TEXT("SIZE / SHAPE DIMENSIONS")) ]'''

    ui = r'''                        + SVerticalBox::Slot().AutoHeight().Padding(0,7,0,3)
                        [
                            SNew(SBox)
                            .Visibility_Lambda([this]()
                            {
                                return ReadSpell().Amount > 1
                                    ? EVisibility::Visible
                                    : EVisibility::Collapsed;
                            })
                            [
                                Section(TEXT("INSTANCE ORIENTATION"))
                            ]
                        ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,4,0,8)
                        [
                            SNew(SBox)
                            .Visibility_Lambda([this]()
                            {
                                return ReadSpell().Amount > 1
                                    ? EVisibility::Visible
                                    : EVisibility::Collapsed;
                            })
                            [
                                SNew(SHorizontalBox)
                                + SHorizontalBox::Slot().AutoWidth().Padding(0,0,10,0)
                                [ MakePatternOrientationControl(ESpellPatternOrientation::Shared, TEXT("Shared")) ]
                                + SHorizontalBox::Slot().AutoWidth().Padding(0,0,10,0)
                                [ MakePatternOrientationControl(ESpellPatternOrientation::Outward, TEXT("Outward")) ]
                                + SHorizontalBox::Slot().AutoWidth().Padding(0,0,10,0)
                                [ MakePatternOrientationControl(ESpellPatternOrientation::Inward, TEXT("Inward")) ]
                                + SHorizontalBox::Slot().AutoWidth()
                                [ MakePatternOrientationControl(ESpellPatternOrientation::Tangent, TEXT("Tangent")) ]
                            ]
                        ]

'''

    if marker not in text:
        raise RuntimeError("Could not locate SIZE / SHAPE DIMENSIONS section.")

    text = text.replace(marker, ui + marker, 1)

write(inner_cpp, text)

print("[4/5] Upgrading SpellExecution to instance transforms...")
text = read(execution_cpp)

old_execution = '''    TArray<FVector> ResolvedLocations;
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
        break;'''

new_execution = '''    TArray<FResolvedPatternInstance> ResolvedInstances;
    FSpellPatternResolver::ResolveInstances(
        ResolvedSpell.Definition.Pattern,
        Placement.SpawnLocation,
        Placement.LaunchDirection,
        ResolvedInstances);

    const FQuat BaseSpellRotation = Placement.SpawnRotation.Quaternion();

    int32 SpawnedCount = 0;
    switch (ResolvedSpell.Definition.Element)
    {
    case ESpellElement::Earth:
        for (const FResolvedPatternInstance& Instance : ResolvedInstances)
        {
            const FQuat FinalRotation =
                Instance.PatternRotation * BaseSpellRotation;

            if (FEarthSpellSpawner::SpawnAndLaunch(
                World,
                Controller,
                ResolvedSpell,
                Instance.Location,
                FinalRotation.Rotator(),
                Placement.LaunchDirection))
            {
                ++SpawnedCount;
            }
        }
        break;'''

text = replace_once(
    text,
    old_execution,
    new_execution,
    "SpellExecution instance transforms",
)

write(execution_cpp, text)

print("[5/5] Upgrading Workbench and live preview transforms...")
text = read(preview_cpp)

old_workbench = '''            TArray<FVector> PreviewLocations;
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

new_workbench = '''            TArray<FResolvedPatternInstance> PreviewInstances;
            FSpellPatternResolver::ResolveInstances(
                SpellCreation->GetStoredGenericSpellDefinition().Pattern,
                PreviewCenter,
                Forward,
                PreviewInstances);

            const FQuat BaseSpellRotation =
                GetWorkbenchOrientationRotation(
                    Spell,
                    WorkbenchReferenceTransform.GetRotation());

            for (const FResolvedPatternInstance& Instance : PreviewInstances)
            {
                const FQuat FinalRotation =
                    Instance.PatternRotation * BaseSpellRotation;

                DrawSpellVisual(
                    World,
                    Spell,
                    Instance.Location,
                    FinalRotation,
                    Spell.SpeedMps > 0.1f);
            }'''

text = replace_once(
    text,
    old_workbench,
    new_workbench,
    "Workbench instance transforms",
)

old_live = '''    TArray<FVector> LivePreviewLocations;
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

new_live = '''    TArray<FResolvedPatternInstance> LivePreviewInstances;
    FSpellPatternResolver::ResolveInstances(
        ResolvedSpell.Definition.Pattern,
        Placement.SpawnLocation,
        AimDirection,
        LivePreviewInstances);

    const FQuat LiveBaseSpellRotation =
        Placement.SpawnRotation.Quaternion();

    for (const FResolvedPatternInstance& Instance : LivePreviewInstances)
    {
        const FQuat FinalRotation =
            Instance.PatternRotation * LiveBaseSpellRotation;

        DrawSpellVisual(
            World,
            Spell,
            Instance.Location,
            FinalRotation,
            bLiveSpeedActive);
    }'''

text = replace_once(
    text,
    old_live,
    new_live,
    "live instance transforms",
)

write(preview_cpp, text)

print()
print("v0.13.3 Pattern Orientation patch applied successfully.")
print("Shared preserves current behavior; movement direction remains unchanged.")
