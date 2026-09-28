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
live_h = ROOT / "Plugins/LiveSpellCasting/Source/LiveSpellCasting/Public/LiveSpellSessionSubsystem.h"
live_cpp = ROOT / "Plugins/LiveSpellCasting/Source/LiveSpellCasting/Private/LiveSpellSessionSubsystem.cpp"
execution_cpp = ROOT / "Plugins/SpellExecution/Source/SpellExecution/Private/SpellExecutionSubsystem.cpp"
placement_cpp = ROOT / "Plugins/SpellExecution/Source/SpellExecution/Private/SpellCastPlacement.cpp"
execution_build = ROOT / "Plugins/SpellExecution/Source/SpellExecution/SpellExecution.Build.cs"
execution_plugin = ROOT / "Plugins/SpellExecution/SpellExecution.uplugin"
inner_cpp = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Private/InnerRealmSubsystem.cpp"
inner_build = ROOT / "Plugins/InnerRealm/Source/InnerRealm/InnerRealm.Build.cs"
inner_plugin = ROOT / "Plugins/InnerRealm/InnerRealm.uplugin"
preview_cpp = ROOT / "Plugins/SpellPreview/Source/SpellPreview/Private/SpellPreviewSubsystem.cpp"
bindings_cpp = ROOT / "Plugins/SpellCastingBindings/Source/SpellCastingBindings/Private/SpellCastingBindingSubsystem.cpp"

for required in [
    spell_def, earth_def, shape_math, live_h, live_cpp, execution_cpp,
    placement_cpp, execution_build, execution_plugin, inner_cpp,
    inner_build, inner_plugin, preview_cpp, bindings_cpp
]:
    if not required.exists():
        raise RuntimeError(f"Expected current cleanup-branch file missing: {required}")

print("[1/9] Adding SpellLoadout dependencies...")
add_build_dependency(inner_build, "SpellLoadout")
add_build_dependency(execution_build, "SpellLoadout")
add_plugin_dependency(inner_plugin, "SpellLoadout")
add_plugin_dependency(execution_plugin, "SpellLoadout")

print("[2/9] Adding generic Orientation data...")
text = read(spell_def)
text = add_include(text, '#include "PhysicalBodyState.h"', '#include "SpellSpatialTypes.h"', "SpellDefinition orientation types")
if "ESpellOrientationAxis Orientation" not in text:
    text = replace_once(
        text,
        '    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell") float DistanceM = 3.0f;\n'
        '    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell") float SpeedMps = 30.0f;',
        '    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell") float DistanceM = 3.0f;\n'
        '    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Spatial") ESpellOrientationAxis Orientation = ESpellOrientationAxis::Up;\n'
        '    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell") float SpeedMps = 30.0f;',
        "generic orientation property",
    )
write(spell_def, text)

text = read(earth_def)
text = add_include(text, '#include "CoreMinimal.h"', '#include "SpellSpatialTypes.h"', "legacy orientation types")
if "ESpellOrientationAxis Orientation" not in text:
    text = replace_once(
        text,
        '    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Spatial", meta=(ClampMin="0.0", Units="m"))\n'
        '    float DistanceM = 3.0f;',
        '    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Spatial", meta=(ClampMin="0.0", Units="m"))\n'
        '    float DistanceM = 3.0f;\n\n'
        '    /** Axis the constructed shape is aligned to inside the cast frame. */\n'
        '    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Spatial")\n'
        '    ESpellOrientationAxis Orientation = ESpellOrientationAxis::Up;',
        "legacy orientation shadow",
    )
write(earth_def, text)

print("[3/9] Preserving Orientation through the legacy compatibility adapter...")
text = read(shape_math)
if "D.Orientation=L.Orientation;" not in text:
    text = replace_once(
        text,
        '    D.ShapeDefinition={L.SphereRadiusCm,L.CubeXcm,L.CubeYcm,L.CubeZcm,L.ConeRadiusCm,L.ConeHeightCm}; D.DistanceM=L.DistanceM; D.SpeedMps=L.SpeedMps;',
        '    D.ShapeDefinition={L.SphereRadiusCm,L.CubeXcm,L.CubeYcm,L.CubeZcm,L.ConeRadiusCm,L.ConeHeightCm}; D.DistanceM=L.DistanceM; D.Orientation=L.Orientation; D.SpeedMps=L.SpeedMps;',
        "legacy -> generic orientation adapter",
    )
