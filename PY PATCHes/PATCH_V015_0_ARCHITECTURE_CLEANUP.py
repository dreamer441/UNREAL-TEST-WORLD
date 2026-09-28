from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
EXPECTED_BASE = "58acd09"

INNER_H = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Public/InnerRealmSubsystem.h"
INNER_CPP = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Private/InnerRealmSubsystem.cpp"
GRAPH_CPP = ROOT / "Plugins/SpellGraph/Source/SpellGraph/Private/SpellGraphSubsystem.cpp"
SHELL_H = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Private/UI/InnerRealmShellUI.h"
SHELL_CPP = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Private/UI/InnerRealmShellUI.cpp"
COMPILER_H = ROOT / "Plugins/SpellGraph/Source/SpellGraph/Public/SpellGraphCompiler.h"
COMPILER_CPP = ROOT / "Plugins/SpellGraph/Source/SpellGraph/Private/SpellGraphCompiler.cpp"
ARCH_DOC = ROOT / "Docs/ARCHITECTURE_V1.md"

for path in [INNER_H, INNER_CPP, GRAPH_CPP, SHELL_H, SHELL_CPP, COMPILER_H, COMPILER_CPP, ARCH_DOC]:
    if not path.exists():
        raise RuntimeError(f"Expected file missing: {path}")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"Could not find expected block for: {label}")
    return text.replace(old, new, 1)


def regex_replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"Could not find exactly one expected block for: {label} (found {count})")
    return updated


# Advisory base check. Anchors below are still the real compatibility gate.
try:
    head = subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        text=True,
        stderr=subprocess.DEVNULL,
    ).strip()
    if not head.startswith(EXPECTED_BASE):
        print(f"WARNING: expected snapshot base {EXPECTED_BASE}, current HEAD is {head}.")
        print("Continuing only if all source anchors still match.\n")
except Exception:
    pass

print("[1/6] Establishing the shared InnerRealm shell...")

htext = read(INNER_H)
if "TSharedPtr<SWidget> ShellWidget;" not in htext:
    htext = replace_once(
        htext,
        "    TSharedPtr<SWidget> NavigationWidget;",
        "    TSharedPtr<SWidget> ShellWidget;",
        "InnerRealm shell member",
    )
write(INNER_H, htext)

text = read(INNER_CPP)
if '#include "UI/InnerRealmShellUI.h"' not in text:
    text = replace_once(
        text,
        '#include "SpellLoadoutSubsystem.h"',
        '#include "SpellLoadoutSubsystem.h"\n#include "UI/InnerRealmShellUI.h"',
        "InnerRealm shell include",
    )

print("[2/6] Moving ready spell slots out of the Preview page...")

# The old page-local slot lambda is no longer needed.
if "auto MakeReadySlot" in text:
    text = regex_replace_once(
        text,
        r"\n    auto MakeReadySlot = \[this, BlackText\].*?\n    };\n\n    EditorWidget = SNew\(SBox\)",
        "\n\n    EditorWidget = SNew(SBox)",
        "old page-local ready slot builder",
    )

old_ready_block = '''                    + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0, 0, 0, 5)
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

'''
if old_ready_block in text:
    text = text.replace(old_ready_block, "", 1)
elif "READY SPELL SLOTS  -  click to save current spell" in text:
    raise RuntimeError("Ready-slot preview block changed unexpectedly.")

# Preview is now genuinely display-only, so neither the root nor descendants need hit testing.
old_preview_visibility = '''            // The preview is display-only. When Rune Canvas is open it sits
            // above the Canvas in the viewport Z-order, so Visible would put
            // its full-screen root into the hit-test path and swallow clicks
            // intended for Canvas buttons underneath.
            //
            // HitTestInvisible keeps the 3D preview/frame visible while
            // allowing pointer input to pass through to the Rune Canvas.
            return (ActivePage == EInnerRealmPage::Spell ||
                    ActivePage == EInnerRealmPage::Canvas)
                ? EVisibility::SelfHitTestInvisible
                : EVisibility::Collapsed;'''
new_preview_visibility = '''            // Preview is presentation-only. Shared interactive controls now live
            // in the InnerRealm shell above every page, so the preview can be
            // completely transparent to mouse hit testing.
            return (ActivePage == EInnerRealmPage::Spell ||
                    ActivePage == EInnerRealmPage::Canvas)
                ? EVisibility::HitTestInvisible
                : EVisibility::Collapsed;'''
text = replace_once(
    text,
    old_preview_visibility,
    new_preview_visibility,
    "display-only preview hit testing",
)

print("[3/6] Replacing page-local navigation with one shared shell...")

if "auto MakePageButton" in text:
    text = regex_replace_once(
        text,
        r"\n    auto MakePageButton = \[this, BlackText\].*?\n    };\n\n    TSharedRef<SVerticalBox> CodexList",
        "\n\n    TSharedRef<SVerticalBox> CodexList",
        "old page navigation builder",
    )

old_navigation = '''    NavigationWidget = SNew(SBox)
        .HAlign(HAlign_Center)
        .VAlign(VAlign_Top)
        [
            SNew(SBorder)
            .Padding(FMargin(10.0f, 8.0f))
            .BorderBackgroundColor(FLinearColor(0.92f, 0.90f, 0.84f, 0.98f))
            [
                SNew(SHorizontalBox)
                + SHorizontalBox::Slot().AutoWidth().Padding(4, 0)
                [ MakePageButton(EInnerRealmPage::Spell, TEXT("SPELL MODIFIER")) ]
                + SHorizontalBox::Slot().AutoWidth().Padding(4, 0)
                [ MakePageButton(EInnerRealmPage::Codex, TEXT("CODEX")) ]
                + SHorizontalBox::Slot().AutoWidth().Padding(4, 0)
                [ MakePageButton(EInnerRealmPage::Canvas, TEXT("RUNE CANVAS")) ]
            ]
        ];

    GEngine->GameViewport->AddViewportWidgetContent(NavigationWidget.ToSharedRef(), 5002);'''

