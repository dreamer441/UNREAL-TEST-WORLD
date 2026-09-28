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
        raise RuntimeError(f"Could not add include for {label}")
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

execution_cpp = ROOT / "Plugins/SpellExecution/Source/SpellExecution/Private/SpellExecutionSubsystem.cpp"
execution_build = ROOT / "Plugins/SpellExecution/Source/SpellExecution/SpellExecution.Build.cs"
execution_plugin = ROOT / "Plugins/SpellExecution/SpellExecution.uplugin"

inner_cpp = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Private/InnerRealmSubsystem.cpp"

world_codex_types = ROOT / "Plugins/WorldCodex/Source/WorldCodex/Public/WorldCodexTypes.h"
motion_resolver = ROOT / "Plugins/SpellMotion/Source/SpellMotion/Public/SpellMotionResolver.h"

for required in [
    spell_def, earth_def, shape_math,
    execution_cpp, execution_build, execution_plugin,
    inner_cpp, world_codex_types, motion_resolver
]:
    if not required.exists():
        raise RuntimeError(f"Expected file missing: {required}")

if "ECodexTier" not in read(world_codex_types):
    raise RuntimeError(
        "Updated v0.13.5 WorldCodex files were not extracted correctly."
    )

print("[1/7] Adding persistent Motion Direction to spell definitions...")

text = read(spell_def)
if '#include "SpellMotionTypes.h"' not in text:
    if '#include "SpellPatternTypes.h"' in text:
        text = add_include(
            text,
            '#include "SpellPatternTypes.h"',
            '#include "SpellMotionTypes.h"',
            "generic motion types")
    else:
        text = add_include(
            text,
            '#include "SpellSpatialTypes.h"',
            '#include "SpellMotionTypes.h"',
            "generic motion types")

if "ESpellMotionDirection MotionDirection" not in text:
    text = replace_once(
        text,
        '''    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Pattern") FSpellPatternDefinition Pattern;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell") float SpeedMps = 30.0f;''',
        '''    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Pattern") FSpellPatternDefinition Pattern;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Motion") ESpellMotionDirection MotionDirection = ESpellMotionDirection::Forward;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell") float SpeedMps = 30.0f;''',
        "generic MotionDirection field")
write(spell_def, text)

text = read(earth_def)
if '#include "SpellMotionTypes.h"' not in text:
    if '#include "SpellPatternTypes.h"' in text:
        text = add_include(
            text,
            '#include "SpellPatternTypes.h"',
            '#include "SpellMotionTypes.h"',
            "legacy motion types")
    else:
        text = add_include(
            text,
            '#include "SpellSpatialTypes.h"',
            '#include "SpellMotionTypes.h"',
            "legacy motion types")

if "ESpellMotionDirection MotionDirection" not in text:
    marker = '''    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Pattern", meta=(Units="cm"))
    float CircleRadiusCm = 220.0f;'''

    replacement = marker + '''

    /** Independent movement direction. Orientation controls facing, not travel. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Motion")
    ESpellMotionDirection MotionDirection = ESpellMotionDirection::Forward;'''

    text = replace_once(
        text,
        marker,
        replacement,
        "legacy MotionDirection field")
write(earth_def, text)

print("[2/7] Preserving Motion Direction through normalization/adapters...")

text = read(shape_math)

normalize_start = text.find("static FSpellDefinition Normalize")
normalize_end = text.find("return Spell;", normalize_start)
normalize_chunk = text[normalize_start:normalize_end]

if "Spell.MotionDirection" not in normalize_chunk:
    marker = "    Spell.SpeedMps = Positive(Spell.SpeedMps, 0.0f, Defaults.SpeedMps);"
    replacement = '''    switch (Spell.MotionDirection)
    {
        case ESpellMotionDirection::Forward:
        case ESpellMotionDirection::Backward:
        case ESpellMotionDirection::Up:
        case ESpellMotionDirection::Down:
        case ESpellMotionDirection::Outward:
        case ESpellMotionDirection::Inward:
        case ESpellMotionDirection::Tangent:
            break;
        default:
            Spell.MotionDirection = ESpellMotionDirection::Forward;
            break;
    }

    Spell.SpeedMps = Positive(Spell.SpeedMps, 0.0f, Defaults.SpeedMps);'''
    text = replace_once(
        text,
        marker,
        replacement,
        "MotionDirection normalization")

if "D.MotionDirection=L.MotionDirection;" not in text:
    if "D.Pattern.InstanceOrientation=L.PatternOrientation;" in text:
        text = text.replace(
            "D.Pattern.InstanceOrientation=L.PatternOrientation;",
            "D.Pattern.InstanceOrientation=L.PatternOrientation; D.MotionDirection=L.MotionDirection;",
            1)
    else:
        text = text.replace(
            "D.SpeedMps=L.SpeedMps;",
            "D.MotionDirection=L.MotionDirection; D.SpeedMps=L.SpeedMps;",
            1)