if "L.Orientation=D.Orientation;" not in text:
    text = replace_once(
        text,
        'L.ConeRadiusCm=D.ShapeDefinition.ConeRadiusCm; L.ConeHeightCm=D.ShapeDefinition.ConeHeightCm; L.DistanceM=D.DistanceM; L.SpeedMps=D.SpeedMps;',
        'L.ConeRadiusCm=D.ShapeDefinition.ConeRadiusCm; L.ConeHeightCm=D.ShapeDefinition.ConeHeightCm; L.DistanceM=D.DistanceM; L.Orientation=D.Orientation; L.SpeedMps=D.SpeedMps;',
        "generic -> legacy orientation adapter",
    )
write(shape_math, text)

print("[4/9] Adding prepared-spell loading to LiveSpellCasting...")
text = read(live_h)
if "LoadPreparedSpell" not in text:
    text = replace_once(
        text,
        '    void SelectShape(EEarthSpellShape Shape);',
        '    void SelectShape(EEarthSpellShape Shape);\n'
        '    /** Loads a complete prepared definition into the transient live session. */\n'
        '    void LoadPreparedSpell(const FSpellDefinition& Spell);',
        "LoadPreparedSpell declaration",
    )
if "PreparedSpellBase" not in text:
    text = replace_once(
        text,
        'private:\n    FLiveSpellState State;',
        'private:\n'
        '    FLiveSpellState State;\n'
        '    /** Optional prepared spell base; manual Q/root selection clears it. */\n'
        '    TOptional<FSpellDefinition> PreparedSpellBase;',
        "PreparedSpellBase member",
    )
write(live_h, text)

text = read(live_cpp)
text = add_include(text, '#include "SpellCreationSubsystem.h"', '#include "SpellParameterRanges.h"', "prepared-spell ranges")
text = replace_once(
    text,
    'void ULiveSpellSessionSubsystem::ResetSession() { State.Reset(); }',
    'void ULiveSpellSessionSubsystem::ResetSession() { PreparedSpellBase.Reset(); State.Reset(); }',
    "ResetSession prepared base clear",
)
text = replace_once(
    text,
    'void ULiveSpellSessionSubsystem::SelectEarth() { State.SelectElement(ESpellElement::Earth); }',
    'void ULiveSpellSessionSubsystem::SelectEarth() { PreparedSpellBase.Reset(); State.SelectElement(ESpellElement::Earth); }',
    "SelectEarth prepared base clear",
)
if "void ULiveSpellSessionSubsystem::LoadPreparedSpell" not in text:
    marker = 'void ULiveSpellSessionSubsystem::SelectShape(EEarthSpellShape Shape) { State.SelectShape(Shape == EEarthSpellShape::Sphere ? ESpellShape::Sphere : Shape == EEarthSpellShape::Cube ? ESpellShape::Cube : ESpellShape::Cone); }'
    load_impl = r'''
void ULiveSpellSessionSubsystem::LoadPreparedSpell(const FSpellDefinition& Spell)
{
    PreparedSpellBase = FSpellDefinitionAdapter::Resolve(Spell).Definition;
    State.Reset();
    State.SelectElement(PreparedSpellBase->Element);
    State.SelectShape(PreparedSpellBase->Shape);

    auto SetRange = [this](const ELiveSpellParameter Parameter, const float Value, const float MinValue, const float MaxValue)
    {
        State.SetParameterNormalized(Parameter, SpellParameterRanges::Normalize(Value, MinValue, MaxValue));
    };

    const FSpellDefinition& D = PreparedSpellBase.GetValue();
    SetRange(ELiveSpellParameter::SphereRadius, D.ShapeDefinition.SphereRadiusCm, SpellParameterRanges::MinSphereRadiusCm, SpellParameterRanges::MaxSphereRadiusCm);
    SetRange(ELiveSpellParameter::CubeX, D.ShapeDefinition.CubeXcm, SpellParameterRanges::MinCubeSideCm, SpellParameterRanges::MaxCubeSideCm);
    SetRange(ELiveSpellParameter::CubeY, D.ShapeDefinition.CubeYcm, SpellParameterRanges::MinCubeSideCm, SpellParameterRanges::MaxCubeSideCm);
    SetRange(ELiveSpellParameter::CubeZ, D.ShapeDefinition.CubeZcm, SpellParameterRanges::MinCubeSideCm, SpellParameterRanges::MaxCubeSideCm);
    SetRange(ELiveSpellParameter::ConeRadius, D.ShapeDefinition.ConeRadiusCm, SpellParameterRanges::MinConeRadiusCm, SpellParameterRanges::MaxConeRadiusCm);
    SetRange(ELiveSpellParameter::ConeHeight, D.ShapeDefinition.ConeHeightCm, SpellParameterRanges::MinConeHeightCm, SpellParameterRanges::MaxConeHeightCm);
    SetRange(ELiveSpellParameter::Speed, D.SpeedMps, SpellParameterRanges::MinSpeedMps, SpellParameterRanges::MaxSpeedMps);
    SetRange(ELiveSpellParameter::Density, D.Material.DensityKgPerM3, SpellParameterRanges::MinDensityKgPerM3, SpellParameterRanges::MaxDensityKgPerM3);
    SetRange(ELiveSpellParameter::Distance, D.DistanceM, SpellParameterRanges::MinDistanceM, SpellParameterRanges::MaxDistanceM);
    State.SetParameterNormalized(ELiveSpellParameter::Hardness, FMath::Clamp(D.Material.Hardness, 0.0f, 1.0f));
    State.SetParameterNormalized(ELiveSpellParameter::Toughness, FMath::Clamp(D.Material.Toughness, 0.0f, 1.0f));
    State.SetParameterNormalized(ELiveSpellParameter::Elasticity, FMath::Clamp(D.Material.Restitution, 0.0f, 1.0f));
}
'''.strip()
    text = replace_once(text, marker, marker + "\n" + load_impl, "LoadPreparedSpell implementation")