new_shell = '''    FInnerRealmShellCallbacks ShellCallbacks;

    ShellCallbacks.GetActivePage = [this]()
    {
        return ActivePage;
    };

    ShellCallbacks.SetActivePage = [this](const EInnerRealmPage Page)
    {
        ActivePage = Page;
    };

    ShellCallbacks.SavePreparedSlot = [this](const int32 SlotIndex)
    {
        UWorld* World = GetWorld();
        USpellCreationSubsystem* Creation = GetSpellCreation();
        USpellLoadoutSubsystem* Loadout =
            World ? World->GetSubsystem<USpellLoadoutSubsystem>() : nullptr;

        if (Creation && Loadout)
        {
            Loadout->SaveSlot(
                SlotIndex,
                Creation->GetStoredGenericSpellDefinition());
            Loadout->EquipSlot(SlotIndex);
        }
    };

    ShellCallbacks.IsPreparedSlotOccupied = [this](const int32 SlotIndex)
    {
        UWorld* World = GetWorld();
        const USpellLoadoutSubsystem* Loadout =
            World ? World->GetSubsystem<USpellLoadoutSubsystem>() : nullptr;
        return Loadout && Loadout->IsSlotOccupied(SlotIndex);
    };

    ShellWidget = FInnerRealmShellUI::Build(ShellCallbacks);

    // Shared shell is always above page content. Canvas/Workbench/Codex can no
    // longer make the prepared-spell buttons unreachable through Z-order.
    GEngine->GameViewport->AddViewportWidgetContent(
        ShellWidget.ToSharedRef(),
        5003);'''

text = replace_once(
    text,
    old_navigation,
    new_shell,
    "shared InnerRealm shell",
)

# Remove/reset lifecycle now refers to the shell, not the old navigation widget.
text = text.replace("NavigationWidget", "ShellWidget")
write(INNER_CPP, text)

print("[4/6] Extracting graph compilation from graph storage/validation...")

graph = read(GRAPH_CPP)
if '#include "SpellGraphCompiler.h"' not in graph:
    graph = replace_once(
        graph,
        '#include "SpellGraphSubsystem.h"',
        '#include "SpellGraphSubsystem.h"\n#include "SpellGraphCompiler.h"',
        "SpellGraph compiler include",
    )

new_compile_method = '''FSpellGraphCompileResult USpellGraphSubsystem::CompileAndApply()
{
    UWorld* World = GetWorld();
    UWorldCodexSubsystem* Codex = GetCodex();
    USpellCreationSubsystem* SpellCreation =
        World ? World->GetSubsystem<USpellCreationSubsystem>() : nullptr;

    if (!World || !Codex || !SpellCreation)
    {
        FSpellGraphCompileResult Result;
        Result.Message = FText::FromString(
            TEXT("Compiler unavailable: missing world, Codex, or SpellCreation."));
        LastCompileResult = Result;
        return Result;
    }

    FSpellGraphCompileResult Result =
        FSpellGraphCompiler::Compile(Nodes, *Codex);

    if (Result.bSuccess)
    {
        SpellCreation->SetStoredGenericSpellDefinition(
            Result.Definition);
    }

    LastCompileResult = Result;
    return Result;
}
'''

graph = regex_replace_once(
    graph,
    r"FSpellGraphCompileResult USpellGraphSubsystem::CompileAndApply\(\)\n\{.*\n\}\s*$",
    new_compile_method,
    "SpellGraph CompileAndApply extraction",
)
write(GRAPH_CPP, graph)

print("[5/6] Verifying architectural boundaries...")

htext = read(INNER_H)
text = read(INNER_CPP)
graph = read(GRAPH_CPP)

checks = {
    "ShellWidget member": "TSharedPtr<SWidget> ShellWidget;" in htext,
    "Shell UI include": '#include "UI/InnerRealmShellUI.h"' in text,
    "Shared prepared-slot callback": "ShellCallbacks.SavePreparedSlot" in text,
    "Shared shell Z-order": "5003" in text,
    "Preview is display-only": "EVisibility::HitTestInvisible" in text,
    "Old preview ready bar removed": "READY SPELL SLOTS  -  click to save current spell" not in text,
    "Old MakeReadySlot removed": "auto MakeReadySlot" not in text,
    "Old MakePageButton removed": "auto MakePageButton" not in text,
    "Compiler delegation": "FSpellGraphCompiler::Compile(Nodes, *Codex)" in graph,
    "Old compile implementation removed": "VALID / APPLIED: EARTH -> %s" not in graph,
}

failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise RuntimeError("Verification failed: " + ", ".join(failed))

print("[6/6] v0.15.0 architecture cleanup phase 1 applied successfully.")
print()
print("What changed:")
print("  - READY SPELLS moved into one shared InnerRealm shell.")
print("  - Slot buttons are no longer children of the preview page.")
print("  - Preview is fully display-only for hit testing.")
print("  - Graph storage/validation delegates compilation to SpellGraphCompiler.")
print("  - Docs/ARCHITECTURE_V1.md records ownership and next migration phases.")
