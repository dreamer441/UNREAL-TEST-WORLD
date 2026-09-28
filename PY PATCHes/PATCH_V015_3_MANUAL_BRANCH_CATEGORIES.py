from pathlib import Path

ROOT = Path(__file__).resolve().parent

INNER_H = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Public/InnerRealmSubsystem.h"
CANVAS_CPP = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Private/UI/RuneCanvasUI.cpp"
ARCH_DOC = ROOT / "Docs/ARCHITECTURE_V1.md"

for path in [INNER_H, CANVAS_CPP, ARCH_DOC]:
    if not path.exists():
        raise RuntimeError(f"Expected file missing: {path}")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


print("[1/5] Verifying v0.15.2 presentation split...")

header = read(INNER_H)
canvas = read(CANVAS_CPP)

required = [
    ("split Canvas source", "void UInnerRealmSubsystem::RebuildCanvasWidget()" in canvas),
    ("radial graph", "SConstraintCanvas" in canvas),
    ("manual expansion state", "ExpandedCanvasNodes" in header),
    ("combined root", "Semantic storage still keeps Earth -> Shape" in canvas),
]

missing = [name for name, ok in required if not ok]
if missing:
    raise RuntimeError(
        "This patch expects the working v0.15.2 project. Missing: "
        + ", ".join(missing)
    )

print("[2/5] Adding Canvas category-navigation state...")

state_marker = '''    TSet<FGuid> ExpandedCanvasNodes;
    FName PendingCanvasElement = NAME_None;'''

state_replacement = '''    TSet<FGuid> ExpandedCanvasNodes;

    /**
     * Rune Canvas palette navigation only.
     * Categories organize Sign selection but are NOT semantic graph nodes.
     */
    int32 SelectedCanvasPaletteCategory = INDEX_NONE;

    FName PendingCanvasElement = NAME_None;'''

if state_replacement not in header:
    if state_marker not in header:
        raise RuntimeError("Could not locate Canvas UI state in InnerRealmSubsystem.h.")
    header = header.replace(state_marker, state_replacement, 1)

write(INNER_H, header)

print("[3/5] Rebuilding the left Canvas palette as category -> Sign navigation...")

palette_start_marker = '''    // ------------------------------------------------------------------
    // CODEX PALETTE
    // ------------------------------------------------------------------'''

layout_marker = '''    // ------------------------------------------------------------------
    // RADIAL LAYOUT
    // ------------------------------------------------------------------'''

palette_start = canvas.find(palette_start_marker)
layout_start = canvas.find(layout_marker, palette_start)

if palette_start < 0 or layout_start < 0:
    raise RuntimeError("Could not locate Rune Canvas palette/layout boundaries.")