text = replace_once(
    text,
    'FResolvedSpell ULiveSpellSessionSubsystem::ResolveGenericSpell() const { return State.Resolve(GetPersistentGenericDefaults()); }',
    'FResolvedSpell ULiveSpellSessionSubsystem::ResolveGenericSpell() const { return State.Resolve(PreparedSpellBase.IsSet() ? PreparedSpellBase.GetValue() : GetPersistentGenericDefaults()); }',
    "prepared ResolveGenericSpell base",
)
write(live_cpp, text)

print("[5/9] Loading slots from number keys inside SpellExecution...")
text = read(execution_cpp)
text = add_include(text, '#include "SpellCastPlacement.h"', '#include "SpellLoadoutSubsystem.h"', "SpellLoadout execution include")
if "Prepared spell slots 1..0" not in text:
    old = '''    APlayerController* Controller = World->GetFirstPlayerController();
    if (Controller && Controller->WasInputKeyJustPressed(EKeys::SpaceBar))
    {
        ExecuteLiveSpell();
    }'''
    new = '''    APlayerController* Controller = World->GetFirstPlayerController();
    if (!Controller)
    {
        return;
    }

    // Prepared spell slots 1..0: load first, SPACE remains the universal execution key.
    static const FKey SlotKeys[USpellLoadoutSubsystem::SlotCount] =
    {
        EKeys::One, EKeys::Two, EKeys::Three, EKeys::Four, EKeys::Five,
        EKeys::Six, EKeys::Seven, EKeys::Eight, EKeys::Nine, EKeys::Zero
    };

    if (USpellLoadoutSubsystem* Loadout = World->GetSubsystem<USpellLoadoutSubsystem>())
    {
        if (ULiveSpellSessionSubsystem* LiveSession = World->GetSubsystem<ULiveSpellSessionSubsystem>())
        {
            for (int32 SlotIndex = 0; SlotIndex < USpellLoadoutSubsystem::SlotCount; ++SlotIndex)
            {
                if (Controller->WasInputKeyJustPressed(SlotKeys[SlotIndex]))
                {
                    FSpellDefinition PreparedSpell;
                    if (Loadout->GetSlotSpell(SlotIndex, PreparedSpell))
                    {
                        Loadout->EquipSlot(SlotIndex);
                        LiveSession->LoadPreparedSpell(PreparedSpell);
                    }
                    break;
                }
            }
        }
    }

    if (Controller->WasInputKeyJustPressed(EKeys::SpaceBar))
    {
        ExecuteLiveSpell();
    }'''
    text = replace_once(text, old, new, "SpellExecution number-slot input")
write(execution_cpp, text)