if "L.MotionDirection=D.MotionDirection;" not in text:
    if "L.PatternOrientation=D.Pattern.InstanceOrientation;" in text:
        text = text.replace(
            "L.PatternOrientation=D.Pattern.InstanceOrientation;",
            "L.PatternOrientation=D.Pattern.InstanceOrientation; L.MotionDirection=D.MotionDirection;",
            1)
    else:
        text = text.replace(
            "L.SpeedMps=D.SpeedMps;",
            "L.MotionDirection=D.MotionDirection; L.SpeedMps=D.SpeedMps;",
            1)

if "D.MotionDirection=L.MotionDirection;" not in text:
    raise RuntimeError("Could not patch legacy -> generic MotionDirection adapter.")
if "L.MotionDirection=D.MotionDirection;" not in text:
    raise RuntimeError("Could not patch generic -> legacy MotionDirection adapter.")

write(shape_math, text)

print("[3/7] Wiring the generic SpellMotion module into execution...")

add_build_dependency(execution_build, "SpellMotion")
add_plugin_dependency(execution_plugin, "SpellMotion")

text = read(execution_cpp)
if '#include "SpellMotionResolver.h"' not in text:
    if '#include "SpellPatternResolver.h"' in text:
        text = add_include(
            text,
            '#include "SpellPatternResolver.h"',
            '#include "SpellMotionResolver.h"',
            "SpellMotion execution include")
    else:
        text = add_include(
            text,
            '#include "SpellCastPlacement.h"',
            '#include "SpellMotionResolver.h"',
            "SpellMotion execution include")

if "InstanceLaunchDirection = FSpellMotionResolver::ResolveDirection" not in text:
    old = '''        for (const FResolvedPatternInstance& Instance : ResolvedInstances)
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
        }'''

    new = '''        for (const FResolvedPatternInstance& Instance : ResolvedInstances)
        {
            const FQuat FinalRotation =
                Instance.PatternRotation * BaseSpellRotation;

            const FVector InstanceLaunchDirection =
                FSpellMotionResolver::ResolveDirection(
                    ResolvedSpell.Definition.MotionDirection,
                    ResolvedSpell.Definition.Pattern,
                    Instance.Location,
                    Placement.SpawnLocation,
                    Placement.LaunchDirection);

            if (FEarthSpellSpawner::SpawnAndLaunch(
                World,
                Controller,
                ResolvedSpell,
                Instance.Location,
                FinalRotation.Rotator(),
                InstanceLaunchDirection))
            {
                ++SpawnedCount;
            }
        }'''

    text = replace_once(
        text,
        old,
        new,
        "per-instance motion direction execution")

write(execution_cpp, text)

print("[4/7] Adding Direction controls to the existing Spell Modifier page...")

text = read(inner_cpp)

if "auto MakeMotionDirectionControl" not in text:
    marker = '''    auto MakeReadySlot = [this, BlackText](const int32 SlotIndex, const TCHAR* Label) -> TSharedRef<SWidget>'''

    helper = r'''    auto MakeMotionDirectionControl = [this, BlackText](
        const ESpellMotionDirection Direction,
        const TCHAR* Label) -> TSharedRef<SWidget>
    {
        return SNew(SButton)
            .IsFocusable(false)
            .OnClicked_Lambda([this, Direction]()
            {
                FEarthSpellDefinition Spell = ReadSpell();
                Spell.MotionDirection = Direction;
                WriteSpell(Spell);
                return FReply::Handled();
            })
            [
                SNew(STextBlock)
                .ColorAndOpacity(BlackText)
                .Text_Lambda([this, Direction, Label]()
                {
                    if (ReadSpell().MotionDirection == Direction)
                    {
                        return FText::FromString(
                            FString::Printf(TEXT("[ %s ]"), Label));
                    }
                    return FText::FromString(Label);
                })
            ];
    };

'''

    if marker not in text:
        raise RuntimeError("Could not locate MakeReadySlot in InnerRealm.")

    text = text.replace(marker, helper + marker, 1)

