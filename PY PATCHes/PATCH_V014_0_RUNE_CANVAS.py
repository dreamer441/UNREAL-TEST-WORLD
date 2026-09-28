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

inner_h = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Public/InnerRealmSubsystem.h"
inner_cpp = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Private/InnerRealmSubsystem.cpp"
inner_build = ROOT / "Plugins/InnerRealm/Source/InnerRealm/InnerRealm.Build.cs"
inner_plugin = ROOT / "Plugins/InnerRealm/InnerRealm.uplugin"

spell_graph_h = ROOT / "Plugins/SpellGraph/Source/SpellGraph/Public/SpellGraphSubsystem.h"
codex_cpp = ROOT / "Plugins/WorldCodex/Source/WorldCodex/Private/WorldCodexSubsystem.cpp"

for required in [
    inner_h, inner_cpp, inner_build, inner_plugin,
    spell_graph_h, codex_cpp
]:
    if not required.exists():
        raise RuntimeError(f"Expected file missing: {required}")

if "ECodexTier" not in read(
    ROOT / "Plugins/WorldCodex/Source/WorldCodex/Public/WorldCodexTypes.h"
):
    raise RuntimeError("v0.14.0 requires working v0.13.5 Codex Grammar first.")

print("[1/6] Wiring SpellGraph into InnerRealm...")
add_build_dependency(inner_build, "SpellGraph")
add_plugin_dependency(inner_plugin, "SpellGraph")

print("[2/6] Adding Rune Canvas state/access to InnerRealm...")
text = read(inner_h)

if "class USpellGraphSubsystem;" not in text:
    text = text.replace(
        "class UWorldCodexSubsystem;\n",
        "class UWorldCodexSubsystem;\nclass USpellGraphSubsystem;\n",
        1)

if "FGuid SelectedCanvasNode" not in text:
    marker = '''    FName SelectedCodexConcept = FName(TEXT("element.earth"));'''
    replacement = '''    FName SelectedCodexConcept = FName(TEXT("element.earth"));
    FGuid SelectedCanvasNode;'''
    text = replace_once(
        text, marker, replacement, "Rune Canvas selected node state")

if "GetSpellGraph() const" not in text:
    marker = '''    UWorldCodexSubsystem* GetWorldCodex() const;

    FText GetSelectedCodexTitle() const;'''
    replacement = '''    UWorldCodexSubsystem* GetWorldCodex() const;
    USpellGraphSubsystem* GetSpellGraph() const;

    void RebuildCanvasWidget();

    FText GetSelectedCodexTitle() const;'''
    text = replace_once(
        text, marker, replacement, "Rune Canvas helper declarations")

# SpellPreview already asks IsSpellWorkbenchVisible(). In v0.14 the preview is
# intentionally visible in both Spell Modifier and Rune Canvas pages.
old_visibility = '''        return bActive && ActivePage == EInnerRealmPage::Spell;'''
new_visibility = '''        return bActive &&
            (ActivePage == EInnerRealmPage::Spell ||
             ActivePage == EInnerRealmPage::Canvas);'''
text = replace_once(
    text,
    old_visibility,
    new_visibility,
    "Spell/Canvas shared preview visibility")

write(inner_h, text)

print("[3/6] Adding SpellGraph access and keeping the 3D preview visible on Canvas...")
text = read(inner_cpp)
text = add_include(
    text,
    '#include "WorldCodexSubsystem.h"',
    '#include "SpellGraphSubsystem.h"',
    "SpellGraph subsystem")

if "USpellGraphSubsystem* UInnerRealmSubsystem::GetSpellGraph() const" not in text:
    marker = '''UWorldCodexSubsystem* UInnerRealmSubsystem::GetWorldCodex() const
{
    UWorld* World = GetWorld();
    return World ? World->GetSubsystem<UWorldCodexSubsystem>() : nullptr;
}
'''
    addition = marker + r'''
USpellGraphSubsystem* UInnerRealmSubsystem::GetSpellGraph() const
{
    UWorld* World = GetWorld();
    return World ? World->GetSubsystem<USpellGraphSubsystem>() : nullptr;
}
'''
    text = replace_once(
        text, marker, addition, "SpellGraph subsystem accessor")