print("[6/9] Applying Orientation to actual cast placement...")
text = read(placement_cpp)
if "Definition.Orientation" not in text:
    old = '''    OutPlacement.SpawnLocation = Pawn->GetActorLocation()
        + FVector(0.0f, 0.0f, ChestOffsetCm)
        + PlacementForward * (CharacterSafetyGapCm + ShapeClearanceCm + ExtraDistanceCm);
    OutPlacement.LaunchDirection = LaunchDirection;
    OutPlacement.SpawnRotation = FRotator(0.0f, PlacementForward.Rotation().Yaw, 0.0f);
    return true;'''
    new = '''    OutPlacement.SpawnLocation = Pawn->GetActorLocation()
        + FVector(0.0f, 0.0f, ChestOffsetCm)
        + PlacementForward * (CharacterSafetyGapCm + ShapeClearanceCm + ExtraDistanceCm);
    OutPlacement.LaunchDirection = LaunchDirection;

    // Shape orientation is independent from aim/launch direction.
    switch (Definition.Orientation)
    {
    case ESpellOrientationAxis::Forward:
        OutPlacement.SpawnRotation = FRotationMatrix::MakeFromZX(
            LaunchDirection,
            FVector::UpVector).Rotator();
        break;

    case ESpellOrientationAxis::Right:
    {
        FVector CastRight = FVector::CrossProduct(FVector::UpVector, PlacementForward).GetSafeNormal();
        if (CastRight.IsNearlyZero())
        {
            CastRight = Pawn->GetActorRightVector().GetSafeNormal();
        }
        OutPlacement.SpawnRotation = FRotationMatrix::MakeFromZX(
            CastRight,
            FVector::UpVector).Rotator();
        break;
    }

    case ESpellOrientationAxis::Up:
    default:
        OutPlacement.SpawnRotation = FRotator(0.0f, PlacementForward.Rotation().Yaw, 0.0f);
        break;
    }

    return true;'''
    text = replace_once(text, old, new, "orientation-aware placement")
write(placement_cpp, text)

print("[7/9] Adding Workbench Orientation controls and 10 save slots...")
text = read(inner_cpp)
text = add_include(text, '#include "SpellCastingBindingSubsystem.h"', '#include "SpellLoadoutSubsystem.h"', "Workbench loadout include")

old_summary = '''FText UInnerRealmSubsystem::GetCurrentSpellSummary() const
{
    const FEarthSpellDefinition Spell = ReadSpell();
    return FText::FromString(FString::Printf(
        TEXT("EARTH / %s   |   speed %.0f m/s   |   density %.0f kg/m3   |   mass %.0f kg   |   distance %.1f m"),
        *GetShapeName().ToString(),
        Spell.SpeedMps,
        Spell.DensityKgPerM3,
        UEarthSpellMath::CalculateMassKg(Spell),
        Spell.DistanceM));
}'''
new_summary = '''FText UInnerRealmSubsystem::GetCurrentSpellSummary() const
{
    const FEarthSpellDefinition Spell = ReadSpell();
    const TCHAR* Orientation = TEXT("UP / Z");
    switch (Spell.Orientation)
    {
        case ESpellOrientationAxis::Forward: Orientation = TEXT("FORWARD / X"); break;
        case ESpellOrientationAxis::Right:   Orientation = TEXT("RIGHT / Y"); break;
        case ESpellOrientationAxis::Up:
        default:                             Orientation = TEXT("UP / Z"); break;
    }

    return FText::FromString(FString::Printf(
        TEXT("EARTH / %s / %s   |   speed %.0f m/s   |   density %.0f kg/m3   |   mass %.0f kg   |   distance %.1f m"),
        *GetShapeName().ToString(),
        Orientation,
        Spell.SpeedMps,
        Spell.DensityKgPerM3,
        UEarthSpellMath::CalculateMassKg(Spell),
        Spell.DistanceM));
}'''
if old_summary in text:
    text = text.replace(old_summary, new_summary, 1)