new_palette = r'''    // ------------------------------------------------------------------
    // CODEX PALETTE
    //
    // Categories are presentation/navigation only. They do NOT become spell
    // graph nodes and therefore never change spell meaning.
    //
    // Flow:
    //      category -> Sign
    //
    // Example:
    //      SHAPE PARAMETERS -> Cube X / Cube Y / Cube Z
    //
    // This keeps the graph semantic while preventing the palette from becoming
    // one long, unclear list of every available concept.
    // ------------------------------------------------------------------
    TSharedRef<SVerticalBox> PaletteList = SNew(SVerticalBox);

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

    auto EntryMatchesCurrentShape =
        [ShapeNode](const FCodexEntry& Entry) -> bool
    {
        if (Entry.Category != ECodexCategory::ShapeParameter)
        {
            return true;
        }

        // Shape-parameter choices only become useful after Shape exists.
        if (!ShapeNode)
        {
            return false;
        }

        const FString Id = Entry.ConceptId.ToString();

        if (ShapeNode->ConceptId == FName(TEXT("shape.sphere")))
        {
            return Id.StartsWith(TEXT("shape.sphere."));
        }

        if (ShapeNode->ConceptId == FName(TEXT("shape.cube")))
        {
            return Id.StartsWith(TEXT("shape.cube."));
        }

        if (ShapeNode->ConceptId == FName(TEXT("shape.cone")))
        {
            return Id.StartsWith(TEXT("shape.cone."));
        }

        return false;
    };

    auto CategoryHasVisibleEntries =
        [Graph, Codex, &EntryMatchesCurrentShape](
            const ECodexCategory Category) -> bool
    {
        if (!Graph || !Codex)
        {
            return false;
        }

        const TArray<const FCodexEntry*> Entries =
            Codex->GetEntriesByCategory(Category);

        for (const FCodexEntry* Entry : Entries)
        {
            if (Entry &&
                Graph->IsConceptSupported(Entry->ConceptId) &&
                EntryMatchesCurrentShape(*Entry))
            {
                return true;
            }
        }

        return false;
    };

    auto HandleEntryChosen =
        [this](const FName EntryId)
    {
        USpellGraphSubsystem* CurrentGraph = GetSpellGraph();
        UWorldCodexSubsystem* CurrentCodex = GetWorldCodex();

        if (!CurrentGraph || !CurrentCodex)
        {
            return;
        }

        const FCodexEntry* ChosenEntry =
            CurrentCodex->FindEntry(EntryId);

        if (!ChosenEntry)
        {
            return;
        }

        const FSpellGraphNode* CurrentRoot = nullptr;

        for (const FSpellGraphNode& Candidate :
             CurrentGraph->GetNodes())
        {
            if (!Candidate.ParentNodeId.IsValid())
            {
                CurrentRoot = &Candidate;
                break;
            }
        }

        // --------------------------------------------------------------
        // Foundation construction:
        // Element + Shape form the single visual construction root.
        // These two initial choices do not require an attachment line.
        // --------------------------------------------------------------
        if (ChosenEntry->Category == ECodexCategory::Element)
        {
            if (CurrentGraph->GetNodes().Num() == 0)
            {
                PendingCanvasElement = EntryId;
                SelectedCanvasNode.Invalidate();
                ExpandedCanvasNodes.Reset();

                // Return to category selection so Shape is the next deliberate
                // category choice.
                SelectedCanvasPaletteCategory = INDEX_NONE;
            }

            RebuildCanvasWidget();
            return;
        }

        if (ChosenEntry->Category == ECodexCategory::Shape)
        {
            if (CurrentGraph->GetNodes().Num() == 0)
            {
                if (PendingCanvasElement ==
                    FName(TEXT("element.earth")))
                {
                    const FGuid NewRoot =
                        CurrentGraph->AddConcept(
                            PendingCanvasElement,
                            FGuid());

                    if (NewRoot.IsValid())
                    {
                        const FGuid NewShape =
                            CurrentGraph->AddConcept(
                                EntryId,
                                NewRoot);

                        if (NewShape.IsValid())
                        {
                            PendingCanvasElement = NAME_None;
                            SelectedCanvasNode = NewRoot;
                            ExpandedCanvasNodes.Reset();
                            SelectedCanvasPaletteCategory = INDEX_NONE;
                        }
                        else
                        {
                            CurrentGraph->ClearGraph();
                        }
                    }
                }

                RebuildCanvasWidget();
                return;
            }

            // Replace only the Shape part of the existing composite root.
            if (CurrentRoot)
            {
                const FGuid CurrentRootId =
                    CurrentRoot->NodeId;

                FGuid OldShapeId;

                for (const FSpellGraphNode& Candidate :
                     CurrentGraph->GetNodes())
                {
                    if (Candidate.ParentNodeId !=
                        CurrentRootId)
                    {
                        continue;
                    }

                    const FCodexEntry* CandidateEntry =
                        CurrentCodex->FindEntry(
                            Candidate.ConceptId);

                    if (CandidateEntry &&
                        CandidateEntry->Category ==
                            ECodexCategory::Shape)
                    {
                        OldShapeId = Candidate.NodeId;
                        break;
                    }
                }

                if (OldShapeId.IsValid())
                {
                    CurrentGraph->RemoveSubtree(
                        OldShapeId);
                }

                const FGuid NewShape =
                    CurrentGraph->AddConcept(
                        EntryId,
                        CurrentRootId);

                if (NewShape.IsValid())
                {
                    SelectedCanvasNode = CurrentRootId;
                    ExpandedCanvasNodes.Remove(CurrentRootId);
                    SelectedCanvasPaletteCategory = INDEX_NONE;
                }
            }

            RebuildCanvasWidget();
            return;
        }

        if (!CurrentRoot)
        {
            RebuildCanvasWidget();
            return;
        }

        // --------------------------------------------------------------
        // Every ordinary attachment requires a line opened manually with a
        // double-click. Merely selecting a Sign never creates another line.
        // --------------------------------------------------------------
        FGuid VisualAttachSource = SelectedCanvasNode;

        if (!VisualAttachSource.IsValid())
        {
            VisualAttachSource = CurrentRoot->NodeId;
        }

        if (!ExpandedCanvasNodes.Contains(
                VisualAttachSource))
        {
            if (GEngine)
            {
                GEngine->AddOnScreenDebugMessage(
                    -1,
                    1.8f,
                    FColor::Yellow,
                    TEXT("Double-click a non-terminal Sign first to open an attachment line."));
            }

            RebuildCanvasWidget();
            return;
        }

        FGuid AttachParent = VisualAttachSource;

        FGuid CurrentShapeId;

        for (const FSpellGraphNode& Candidate :
             CurrentGraph->GetNodes())
        {
            if (Candidate.ParentNodeId !=
                CurrentRoot->NodeId)
            {
                continue;
            }

            const FCodexEntry* CandidateEntry =
                CurrentCodex->FindEntry(
                    Candidate.ConceptId);

            if (CandidateEntry &&
                CandidateEntry->Category ==
                    ECodexCategory::Shape)
            {
                CurrentShapeId = Candidate.NodeId;
                break;
            }
        }

        // Shape parameters visually attach to the combined Earth+Shape node,
        // but remain semantic children of the hidden Shape concept.
        if (ChosenEntry->Category ==
                ECodexCategory::ShapeParameter &&
            VisualAttachSource ==
                CurrentRoot->NodeId &&
            CurrentShapeId.IsValid())
        {
            AttachParent = CurrentShapeId;
        }

        const FGuid NewNode =
            CurrentGraph->AddConcept(
                EntryId,
                AttachParent);

        if (NewNode.IsValid())
        {
            // IMPORTANT: branch expansion is one-shot.
            //
            // Filling a manually opened line consumes it. No new empty line
            // appears automatically. To add another sibling branch, the user
            // must double-click the source Sign again.
            ExpandedCanvasNodes.Remove(
                VisualAttachSource);

            if (CurrentShapeId.IsValid() &&
                AttachParent == CurrentShapeId)
            {
                SelectedCanvasNode =
                    CurrentRoot->NodeId;
            }
            else
            {
                SelectedCanvasNode =
                    VisualAttachSource;
            }

            // One Sign was selected. Return to category navigation for the
            // next deliberate choice.
            SelectedCanvasPaletteCategory =
                INDEX_NONE;
        }

        RebuildCanvasWidget();
    };

    if (Graph && Codex)
    {
        bool bHasActiveCategory = false;
        ECodexCategory ActiveCategory =
            ECodexCategory::Element;

        for (const ECodexCategory Category :
             CategoryOrder)
        {
            if (SelectedCanvasPaletteCategory ==
                static_cast<int32>(Category))
            {
                ActiveCategory = Category;
                bHasActiveCategory = true;
                break;
            }
        }

        if (!bHasActiveCategory)
        {
            PaletteList->AddSlot()
                .AutoHeight()
                .Padding(0, 0, 0, 8)
            [
                SNew(STextBlock)
                .ColorAndOpacity(BlackText)
                .AutoWrapText(true)
                .Text(FText::FromString(
                    TEXT("Choose a category first. Categories organize Signs; they do not become graph nodes.")))
            ];

            for (const ECodexCategory Category :
                 CategoryOrder)
            {
                if (!CategoryHasVisibleEntries(Category))
                {
                    continue;
                }

                PaletteList->AddSlot()
                    .AutoHeight()
                    .Padding(0, 2)
                [
                    SNew(SButton)
                    .IsFocusable(false)
                    .ContentPadding(FMargin(8.0f, 7.0f))
                    .OnClicked_Lambda(
                        [this, Category]()
                        {
                            SelectedCanvasPaletteCategory =
                                static_cast<int32>(Category);

                            RebuildCanvasWidget();
                            return FReply::Handled();
                        })
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(BlackText)
                        .Text(CodexCategoryToText(Category))
                    ]
                ];
            }
        }
        else
        {
            PaletteList->AddSlot()
                .AutoHeight()
                .Padding(0, 0, 0, 7)
            [
                SNew(SButton)
                .IsFocusable(false)
                .ContentPadding(FMargin(7.0f, 5.0f))
                .OnClicked_Lambda([this]()
                {
                    SelectedCanvasPaletteCategory =
                        INDEX_NONE;

                    RebuildCanvasWidget();
                    return FReply::Handled();
                })
                [
                    SNew(STextBlock)
                    .ColorAndOpacity(BlackText)
                    .Text(FText::FromString(
                        TEXT("<  CATEGORIES")))
                ]
            ];

            PaletteList->AddSlot()
                .AutoHeight()
                .Padding(0, 0, 0, 5)
            [
                SNew(SBorder)
                .Padding(FMargin(7.0f, 5.0f))
                .BorderBackgroundColor(
                    FLinearColor(
                        0.78f,
                        0.76f,
                        0.70f,
                        0.96f))
                [
                    SNew(STextBlock)
                    .ColorAndOpacity(BlackText)
                    .Text(CodexCategoryToText(
                        ActiveCategory))
                ]
            ];

            const TArray<const FCodexEntry*> Entries =
                Codex->GetEntriesByCategory(
                    ActiveCategory);

            bool bAddedAny = false;

            for (const FCodexEntry* Entry :
                 Entries)
            {
                if (!Entry ||
                    !Graph->IsConceptSupported(
                        Entry->ConceptId) ||
                    !EntryMatchesCurrentShape(*Entry))
                {
                    continue;
                }

                bAddedAny = true;

                const FName EntryId =
                    Entry->ConceptId;

                const FString ButtonLabel =
                    FString::Printf(
                        TEXT("[ %s ]  %s"),
                        *Entry->Sign.Glyph,
                        *Entry->DisplayName.ToString());

                PaletteList->AddSlot()
                    .AutoHeight()
                    .Padding(0, 2)
                [
                    SNew(SButton)
                    .IsFocusable(false)
                    .ContentPadding(
                        FMargin(7.0f, 6.0f))
                    .ToolTipText(
                        Entry->Description)
                    .OnClicked_Lambda(
                        [HandleEntryChosen, EntryId]()
                        {
                            HandleEntryChosen(EntryId);
                            return FReply::Handled();
                        })
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(BlackText)
                        .Text(FText::FromString(
                            ButtonLabel))
                    ]
                ];
            }

            if (!bAddedAny)
            {
                PaletteList->AddSlot()
                    .AutoHeight()
                    .Padding(0, 6)
                [
                    SNew(STextBlock)
                    .ColorAndOpacity(BlackText)
                    .AutoWrapText(true)
                    .Text(FText::FromString(
                        TEXT("No valid Signs are available in this category for the current construction.")))
                ];
            }
        }
    }

'''