old_preview_visibility = '''        .Visibility_Lambda([this]() { return ActivePage == EInnerRealmPage::Spell ? EVisibility::Visible : EVisibility::Collapsed; })
        .HAlign(HAlign_Right)'''
new_preview_visibility = '''        .Visibility_Lambda([this]()
        {
            return (ActivePage == EInnerRealmPage::Spell ||
                    ActivePage == EInnerRealmPage::Canvas)
                ? EVisibility::Visible
                : EVisibility::Collapsed;
        })
        .HAlign(HAlign_Right)'''
text = replace_once(
    text,
    old_preview_visibility,
    new_preview_visibility,
    "Spell/Canvas preview-frame visibility")

print("[4/6] Replacing the Canvas placeholder with the real Rune Canvas...")
canvas_start = text.find("    CanvasWidget = SNew(SBox)")
if canvas_start == -1:
    if "RebuildCanvasWidget();" not in text:
        raise RuntimeError("Could not locate the v0.13.4 Canvas placeholder.")

canvas_end_marker = "    GEngine->GameViewport->AddViewportWidgetContent(CanvasWidget.ToSharedRef(), 4997);"
canvas_end = text.find(canvas_end_marker, canvas_start) if canvas_start != -1 else -1

if canvas_start != -1 and canvas_end != -1:
    canvas_end += len(canvas_end_marker)
    text = text[:canvas_start] + "    RebuildCanvasWidget();" + text[canvas_end:]

text = text.replace(
    'MakePageButton(EInnerRealmPage::Canvas, TEXT("CANVAS / LATER"))',
    'MakePageButton(EInnerRealmPage::Canvas, TEXT("RUNE CANVAS"))')