if "auto MakeOrientationControl" not in text:
    marker = '''    auto MakeDimension = [this, &MakeBindSelector, BlackText]('''
    orientation_lambda = r'''    auto MakeOrientationControl = [this, BlackText](
        const ESpellOrientationAxis Orientation,
        const TCHAR* Label) -> TSharedRef<SWidget>
    {
        return SNew(SButton)
            .IsFocusable(false)
            .ContentPadding(FMargin(12.0f, 6.0f))
            .OnClicked_Lambda([this, Orientation]()
            {
                FEarthSpellDefinition Spell = ReadSpell();
                Spell.Orientation = Orientation;
                WriteSpell(Spell);
                return FReply::Handled();
            })
            [
                SNew(STextBlock)
                .ColorAndOpacity(BlackText)
                .Text_Lambda([this, Orientation, Label]()
                {
                    return FText::FromString(
                        ReadSpell().Orientation == Orientation
                            ? FString::Printf(TEXT("[ %s ]"), Label)
                            : FString(Label));
                })
            ];
    };

'''
    if marker not in text:
        raise RuntimeError("Could not locate MakeDimension lambda for Orientation controls")
    text = text.replace(marker, orientation_lambda + marker, 1)

if 'Section(TEXT("ORIENTATION"))' not in text:
    marker = '''                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
                        [ Section(TEXT("SIZE / SHAPE DIMENSIONS")) ]'''
    block = '''                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
                        [ Section(TEXT("ORIENTATION")) ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0, 4, 0, 4)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().Padding(0,0,14,0)
                            [ MakeOrientationControl(ESpellOrientationAxis::Forward, TEXT("Forward / X")) ]
                            + SHorizontalBox::Slot().AutoWidth().Padding(0,0,14,0)
                            [ MakeOrientationControl(ESpellOrientationAxis::Right, TEXT("Right / Y")) ]
                            + SHorizontalBox::Slot().AutoWidth()
                            [ MakeOrientationControl(ESpellOrientationAxis::Up, TEXT("Up / Z")) ]
                        ]

''' + marker
    text = replace_once(text, marker, block, "Workbench Orientation section")

if "auto MakeReadySlot" not in text:
    marker = '''    EditorWidget = SNew(SBox)'''
    ready_lambda = r'''    auto MakeReadySlot = [this, BlackText](const int32 SlotIndex, const TCHAR* Label) -> TSharedRef<SWidget>
    {
        return SNew(SButton)
            .IsFocusable(false)
            .ContentPadding(FMargin(8.0f, 5.0f))
            .ToolTipText(FText::FromString(TEXT("Save the current Workbench spell into this ready slot.")))
            .OnClicked_Lambda([this, SlotIndex]()
            {
                UWorld* World = GetWorld();
                USpellCreationSubsystem* Creation = GetSpellCreation();
                USpellLoadoutSubsystem* Loadout = World ? World->GetSubsystem<USpellLoadoutSubsystem>() : nullptr;
                if (Creation && Loadout)
                {
                    Loadout->SaveSlot(SlotIndex, Creation->GetStoredGenericSpellDefinition());
                    Loadout->EquipSlot(SlotIndex);
                }
                return FReply::Handled();
            })
            [
                SNew(STextBlock)
                .ColorAndOpacity(BlackText)
                .Text_Lambda([this, SlotIndex, Label]()
                {
                    UWorld* World = GetWorld();
                    const USpellLoadoutSubsystem* Loadout = World ? World->GetSubsystem<USpellLoadoutSubsystem>() : nullptr;
                    const bool bSaved = Loadout && Loadout->IsSlotOccupied(SlotIndex);
                    return FText::FromString(bSaved
                        ? FString::Printf(TEXT("%s*"), Label)
                        : FString(Label));
                })
            ];
    };

'''
    if marker not in text:
        raise RuntimeError("Could not locate EditorWidget creation for ready-slot lambda")
    text = text.replace(marker, ready_lambda + marker, 1)