canvas = (
    canvas[:palette_start]
    + new_palette
    + canvas[layout_start:]
)

print("[4/5] Making branch expansion explicitly one-shot...")

# Double-click already controls ExpandedCanvasNodes. Tighten the explanatory
# comment so the source matches the new behavior.
old_comment = '''        // Double-clicking opens exactly one empty branch. Once filled,
        // another empty branch remains available around the same node.
        if (!bTerminal &&
            ExpandedCanvasNodes.Contains(NodeId))'''

new_comment = '''        // Double-clicking opens exactly one pending empty branch.
        // Filling that branch removes NodeId from ExpandedCanvasNodes, so no
        // replacement line appears until the user double-clicks again.
        if (!bTerminal &&
            ExpandedCanvasNodes.Contains(NodeId))'''

if old_comment in canvas:
    canvas = canvas.replace(
        old_comment,
        new_comment,
        1,
    )
elif new_comment not in canvas:
    raise RuntimeError(
        "Could not locate radial pending-branch comment."
    )

# Clear should also reset palette navigation.
clear_marker = '''                                            PendingCanvasElement = NAME_None;
                                            SelectedCanvasNode.Invalidate();
                                            ExpandedCanvasNodes.Reset();

                                            RebuildCanvasWidget();'''

clear_replacement = '''                                            PendingCanvasElement = NAME_None;
                                            SelectedCanvasNode.Invalidate();
                                            ExpandedCanvasNodes.Reset();
                                            SelectedCanvasPaletteCategory =
                                                INDEX_NONE;

                                            RebuildCanvasWidget();'''

