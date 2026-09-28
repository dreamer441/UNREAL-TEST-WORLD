from pathlib import Path

ROOT = Path(__file__).resolve().parent

INNER_CPP = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Private/InnerRealmSubsystem.cpp"
INNER_H = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Public/InnerRealmSubsystem.h"
UI_DIR = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Private/UI"
ARCH_DOC = ROOT / "Docs/ARCHITECTURE_V1.md"

for path in [INNER_CPP, INNER_H, ARCH_DOC]:
    if not path.exists():
        raise RuntimeError(f"Expected file missing: {path}")

UI_DIR.mkdir(parents=True, exist_ok=True)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def find_matching_brace(text: str, open_index: int) -> int:
    depth = 0
    i = open_index
    state = "code"

    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""

        if state == "code":
            if ch == "/" and nxt == "/":
                state = "line_comment"
                i += 2
                continue
            if ch == "/" and nxt == "*":
                state = "block_comment"
                i += 2
                continue
            if ch == '"':
                state = "string"
                i += 1
                continue
            if ch == "'":
                state = "char"
                i += 1
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return i

        elif state == "line_comment":
            if ch == "\n":
                state = "code"

        elif state == "block_comment":
            if ch == "*" and nxt == "/":
                state = "code"
                i += 2
                continue

        elif state == "string":
            if ch == "\\":
                i += 2
                continue
            if ch == '"':
                state = "code"

        elif state == "char":
            if ch == "\\":
                i += 2
                continue
            if ch == "'":
                state = "code"

        i += 1

    raise RuntimeError("Unbalanced braces while extracting function.")


def extract_member_function(text: str, function_name: str):
    needle = f"UInnerRealmSubsystem::{function_name}"
    pos = text.find(needle)
    if pos < 0:
        raise RuntimeError(f"Could not find function: {function_name}")

    line_start = text.rfind("\n", 0, pos) + 1
    brace = text.find("{", pos)
    if brace < 0:
        raise RuntimeError(f"Could not find opening brace for: {function_name}")

    close = find_matching_brace(text, brace)

    end = close + 1
    while end < len(text) and text[end] in " \t":
        end += 1
    if end < len(text) and text[end] == "\n":
        end += 1
    if end < len(text) and text[end] == "\n":
        end += 1

    block = text[line_start:end].rstrip() + "\n"
    updated = text[:line_start] + text[end:]
    return updated, block


def extract_group(text: str, names):
    blocks = []
    for name in names:
        text, block = extract_member_function(text, name)
        blocks.append(block)
    return text, "\n".join(blocks)


print("[1/7] Verifying v0.15.1 generic Workbench base...")

header = read(INNER_H)
source = read(INNER_CPP)

required = [
    ("shared shell", "TSharedPtr<SWidget> ShellWidget;" in header),
    ("generic Workbench read", "FSpellDefinition UInnerRealmSubsystem::ReadSpell() const" in source),
    ("generic Workbench write", "SetStoredGenericSpellDefinition(Spell)" in source),
    ("shared shell builder", "FInnerRealmShellUI::Build" in source),
    ("radial Canvas", "void UInnerRealmSubsystem::RebuildCanvasWidget()" in source),
]

missing = [name for name, ok in required if not ok]
if missing:
    raise RuntimeError(
        "This patch expects the working v0.15.1 project. Missing: "
        + ", ".join(missing)
    )

print("[2/7] Extracting Spell Workbench presentation helpers...")

workbench_functions = [
    "ReadSpell",
    "WriteSpell",
    "SetShape",
    "GetShapeName",
    "GetBindingChord",
    "HandleBindingSelected",
    "GetCurrentSpellSummary",
    "GetSpeedSlider",
    "GetDistanceSlider",
    "GetDensitySlider",
    "GetHardnessSlider",
    "GetToughnessSlider",
    "GetElasticitySlider",
    "SetSpeedSlider",
    "SetDistanceSlider",
    "SetDensitySlider",
    "SetHardnessSlider",
    "SetToughnessSlider",
    "SetElasticitySlider",
    "GetDimensionSlider",
    "SetDimensionSlider",
    "GetDimensionVisibility",
    "GetDimensionLabel",
]