# Insert the standalone Canvas builder before RemoveEditorWidget.
if "void UInnerRealmSubsystem::RebuildCanvasWidget()" not in text:
    marker = "\nvoid UInnerRealmSubsystem::RemoveEditorWidget()\n{"
    if marker not in text:
        raise RuntimeError("Could not locate RemoveEditorWidget for Canvas builder insertion.")

    method = r'''
void UInnerRealmSubsystem::RebuildCanvasWidget()
{
    if (!GEngine || !GEngine->GameViewport)
    {
        return;
    }

    if (CanvasWidget.IsValid())
    {
        GEngine->GameViewport->RemoveViewportWidgetContent(
            CanvasWidget.ToSharedRef());
        CanvasWidget.Reset();
    }

    const FSlateColor BlackText(FLinearColor::Black);
    USpellGraphSubsystem* Graph = GetSpellGraph();
    UWorldCodexSubsystem* Codex = GetWorldCodex();

    TSharedRef<SVerticalBox> PaletteList = SNew(SVerticalBox);

    if (Graph && Codex)
    {
        const ECodexCategory CategoryOrder[] =
        {
            ECodexCategory::Element,
            ECodexCategory::Shape,
            ECodexCategory::ShapeParameter,
            ECodexCategory::MaterialProperty,
            ECodexCategory::Spatial,
            ECodexCategory::Pattern,
            ECodexCategory::Motion,
            ECodexCategory::Value
        };

        for (const ECodexCategory Category : CategoryOrder)
        {
            const TArray<const FCodexEntry*> Entries =
                Codex->GetEntriesByCategory(Category);

            bool bAddedHeader = false;

            for (const FCodexEntry* Entry : Entries)
            {
                if (!Entry || !Graph->IsConceptSupported(Entry->ConceptId))
                {
                    continue;
                }

                if (!bAddedHeader)
                {
                    bAddedHeader = true;
                    PaletteList->AddSlot().AutoHeight().Padding(0, 8, 0, 3)
                    [
                        SNew(SBorder)
                        .Padding(FMargin(6.0f, 4.0f))
                        .BorderBackgroundColor(
                            FLinearColor(0.78f, 0.76f, 0.70f, 0.96f))
                        [
                            SNew(STextBlock)
                            .ColorAndOpacity(BlackText)
                            .Text(CodexCategoryToText(Category))
                        ]
                    ];
                }

                const FName EntryId = Entry->ConceptId;
                const FString Glyph = Entry->Sign.Glyph;
                const FString Name = Entry->DisplayName.ToString();

                FString TierLabel = TEXT("II");
                if (Entry->Tier == ECodexTier::TierI) TierLabel = TEXT("I");
                else if (Entry->Tier == ECodexTier::TierIII) TierLabel = TEXT("III");

                const FString ButtonLabel = FString::Printf(
                    TEXT("[ %s ]  %s   / %s"),
                    *Glyph,
                    *Name,
                    *TierLabel);

                PaletteList->AddSlot().AutoHeight().Padding(0, 1)
                [
                    SNew(SButton)
                    .IsFocusable(false)
                    .ContentPadding(FMargin(7.0f, 4.0f))
                    .OnClicked_Lambda([this, EntryId]()
                    {
                        if (USpellGraphSubsystem* CurrentGraph = GetSpellGraph())
                        {
                            const FGuid NewNode =
                                CurrentGraph->AddConcept(
                                    EntryId,
                                    SelectedCanvasNode);

                            if (NewNode.IsValid())
                            {
                                SelectedCanvasNode = NewNode;
                            }
                        }

                        RebuildCanvasWidget();
                        return FReply::Handled();
                    })
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(BlackText)
                        .Text(FText::FromString(ButtonLabel))
                    ]
                ];
            }
        }
    }

    TSharedRef<SVerticalBox> GraphList = SNew(SVerticalBox);

    if (Graph && Codex && Graph->GetNodes().Num() > 0)
    {
        TArray<FSpellGraphNode> OrderedNodes = Graph->GetNodes();
        OrderedNodes.Sort([](
            const FSpellGraphNode& A,
            const FSpellGraphNode& B)
        {
            return A.Order < B.Order;
        });

        for (const FSpellGraphNode& Node : OrderedNodes)
        {
            const FCodexEntry* Entry = Codex->FindEntry(Node.ConceptId);
            if (!Entry)
            {
                continue;
            }

            const int32 Depth = Graph->GetNodeDepth(Node.NodeId);
            const FString Indent =
                FString::ChrN(FMath::Max(Depth, 0) * 3, TEXT(' '));

            const bool bSelected =
                SelectedCanvasNode.IsValid() &&
                SelectedCanvasNode == Node.NodeId;

            FString TierLabel = TEXT("II");
            if (Entry->Tier == ECodexTier::TierI) TierLabel = TEXT("I");
            else if (Entry->Tier == ECodexTier::TierIII) TierLabel = TEXT("III");

            FString NodeLabel;
            if (bSelected)
            {
                NodeLabel = FString::Printf(
                    TEXT("%s[SELECTED]  [ %s ]  %s   / %s"),
                    *Indent,
                    *Entry->Sign.Glyph,
                    *Entry->DisplayName.ToString(),
                    *TierLabel);
            }
            else
            {
                NodeLabel = FString::Printf(
                    TEXT("%s|--  [ %s ]  %s   / %s"),
                    *Indent,
                    *Entry->Sign.Glyph,
                    *Entry->DisplayName.ToString(),
                    *TierLabel);
            }

            const FGuid NodeId = Node.NodeId;

            GraphList->AddSlot().AutoHeight().Padding(0, 2)
            [
                SNew(SButton)
                .IsFocusable(false)
                .ContentPadding(FMargin(8.0f, 5.0f))
                .OnClicked_Lambda([this, NodeId]()
                {
                    SelectedCanvasNode = NodeId;
                    RebuildCanvasWidget();
                    return FReply::Handled();
                })
                [
                    SNew(STextBlock)
                    .ColorAndOpacity(BlackText)
                    .Text(FText::FromString(NodeLabel))
                ]
            ];
        }
    }
    else
    {
        GraphList->AddSlot().AutoHeight().Padding(0, 12)
        [
            SNew(STextBlock)
            .ColorAndOpacity(BlackText)
            .AutoWrapText(true)
            .Text(FText::FromString(
                TEXT("EMPTY CANVAS\n\nStart with the Tier I Earth Sign. Then select a node in the graph and click another Sign on the left to attach it.")))
        ];
    }

    const FText StatusText = Graph
        ? Graph->GetLastCompileResult().Message
        : FText::FromString(TEXT("SpellGraph subsystem unavailable."));

    CanvasWidget = SNew(SBox)
        .Visibility_Lambda([this]()
        {
            return ActivePage == EInnerRealmPage::Canvas
                ? EVisibility::Visible
                : EVisibility::Collapsed;
        })
        .HAlign(HAlign_Left)
        .VAlign(VAlign_Center)
        [
            SNew(SBorder)
            .Padding(FMargin(18.0f))
            .BorderBackgroundColor(
                FLinearColor(0.92f, 0.90f, 0.84f, 0.98f))
            [
                SNew(SBox)
                .WidthOverride(820.0f)
                .HeightOverride(760.0f)
                [
                    SNew(SVerticalBox)

                    + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0, 0, 0, 5)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(BlackText)
                        .Text(FText::FromString(TEXT("RUNE CANVAS / SPELL GRAPH V1")))
                    ]

                    + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 8)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(BlackText)
                        .AutoWrapText(true)
                        .Text(FText::FromString(
                            TEXT("Click-to-place V1: select a graph node, then click a Codex Sign to attach it. This builds the semantic graph directly; drag/drop can replace the interaction later without changing the spell data.")))
                    ]

                    + SVerticalBox::Slot().FillHeight(1.0f)
                    [
                        SNew(SHorizontalBox)

                        + SHorizontalBox::Slot().FillWidth(0.42f).Padding(0, 0, 12, 0)
                        [
                            SNew(SBorder)
                            .Padding(FMargin(8.0f))
                            .BorderBackgroundColor(
                                FLinearColor(0.84f, 0.82f, 0.76f, 0.72f))
                            [
                                SNew(SVerticalBox)

                                + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 5)
                                [
                                    SNew(STextBlock)
                                    .ColorAndOpacity(BlackText)
                                    .Text(FText::FromString(TEXT("CODEX SIGNS / PALETTE")))
                                ]

                                + SVerticalBox::Slot().FillHeight(1.0f)
                                [
                                    SNew(SScrollBox)
                                    + SScrollBox::Slot()
                                    [
                                        PaletteList
                                    ]
                                ]
                            ]
                        ]

                        + SHorizontalBox::Slot().FillWidth(0.58f)
                        [
                            SNew(SBorder)
                            .Padding(FMargin(8.0f))
                            .BorderBackgroundColor(
                                FLinearColor(0.82f, 0.81f, 0.75f, 0.72f))
                            [
                                SNew(SVerticalBox)

                                + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 5)
                                [
                                    SNew(STextBlock)
                                    .ColorAndOpacity(BlackText)
                                    .Text(FText::FromString(TEXT("SEMANTIC GRAPH")))
                                ]

                                + SVerticalBox::Slot().FillHeight(1.0f)
                                [
                                    SNew(SScrollBox)
                                    + SScrollBox::Slot()
                                    [
                                        GraphList
                                    ]
                                ]

                                + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 4)
                                [
                                    SNew(STextBlock)
                                    .ColorAndOpacity(BlackText)
                                    .AutoWrapText(true)
                                    .Text(StatusText)
                                ]

                                + SVerticalBox::Slot().AutoHeight()
                                [
                                    SNew(SHorizontalBox)

                                    + SHorizontalBox::Slot().AutoWidth().Padding(0, 0, 6, 0)
                                    [
                                        SNew(SButton)
                                        .IsFocusable(false)
                                        .OnClicked_Lambda([this]()
                                        {
                                            if (USpellGraphSubsystem* CurrentGraph = GetSpellGraph())
                                            {
                                                CurrentGraph->CompileAndApply();
                                            }
                                            RebuildCanvasWidget();
                                            return FReply::Handled();
                                        })
                                        [
                                            SNew(STextBlock)
                                            .ColorAndOpacity(BlackText)
                                            .Text(FText::FromString(TEXT("COMPILE / APPLY")))
                                        ]
                                    ]

                                    + SHorizontalBox::Slot().AutoWidth().Padding(0, 0, 6, 0)
                                    [
                                        SNew(SButton)
                                        .IsFocusable(false)
                                        .OnClicked_Lambda([this]()
                                        {
                                            if (USpellGraphSubsystem* CurrentGraph = GetSpellGraph())
                                            {
                                                if (SelectedCanvasNode.IsValid())
                                                {
                                                    CurrentGraph->RemoveSubtree(
                                                        SelectedCanvasNode);
                                                }
                                            }

                                            SelectedCanvasNode.Invalidate();
                                            RebuildCanvasWidget();
                                            return FReply::Handled();
                                        })
                                        [
                                            SNew(STextBlock)
                                            .ColorAndOpacity(BlackText)
                                            .Text(FText::FromString(TEXT("REMOVE SELECTED")))
                                        ]
                                    ]

                                    + SHorizontalBox::Slot().AutoWidth()
                                    [
                                        SNew(SButton)
                                        .IsFocusable(false)
                                        .OnClicked_Lambda([this]()
                                        {
                                            if (USpellGraphSubsystem* CurrentGraph = GetSpellGraph())
                                            {
                                                CurrentGraph->ClearGraph();
                                            }

                                            SelectedCanvasNode.Invalidate();
                                            RebuildCanvasWidget();
                                            return FReply::Handled();
                                        })
                                        [
                                            SNew(STextBlock)
                                            .ColorAndOpacity(BlackText)
                                            .Text(FText::FromString(TEXT("CLEAR")))
                                        ]
                                    ]
                                ]
                            ]
                        ]
                    ]

                    + SVerticalBox::Slot().AutoHeight().Padding(0, 8, 0, 0)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(BlackText)
                        .AutoWrapText(true)
                        .Text(FText::FromString(
                            TEXT("V1 scope: one Tier-I root. A valid Earth + Shape graph compiles into the existing FSpellDefinition, so the current 3D preview, ready-spell data and execution pipeline remain reusable. Multiple roots / stacking comes next.")))
                    ]
                ]
            ]
        ];

    GEngine->GameViewport->AddViewportWidgetContent(
        CanvasWidget.ToSharedRef(),
        4997);
}
'''
    text = text.replace(marker, method + marker, 1)

