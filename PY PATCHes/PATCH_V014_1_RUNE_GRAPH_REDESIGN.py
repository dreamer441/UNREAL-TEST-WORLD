from pathlib import Path

ROOT = Path(__file__).resolve().parent
CPP = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Private/InnerRealmSubsystem.cpp"

if not CPP.exists():
    raise RuntimeError(f"Expected file missing: {CPP}")

text = CPP.read_text(encoding="utf-8").replace("\r\n", "\n")

print("[1/3] Restoring ready-slot interaction while keeping Canvas clicks working...")

# v0.14.0.1 used HitTestInvisible to stop the preview overlay swallowing Canvas
# clicks, but that also disabled hit testing for the preview's child controls
# (including the ready-spell slot buttons). SelfHitTestInvisible is the correct
# Slate visibility here: the full-screen alignment root ignores mouse input,
# while its actual child buttons remain interactive.
old_visibility = '''                ? EVisibility::HitTestInvisible
                : EVisibility::Collapsed;'''
new_visibility = '''                ? EVisibility::SelfHitTestInvisible
                : EVisibility::Collapsed;'''

if new_visibility not in text:
    if old_visibility not in text:
        raise RuntimeError(
            "Could not find the v0.14.0.1 preview hit-test visibility block."
        )
    text = text.replace(old_visibility, new_visibility, 1)

print("[2/3] Replacing the sentence-style Canvas graph with a branching sign graph...")

start = text.find("void UInnerRealmSubsystem::RebuildCanvasWidget()")
end = text.find("\nvoid UInnerRealmSubsystem::RemoveEditorWidget()", start)

if start == -1 or end == -1:
    raise RuntimeError(
        "Could not locate the v0.14.0 Rune Canvas builder method."
    )