source, workbench_block = extract_group(source, workbench_functions)

workbench_cpp = r'''#include "InnerRealmSubsystem.h"

#include "SpellCastingBindingSubsystem.h"
#include "SpellCreationSubsystem.h"
#include "SpellParameterRanges.h"
#include "SpellShapeMath.h"

namespace InnerRealmEditor
{
    static void GetDimensionRange(
        const ESpellShape Shape,
        const int32 Index,
        float& OutMin,
        float& OutMax)
    {
        switch (Shape)
        {
            case ESpellShape::Sphere:
                OutMin = SpellParameterRanges::MinSphereRadiusCm;
                OutMax = SpellParameterRanges::MaxSphereRadiusCm;
                break;

            case ESpellShape::Cube:
                OutMin = SpellParameterRanges::MinCubeSideCm;
                OutMax = SpellParameterRanges::MaxCubeSideCm;
                break;

            case ESpellShape::Cone:
            default:
                if (Index == 0)
                {
                    OutMin = SpellParameterRanges::MinConeRadiusCm;
                    OutMax = SpellParameterRanges::MaxConeRadiusCm;
                }
                else
                {
                    OutMin = SpellParameterRanges::MinConeHeightCm;
                    OutMax = SpellParameterRanges::MaxConeHeightCm;
                }
                break;
        }
    }
}

''' + workbench_block

write(UI_DIR / "SpellWorkbenchUI.cpp", workbench_cpp)

print("[3/7] Extracting Codex presentation helpers...")

codex_functions = [
    "GetSelectedCodexTitle",
    "GetSelectedCodexSign",
    "GetSelectedCodexDetails",
]

source, codex_block = extract_group(source, codex_functions)

codex_cpp = r'''#include "InnerRealmSubsystem.h"

#include "WorldCodexSubsystem.h"
#include "WorldCodexTypes.h"

''' + codex_block

write(UI_DIR / "CodexUI.cpp", codex_cpp)

print("[4/7] Extracting Rune Canvas renderer/layout...")

source, canvas_block = extract_group(
    source,
    ["RebuildCanvasWidget"],
)

canvas_cpp = r'''#include "InnerRealmSubsystem.h"

#include "SpellGraphSubsystem.h"
#include "WorldCodexSubsystem.h"
#include "WorldCodexTypes.h"

#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "InputCoreTypes.h"

#include "Widgets/Input/SButton.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SConstraintCanvas.h"
#include "Widgets/Layout/SScrollBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Text/STextBlock.h"

''' + canvas_block

write(UI_DIR / "RuneCanvasUI.cpp", canvas_cpp)

print("[5/7] Extracting page host / Slate construction...")

source, host_block = extract_group(
    source,
    [
        "CreateEditorWidget",
        "RemoveEditorWidget",
    ],
)

host_cpp = r'''#include "InnerRealmSubsystem.h"

#include "SpellCastingBindingSubsystem.h"
#include "SpellCreationSubsystem.h"
#include "SpellGraphSubsystem.h"
#include "SpellLoadoutSubsystem.h"
#include "SpellParameterRanges.h"
#include "SpellShapeMath.h"
#include "WorldCodexSubsystem.h"
#include "WorldCodexTypes.h"
#include "UI/InnerRealmShellUI.h"

#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/World.h"
#include "InputCoreTypes.h"

#include "Widgets/Input/SButton.h"
#include "Widgets/Input/SInputKeySelector.h"
#include "Widgets/Input/SSlider.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SScrollBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Text/STextBlock.h"
#include "Styling/CoreStyle.h"

''' + host_block

write(UI_DIR / "InnerRealmPageHost.cpp", host_cpp)

namespace_start = source.find("namespace InnerRealmEditor\n{")
if namespace_start >= 0:
    brace = source.find("{", namespace_start)
    close = find_matching_brace(source, brace)
    end = close + 1
    while end < len(source) and source[end] in " \t\n":
        end += 1
    source = source[:namespace_start] + source[end:]