if "READY SPELL SLOTS" not in text:
    marker = '''                    + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0, 0, 0, 8)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(FSlateColor(FLinearColor(0.86f, 0.96f, 0.87f, 1.0f)))
                        .Text(FText::FromString(TEXT("SPELL WORKBENCH / 3D PREVIEW")))
                    ]'''
    slot_block = '''                    + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0, 0, 0, 5)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(FSlateColor(FLinearColor(0.82f, 0.94f, 0.84f, 1.0f)))
                        .Text(FText::FromString(TEXT("READY SPELL SLOTS  -  click to save current spell")))
                    ]

                    + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0, 0, 0, 10)
                    [
                        SNew(SHorizontalBox)
                        + SHorizontalBox::Slot().AutoWidth().Padding(2)[MakeReadySlot(0, TEXT("1"))]
                        + SHorizontalBox::Slot().AutoWidth().Padding(2)[MakeReadySlot(1, TEXT("2"))]
                        + SHorizontalBox::Slot().AutoWidth().Padding(2)[MakeReadySlot(2, TEXT("3"))]
                        + SHorizontalBox::Slot().AutoWidth().Padding(2)[MakeReadySlot(3, TEXT("4"))]
                        + SHorizontalBox::Slot().AutoWidth().Padding(2)[MakeReadySlot(4, TEXT("5"))]
                        + SHorizontalBox::Slot().AutoWidth().Padding(2)[MakeReadySlot(5, TEXT("6"))]
                        + SHorizontalBox::Slot().AutoWidth().Padding(2)[MakeReadySlot(6, TEXT("7"))]
                        + SHorizontalBox::Slot().AutoWidth().Padding(2)[MakeReadySlot(7, TEXT("8"))]
                        + SHorizontalBox::Slot().AutoWidth().Padding(2)[MakeReadySlot(8, TEXT("9"))]
                        + SHorizontalBox::Slot().AutoWidth().Padding(2)[MakeReadySlot(9, TEXT("0"))]
                    ]

''' + marker
    text = replace_once(text, marker, slot_block, "ready-slot row above Workbench preview")
write(inner_cpp, text)

print("[8/9] Making Workbench preview orientation-aware...")
text = read(preview_cpp)
if "GetWorkbenchOrientationRotation" not in text:
    marker = '''    void DrawSpellVisual(
        UWorld* World,'''
    helper = r'''    FQuat GetWorkbenchOrientationRotation(
        const FEarthSpellDefinition& Spell,
        const FQuat& BaseRotation)
    {
        if (Spell.Orientation == ESpellOrientationAxis::Up)
        {
            return BaseRotation;
        }

        FVector DesiredZ = Spell.Orientation == ESpellOrientationAxis::Forward
            ? BaseRotation.RotateVector(FVector::ForwardVector)
            : BaseRotation.RotateVector(FVector::RightVector);
        DesiredZ.Normalize();

        FVector ReferenceX = BaseRotation.RotateVector(FVector::UpVector);
        if (ReferenceX.IsNearlyZero() || FMath::Abs(FVector::DotProduct(DesiredZ, ReferenceX.GetSafeNormal())) > 0.98f)
        {
            ReferenceX = FVector::ForwardVector;
        }

        return FRotationMatrix::MakeFromZX(DesiredZ, ReferenceX).ToQuat();
    }

'''
    if marker not in text:
        raise RuntimeError("Could not locate DrawSpellVisual for Workbench orientation helper")
    text = text.replace(marker, helper + marker, 1)

old = '''                WorkbenchReferenceTransform.GetRotation(),
                Spell.SpeedMps > 0.1f);'''
new = '''                GetWorkbenchOrientationRotation(Spell, WorkbenchReferenceTransform.GetRotation()),
                Spell.SpeedMps > 0.1f);'''
if old in text:
    text = text.replace(old, new, 1)
elif "GetWorkbenchOrientationRotation(Spell, WorkbenchReferenceTransform.GetRotation())" not in text:
    raise RuntimeError("Could not update Workbench preview rotation")
write(preview_cpp, text)

print("[9/9] Reserving number keys for ready spell slots...")
text = read(bindings_cpp)
can_assign_start = text.find("bool USpellCastingBindingSubsystem::CanAssignKey")
can_assign_end = text.find("bool USpellCastingBindingSubsystem::IsShapeSelector")
can_assign_chunk = text[can_assign_start:can_assign_end]
if "EKeys::One" not in can_assign_chunk:
    marker = '''        && Key != EKeys::Escape
        && Key != EKeys::MouseScrollUp'''
    replacement = '''        && Key != EKeys::Escape
        && Key != EKeys::One
        && Key != EKeys::Two
        && Key != EKeys::Three
        && Key != EKeys::Four
        && Key != EKeys::Five
        && Key != EKeys::Six
        && Key != EKeys::Seven
        && Key != EKeys::Eight
        && Key != EKeys::Nine
        && Key != EKeys::Zero
        && Key != EKeys::MouseScrollUp'''
    text = replace_once(text, marker, replacement, "reserve numeric loadout keys")
write(bindings_cpp, text)

print()
print("Patch v0.13.1.1 applied successfully.")
print("Ready slots live in SpellLoadout; Orientation is generic spell data.")