if 'TEXT("DIRECTION / TRAVEL")' not in text:
    marker = '''                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
                        [ Section(TEXT("MOTION / MATERIAL")) ]'''

    direction_ui = marker + r'''

                        + SVerticalBox::Slot().AutoHeight().Padding(0, 4, 0, 3)
                        [
                            SNew(STextBlock)
                            .ColorAndOpacity(BlackText)
                            .Text(FText::FromString(TEXT("DIRECTION / TRAVEL   (independent from shape orientation)")))
                        ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0, 2, 0, 3)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().Padding(0,0,8,0)
                            [ MakeMotionDirectionControl(ESpellMotionDirection::Forward, TEXT("Forward")) ]
                            + SHorizontalBox::Slot().AutoWidth().Padding(0,0,8,0)
                            [ MakeMotionDirectionControl(ESpellMotionDirection::Backward, TEXT("Backward")) ]
                            + SHorizontalBox::Slot().AutoWidth().Padding(0,0,8,0)
                            [ MakeMotionDirectionControl(ESpellMotionDirection::Up, TEXT("Up")) ]
                            + SHorizontalBox::Slot().AutoWidth()
                            [ MakeMotionDirectionControl(ESpellMotionDirection::Down, TEXT("Down")) ]
                        ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0, 2, 0, 9)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().Padding(0,0,8,0)
                            [ MakeMotionDirectionControl(ESpellMotionDirection::Outward, TEXT("Outward")) ]
                            + SHorizontalBox::Slot().AutoWidth().Padding(0,0,8,0)
                            [ MakeMotionDirectionControl(ESpellMotionDirection::Inward, TEXT("Inward")) ]
                            + SHorizontalBox::Slot().AutoWidth()
                            [ MakeMotionDirectionControl(ESpellMotionDirection::Tangent, TEXT("Tangent")) ]
                        ]'''

    text = replace_once(
        text,
        marker,
        direction_ui,
        "Motion Direction Workbench UI")

write(inner_cpp, text)

print("[5/7] Showing Codex Tier grammar and the new Value category...")

text = read(inner_cpp)

if "TIER\\n%s" not in text:
    old = '''        TEXT("CONCEPT ID\\n%s\\n\\nCATEGORY\\n%s\\n\\nSTATUS\\n%s\\n\\nOWNING SYSTEM\\n%s\\n\\nDESCRIPTION\\n%s\\n\\nPROVIDES CAPABILITIES\\n%s\\n\\nREQUIRES CAPABILITIES\\n%s\\n\\nRELATIONSHIPS\\n%s"),
        *Entry->ConceptId.ToString(),
        *CodexCategoryToText(Entry->Category).ToString(),
        *CodexImplementationStateToText(Entry->ImplementationState).ToString(),'''

    new = '''        TEXT("CONCEPT ID\\n%s\\n\\nCATEGORY\\n%s\\n\\nTIER\\n%s\\n\\nSTATUS\\n%s\\n\\nOWNING SYSTEM\\n%s\\n\\nDESCRIPTION\\n%s\\n\\nPROVIDES CAPABILITIES\\n%s\\n\\nREQUIRES CAPABILITIES\\n%s\\n\\nRELATIONSHIPS\\n%s"),
        *Entry->ConceptId.ToString(),
        *CodexCategoryToText(Entry->Category).ToString(),
        *CodexTierToText(Entry->Tier).ToString(),
        *CodexImplementationStateToText(Entry->ImplementationState).ToString(),'''

    text = replace_once(
        text,
        old,
        new,
        "Codex Tier details")

if "ECodexCategory::Value," not in text:
    marker = '''            ECodexCategory::Logic,
            ECodexCategory::PhysicsConcept'''
    replacement = '''            ECodexCategory::Logic,
            ECodexCategory::Value,
            ECodexCategory::PhysicsConcept'''
    text = replace_once(
        text,
        marker,
        replacement,
        "Codex Value category order")

write(inner_cpp, text)

print("[6/7] Verifying Codex semantic cleanup...")

codex_cpp = read(
    ROOT / "Plugins/WorldCodex/Source/WorldCodex/Private/WorldCodexSubsystem.cpp")

required_codex_tokens = [
    'TEXT("value.magnitude.0")',
    'TEXT("value.magnitude.5")',
    'TEXT("world.state.airborne")',
    'TEXT("motion.direction")',
    'ECodexTier::TierI',
    'ECodexTier::TierIII'
]

for token in required_codex_tokens:
    if token not in codex_cpp:
        raise RuntimeError(f"Updated Codex vocabulary missing expected token: {token}")

if 'TEXT("world.state.in_air")' in codex_cpp:
    raise RuntimeError("Old ambiguous world.state.in_air entry is still present.")

print("[7/7] v0.13.5 patch applied successfully.")
print()
print("Important semantics:")
print("  Orientation = where the object faces.")
print("  Motion Direction = where the object travels.")
print("  Magnitude 0..5 = Tier III normalized language for the future Canvas.")
print("  Airborne = boolean state of a referenced object, not an event/loop.")