if clear_replacement not in canvas:
    if clear_marker not in canvas:
        raise RuntimeError(
            "Could not locate Canvas CLEAR state reset."
        )
    canvas = canvas.replace(
        clear_marker,
        clear_replacement,
        1,
    )

# Update the visible instruction so the interaction contract is unambiguous.
canvas = canvas.replace(
    'TEXT("SPELL GRAPH — DOUBLE CLICK A NON-TERMINAL SIGN TO OPEN ITS NEXT RADIAL BRANCH")',
    'TEXT("SPELL GRAPH — DOUBLE CLICK A SIGN TO OPEN ONE BRANCH; FILLING IT DOES NOT CREATE ANOTHER")',
)

write(CANVAS_CPP, canvas)

print("[5/5] Updating architecture note and verifying behavior contract...")

doc = read(ARCH_DOC)

if "### v0.15.3" not in doc:
    doc += '''

### v0.15.3
- Rune Canvas branch creation is manual and one-shot
- a line exists only after the source Sign is double-clicked
- filling a line consumes that pending branch; another line requires another double-click
- Canvas Sign palette is category-first
- categories are UI navigation only, never semantic spell graph nodes
- Shape Parameters are filtered to the active Shape (for example Cube -> X/Y/Z)
'''

write(ARCH_DOC, doc)