write(INNER_CPP, source)

print("[6/7] Updating architecture documentation...")

doc = read(ARCH_DOC)

phase3_old = '''### Phase 3 — presentation split
- extract Spell Workbench widget
- extract Codex widget
- extract Rune Canvas widget/layout
- reduce `UInnerRealmSubsystem` to lifecycle/page orchestration'''

phase3_new = '''### Phase 3 — presentation split — IN PROGRESS
- `InnerRealmSubsystem.cpp` now contains realm lifecycle/orchestration rather than page implementation
- Spell Workbench helpers moved to `UI/SpellWorkbenchUI.cpp`
- Codex presentation helpers moved to `UI/CodexUI.cpp`
- Rune Canvas rendering/layout moved to `UI/RuneCanvasUI.cpp`
- shared page construction moved to `UI/InnerRealmPageHost.cpp`
- next step: replace the remaining same-class page methods with dedicated page objects/state models'''

if phase3_new not in doc:
    if phase3_old in doc:
        doc = doc.replace(phase3_old, phase3_new, 1)
    else:
        raise RuntimeError("Could not find Phase 3 section in architecture document.")

if "### v0.15.2" not in doc:
    doc += '''

### v0.15.2
- presentation implementation physically separated from realm lifecycle
- no gameplay behavior or spell semantics changed
- Rune Canvas layout is now isolated in its own source file
- Workbench and Codex presentation helpers are isolated for the next page-object migration
'''

write(ARCH_DOC, doc)

print("[7/7] Verifying presentation/lifecycle separation...")

main = read(INNER_CPP)
workbench = read(UI_DIR / "SpellWorkbenchUI.cpp")
codex = read(UI_DIR / "CodexUI.cpp")
canvas = read(UI_DIR / "RuneCanvasUI.cpp")
host = read(UI_DIR / "InnerRealmPageHost.cpp")

checks = {
    "main no CreateEditorWidget":
        "UInnerRealmSubsystem::CreateEditorWidget" not in main,
    "main no RebuildCanvasWidget":
        "UInnerRealmSubsystem::RebuildCanvasWidget" not in main,
    "main no ReadSpell":
        "UInnerRealmSubsystem::ReadSpell" not in main,
    "main no Codex details":
        "UInnerRealmSubsystem::GetSelectedCodexDetails" not in main,
    "Workbench owns ReadSpell":
        "UInnerRealmSubsystem::ReadSpell" in workbench,
    "Workbench owns dimension logic":
        "UInnerRealmSubsystem::GetDimensionSlider" in workbench,
    "Codex owns details":
        "UInnerRealmSubsystem::GetSelectedCodexDetails" in codex,
    "Canvas owns radial renderer":
        "UInnerRealmSubsystem::RebuildCanvasWidget" in canvas and
        "SConstraintCanvas" in canvas,
    "Host owns page creation":
        "UInnerRealmSubsystem::CreateEditorWidget" in host,
    "Host owns teardown":
        "UInnerRealmSubsystem::RemoveEditorWidget" in host,
    "Shared shell retained":
        "FInnerRealmShellUI::Build" in host,
}

failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise RuntimeError("Verification failed: " + ", ".join(failed))

print()
print("v0.15.2 presentation split applied successfully.")
print()
print("InnerRealm source layout:")
print("  InnerRealmSubsystem.cpp       -> lifecycle / realm orchestration")
print("  UI/InnerRealmPageHost.cpp     -> page creation / teardown")
print("  UI/SpellWorkbenchUI.cpp       -> Workbench presentation helpers")
print("  UI/CodexUI.cpp                -> Codex presentation helpers")
print("  UI/RuneCanvasUI.cpp           -> Canvas rendering/layout")
print("  UI/InnerRealmShellUI.cpp      -> shared navigation / ready slots")
print()
print("No gameplay semantics were changed.")