write(inner_cpp, text)

print("[5/6] Verifying the v0.14 Codex extension and Canvas hooks...")
codex_text = read(codex_cpp)
for token in [
    'TEXT("orientation.forward")',
    'TEXT("orientation.right")',
    'TEXT("orientation.up")',
    'TEXT("axis.forward")',
    'TEXT("axis.right")',
    'TEXT("axis.up")'
]:
    if token not in codex_text:
        raise RuntimeError(f"Missing Rune Canvas terminal Codex sign: {token}")

inner_text = read(inner_cpp)
for token in [
    "RebuildCanvasWidget();",
    "RUNE CANVAS / SPELL GRAPH V1",
    "GetSubsystem<USpellGraphSubsystem>()",
    'MakePageButton(EInnerRealmPage::Canvas, TEXT("RUNE CANVAS"))'
]:
    if token not in inner_text:
        raise RuntimeError(f"Missing Rune Canvas integration token: {token}")

print("[6/6] v0.14.0 Rune Canvas V1 patch applied successfully.")
print()
print("Interaction:")
print("  1. Open TAB -> RUNE CANVAS")
print("  2. Click Earth")
print("  3. Select Earth in graph")
print("  4. Click Sphere/Cube/Cone")
print("  5. Select the operator you want to extend")
print("  6. Add modifiers and Tier-III value Signs")
print("  7. Valid graphs auto-compile into the existing spell preview/data")
print()
print("V1 deliberately uses click-to-place. The semantic graph is independent")
print("from UI layout, so free drag/drop can be added later without a rewrite.")