header = read(INNER_H)
canvas = read(CANVAS_CPP)

checks = {
    "palette category state":
        "SelectedCanvasPaletteCategory" in header,
    "category-first text":
        "Choose a category first." in canvas,
    "shape parameter filtering":
        'Id.StartsWith(TEXT("shape.cube."))' in canvas and
        'Id.StartsWith(TEXT("shape.sphere."))' in canvas and
        'Id.StartsWith(TEXT("shape.cone."))' in canvas,
    "manual branch requirement":
        "Double-click a non-terminal Sign first to open an attachment line." in canvas,
    "one-shot consume":
        "ExpandedCanvasNodes.Remove(\n                VisualAttachSource);" in canvas,
    "no automatic replacement description":
        "does not create another" in canvas,
    "category reset on clear":
        "SelectedCanvasPaletteCategory =\n                                                INDEX_NONE;" in canvas,
}

failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise RuntimeError(
        "Verification failed: " + ", ".join(failed)
    )

print()
print("v0.15.3 Canvas interaction cleanup applied.")
print()
print("New branch rule:")
print("  double-click Sign -> one empty line")
print("  choose category -> choose Sign -> attach")
print("  line is consumed")
print("  no new line until the source Sign is double-clicked again")
print()
print("Palette rule:")
print("  Categories are navigation only, not spell graph nodes.")
print("  Shape Parameters filters to the active Shape.")