new_method = r'''void UInnerRealmSubsystem::RebuildCanvasWidget()
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

    // ------------------------------------------------------------------
    // LEFT: CODEX SIGN PALETTE
    // Names remain here for learning/readability.
    // The actual graph on the right intentionally shows SIGNS ONLY.
    // ------------------------------------------------------------------
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
                if (Entry->Tier == ECodexTier::TierI)
                {
                    TierLabel = TEXT("I");
                }
                else if (Entry->Tier == ECodexTier::TierIII)
                {
                    TierLabel = TEXT("III");
                }

                const FString ButtonLabel = FString::Printf(
                    TEXT("[ %s ]  %s   / TIER %s"),
                    *Glyph,
                    *Name,
                    *TierLabel);

                PaletteList->AddSlot().AutoHeight().Padding(0, 1)
                [
                    SNew(SButton)
                    .IsFocusable(false)
                    .ContentPadding(FMargin(7.0f, 4.0f))
                    .ToolTipText(Entry->Description)
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

    // ------------------------------------------------------------------
    // RIGHT: BRANCHING SIGN GRAPH
    //
    // Node semantics:
    // - graph node itself displays only the Sign
    // - click a Sign to choose it as the attachment parent
    // - every Tier I / II node always owns one EMPTY child socket
    // - attach a child -> a fresh EMPTY socket remains beside it
    // - Tier III is terminal and therefore has no outgoing socket
    //
    // This is already the structural behavior we want for the later
    // free-position Rune Canvas. Only the visual placement mechanism changes.
    // ------------------------------------------------------------------
    TSharedRef<SWidget> GraphTree =
        SNew(STextBlock)
        .ColorAndOpacity(BlackText)
        .Text(FText::FromString(TEXT("EMPTY")));

    if (Graph && Codex && Graph->GetNodes().Num() > 0)
    {
        const FSpellGraphNode* RootNode = nullptr;

        for (const FSpellGraphNode& Candidate : Graph->GetNodes())
        {
            if (!Candidate.ParentNodeId.IsValid())
            {
                RootNode = &Candidate;
                break;
            }
        }

        if (RootNode)
        {
            TFunction<TSharedRef<SWidget>(const FGuid&)> BuildNodeTree;

            BuildNodeTree =
                [this, Graph, Codex, BlackText, &BuildNodeTree](
                    const FGuid& NodeId) -> TSharedRef<SWidget>
            {
                const FSpellGraphNode* Node = Graph->FindNode(NodeId);
                if (!Node)
                {
                    return SNew(SBox);
                }

                const FCodexEntry* Entry =
                    Codex->FindEntry(Node->ConceptId);

                if (!Entry)
                {
                    return SNew(SBox);
                }

                TArray<const FSpellGraphNode*> Children;

                for (const FSpellGraphNode& Candidate : Graph->GetNodes())
                {
                    if (Candidate.ParentNodeId == NodeId)
                    {
                        Children.Add(&Candidate);
                    }
                }

                Children.Sort([](
                    const FSpellGraphNode& A,
                    const FSpellGraphNode& B)
                {
                    return A.Order < B.Order;
                });

                const bool bSelected =
                    SelectedCanvasNode.IsValid() &&
                    SelectedCanvasNode == NodeId;

                const FLinearColor NodeColor = bSelected
                    ? FLinearColor(0.66f, 0.82f, 0.66f, 0.98f)
                    : FLinearColor(0.84f, 0.82f, 0.76f, 0.96f);

                TSharedRef<SVerticalBox> NodeColumn =
                    SNew(SVerticalBox);

                // SIGN ONLY. Name is available via tooltip and palette.
                NodeColumn->AddSlot()
                    .AutoHeight()
                    .HAlign(HAlign_Center)
                    .Padding(3.0f)
                [
                    SNew(SButton)
                    .IsFocusable(false)
                    .ContentPadding(FMargin(10.0f, 8.0f))
                    .ButtonColorAndOpacity(NodeColor)
                    .ToolTipText(FText::FromString(FString::Printf(
                        TEXT("%s\n%s\n%s"),
                        *Entry->DisplayName.ToString(),
                        *CodexTierToText(Entry->Tier).ToString(),
                        *Entry->Description.ToString())))
                    .OnClicked_Lambda([this, NodeId]()
                    {
                        SelectedCanvasNode = NodeId;
                        RebuildCanvasWidget();
                        return FReply::Handled();
                    })
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(BlackText)
                        .Justification(ETextJustify::Center)
                        .Text(FText::FromString(Entry->Sign.Glyph))
                    ]
                ];

                // Tier III is terminal: absolutely no outgoing line/socket.
                if (Entry->Tier == ECodexTier::TierIII)
                {
                    return NodeColumn;
                }

                // One line always leaves every non-terminal Sign.
                NodeColumn->AddSlot()
                    .AutoHeight()
                    .HAlign(HAlign_Center)
                    .Padding(0.0f)
                [
                    SNew(STextBlock)
                    .ColorAndOpacity(BlackText)
                    .Text(FText::FromString(TEXT("|")))
                ];

                TSharedRef<SHorizontalBox> BranchRow =
                    SNew(SHorizontalBox);

                // Existing children become real branches.
                for (const FSpellGraphNode* Child : Children)
                {
                    if (!Child)
                    {
                        continue;
                    }

                    const FGuid ChildId = Child->NodeId;

                    BranchRow->AddSlot()
                        .AutoWidth()
                        .VAlign(VAlign_Top)
                        .Padding(6.0f, 0.0f)
                    [
                        SNew(SVerticalBox)

                        + SVerticalBox::Slot()
                        .AutoHeight()
                        .HAlign(HAlign_Center)
                        [
                            SNew(STextBlock)
                            .ColorAndOpacity(BlackText)
                            .Text(FText::FromString(TEXT("+")))
                        ]

                        + SVerticalBox::Slot()
                        .AutoHeight()
                        .HAlign(HAlign_Center)
                        [
                            SNew(STextBlock)
                            .ColorAndOpacity(BlackText)
                            .Text(FText::FromString(TEXT("|")))
                        ]

                        + SVerticalBox::Slot()
                        .AutoHeight()
                        [
                            BuildNodeTree(ChildId)
                        ]
                    ];
                }

                // Permanent empty child socket.
                // Clicking it explicitly chooses this node as the parent.
                BranchRow->AddSlot()
                    .AutoWidth()
                    .VAlign(VAlign_Top)
                    .Padding(6.0f, 0.0f)
                [
                    SNew(SVerticalBox)

                    + SVerticalBox::Slot()
                    .AutoHeight()
                    .HAlign(HAlign_Center)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(BlackText)
                        .Text(FText::FromString(TEXT("+")))
                    ]

                    + SVerticalBox::Slot()
                    .AutoHeight()
                    .HAlign(HAlign_Center)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(BlackText)
                        .Text(FText::FromString(TEXT("|")))
                    ]

                    + SVerticalBox::Slot()
                    .AutoHeight()
                    .HAlign(HAlign_Center)
                    [
                        SNew(SButton)
                        .IsFocusable(false)
                        .ContentPadding(FMargin(8.0f, 5.0f))
                        .ToolTipText(FText::FromString(
                            TEXT("Empty attachment socket. Click, then choose a Codex Sign from the palette.")))
                        .OnClicked_Lambda([this, NodeId]()
                        {
                            SelectedCanvasNode = NodeId;
                            RebuildCanvasWidget();
                            return FReply::Handled();
                        })
                        [
                            SNew(STextBlock)
                            .ColorAndOpacity(BlackText)
                            .Text(FText::FromString(TEXT("o")))
                        ]
                    ]
                ];

                NodeColumn->AddSlot()
                    .AutoHeight()
                    .HAlign(HAlign_Center)
                    .Padding(0.0f, 0.0f, 0.0f, 4.0f)
                [
                    BranchRow
                ];

                return NodeColumn;
            };

            GraphTree = BuildNodeTree(RootNode->NodeId);
        }
    }
    else
    {
        GraphTree =
            SNew(SVerticalBox)

            + SVerticalBox::Slot()
            .AutoHeight()
            .HAlign(HAlign_Center)
            .Padding(0, 24, 0, 8)
            [
                SNew(STextBlock)
                .ColorAndOpacity(BlackText)
                .Text(FText::FromString(TEXT("o")))
            ]

            + SVerticalBox::Slot()
            .AutoHeight()
            .HAlign(HAlign_Center)
            [
                SNew(STextBlock)
                .ColorAndOpacity(BlackText)
                .AutoWrapText(true)
                .Text(FText::FromString(
                    TEXT("EMPTY ROOT SOCKET\nChoose the Tier I Earth Sign from the palette.")))
            ];
    }

    FString SelectedLabel = TEXT("ROOT / NONE");

    if (Graph && Codex && SelectedCanvasNode.IsValid())
    {
        if (const FSpellGraphNode* SelectedNode =
                Graph->FindNode(SelectedCanvasNode))
        {
            if (const FCodexEntry* SelectedEntry =
                    Codex->FindEntry(SelectedNode->ConceptId))
            {
                SelectedLabel = FString::Printf(
                    TEXT("[ %s ] %s"),
                    *SelectedEntry->Sign.Glyph,
                    *SelectedEntry->DisplayName.ToString());
            }
        }
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

                    + SVerticalBox::Slot()
                    .AutoHeight()
                    .HAlign(HAlign_Center)
                    .Padding(0, 0, 0, 4)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(BlackText)
                        .Text(FText::FromString(
                            TEXT("RUNE CANVAS / BRANCHING SPELL GRAPH")))
                    ]

                    + SVerticalBox::Slot()
                    .AutoHeight()
                    .Padding(0, 0, 0, 7)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(BlackText)
                        .AutoWrapText(true)
                        .Text(FText::FromString(
                            TEXT("Graph nodes show only their Sign. Click a Sign or its empty child socket, then choose a Sign from the Codex palette to attach it. Tier III values are terminal and have no outgoing socket.")))
                    ]

                    + SVerticalBox::Slot()
                    .AutoHeight()
                    .Padding(0, 0, 0, 7)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(BlackText)
                        .Text(FText::FromString(FString::Printf(
                            TEXT("ATTACH NEXT SIGN TO:  %s"),
                            *SelectedLabel)))
                    ]

                    + SVerticalBox::Slot()
                    .FillHeight(1.0f)
                    [
                        SNew(SHorizontalBox)

                        // --------------------------------------------------
                        // Palette
                        // --------------------------------------------------
                        + SHorizontalBox::Slot()
                        .FillWidth(0.38f)
                        .Padding(0, 0, 12, 0)
                        [
                            SNew(SBorder)
                            .Padding(FMargin(8.0f))
                            .BorderBackgroundColor(
                                FLinearColor(0.84f, 0.82f, 0.76f, 0.72f))
                            [
                                SNew(SVerticalBox)

                                + SVerticalBox::Slot()
                                .AutoHeight()
                                .Padding(0, 0, 0, 5)
                                [
                                    SNew(STextBlock)
                                    .ColorAndOpacity(BlackText)
                                    .Text(FText::FromString(
                                        TEXT("CODEX SIGNS")))
                                ]

                                + SVerticalBox::Slot()
                                .FillHeight(1.0f)
                                [
                                    SNew(SScrollBox)
                                    + SScrollBox::Slot()
                                    [
                                        PaletteList
                                    ]
                                ]
                            ]
                        ]

                        // --------------------------------------------------
                        // Real graph
                        // --------------------------------------------------
                        + SHorizontalBox::Slot()
                        .FillWidth(0.62f)
                        [
                            SNew(SBorder)
                            .Padding(FMargin(8.0f))
                            .BorderBackgroundColor(
                                FLinearColor(0.82f, 0.81f, 0.75f, 0.72f))
                            [
                                SNew(SVerticalBox)

                                + SVerticalBox::Slot()
                                .AutoHeight()
                                .Padding(0, 0, 0, 5)
                                [
                                    SNew(STextBlock)
                                    .ColorAndOpacity(BlackText)
                                    .Text(FText::FromString(
                                        TEXT("SPELL STRUCTURE")))
                                ]

                                + SVerticalBox::Slot()
                                .FillHeight(1.0f)
                                [
                                    SNew(SScrollBox)
                                    .Orientation(Orient_Horizontal)

                                    + SScrollBox::Slot()
                                    [
                                        SNew(SScrollBox)

                                        + SScrollBox::Slot()
                                        [
                                            SNew(SBox)
                                            .Padding(FMargin(18.0f))
                                            .HAlign(HAlign_Center)
                                            .VAlign(VAlign_Top)
                                            [
                                                GraphTree
                                            ]
                                        ]
                                    ]
                                ]

                                + SVerticalBox::Slot()
                                .AutoHeight()
                                .Padding(0, 7, 0, 4)
                                [
                                    SNew(STextBlock)
                                    .ColorAndOpacity(BlackText)
                                    .AutoWrapText(true)
                                    .Text(StatusText)
                                ]

                                + SVerticalBox::Slot()
                                .AutoHeight()
                                [
                                    SNew(SHorizontalBox)

                                    + SHorizontalBox::Slot()
                                    .AutoWidth()
                                    .Padding(0, 0, 6, 0)
                                    [
                                        SNew(SButton)
                                        .IsFocusable(false)
                                        .OnClicked_Lambda([this]()
                                        {
                                            if (USpellGraphSubsystem* CurrentGraph =
                                                    GetSpellGraph())
                                            {
                                                CurrentGraph->CompileAndApply();
                                            }

                                            RebuildCanvasWidget();
                                            return FReply::Handled();
                                        })
                                        [
                                            SNew(STextBlock)
                                            .ColorAndOpacity(BlackText)
                                            .Text(FText::FromString(
                                                TEXT("COMPILE / APPLY")))
                                        ]
                                    ]

                                    + SHorizontalBox::Slot()
                                    .AutoWidth()
                                    .Padding(0, 0, 6, 0)
                                    [
                                        SNew(SButton)
                                        .IsFocusable(false)
                                        .OnClicked_Lambda([this]()
                                        {
                                            if (USpellGraphSubsystem* CurrentGraph =
                                                    GetSpellGraph())
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
                                            .Text(FText::FromString(
                                                TEXT("REMOVE SELECTED")))
                                        ]
                                    ]

                                    + SHorizontalBox::Slot()
                                    .AutoWidth()
                                    [
                                        SNew(SButton)
                                        .IsFocusable(false)
                                        .OnClicked_Lambda([this]()
                                        {
                                            if (USpellGraphSubsystem* CurrentGraph =
                                                    GetSpellGraph())
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
                                            .Text(FText::FromString(
                                                TEXT("CLEAR")))
                                        ]
                                    ]
                                ]
                            ]
                        ]
                    ]

                    + SVerticalBox::Slot()
                    .AutoHeight()
                    .Padding(0, 8, 0, 0)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(BlackText)
                        .AutoWrapText(true)
                        .Text(FText::FromString(
                            TEXT("READY SPELL SLOTS remain above the 3D preview. The preview root now ignores hit testing itself while keeping its child controls interactive, so Canvas clicks and number-slot assignment can work at the same time.")))
                    ]
                ]
            ]
        ];

    GEngine->GameViewport->AddViewportWidgetContent(
        CanvasWidget.ToSharedRef(),
        4997);
}
'''

text = text[:start] + new_method + text[end:]

print("[3/3] Verifying redesign markers...")

required = [
    "SelfHitTestInvisible",
    "RUNE CANVAS / BRANCHING SPELL GRAPH",
    "EMPTY ROOT SOCKET",
    "ATTACH NEXT SIGN TO:",
    "Tier III values are terminal",
    "BuildNodeTree"
]

for token in required:
    if token not in text:
        raise RuntimeError(f"Verification failed: missing {token}")

CPP.write_text(text, encoding="utf-8", newline="\n")

print()
print("v0.14.1 Rune Graph Redesign applied successfully.")
print("Ready-slot buttons are interactive again.")
print("Graph nodes now show signs only and branch downward with permanent empty sockets.")
