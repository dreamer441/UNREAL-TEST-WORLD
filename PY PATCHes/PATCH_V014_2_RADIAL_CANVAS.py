from pathlib import Path

ROOT = Path(__file__).resolve().parent
H = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Public/InnerRealmSubsystem.h"
CPP = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Private/InnerRealmSubsystem.cpp"

for path in (H, CPP):
    if not path.exists():
        raise RuntimeError(f"Expected file missing: {path}")

def read(path):
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")

def write(path, text):
    path.write_text(text, encoding="utf-8", newline="\n")

print("[1/5] Fixing ready-slot input on the SPELL MODIFIER page...")

text = read(CPP)

old_editor_visibility = '''        .Visibility_Lambda([this]() { return ActivePage == EInnerRealmPage::Spell ? EVisibility::Visible : EVisibility::Collapsed; })
        .HAlign(HAlign_Left)'''
new_editor_visibility = '''        .Visibility_Lambda([this]()
        {
            return ActivePage == EInnerRealmPage::Spell
                ? EVisibility::SelfHitTestInvisible
                : EVisibility::Collapsed;
        })
        .HAlign(HAlign_Left)'''

if new_editor_visibility not in text:
    if old_editor_visibility not in text:
        raise RuntimeError(
            "Could not find the SPELL MODIFIER EditorWidget visibility block."
        )
    text = text.replace(old_editor_visibility, new_editor_visibility, 1)

print("[2/5] Adding radial-canvas state...")

htext = read(H)

if "TSet<FGuid> ExpandedCanvasNodes;" not in htext:
    marker = '''    FGuid SelectedCanvasNode;'''
    replacement = '''    FGuid SelectedCanvasNode;
    TSet<FGuid> ExpandedCanvasNodes;
    FName PendingCanvasElement = NAME_None;'''
    if marker not in htext:
        raise RuntimeError("Could not locate SelectedCanvasNode in InnerRealm header.")
    htext = htext.replace(marker, replacement, 1)

write(H, htext)

print("[3/5] Adding Slate constraint-canvas support...")

if '#include "Widgets/Layout/SConstraintCanvas.h"' not in text:
    marker = '#include "Widgets/Layout/SBox.h"'
    if marker not in text:
        raise RuntimeError("Could not locate SBox include.")
    text = text.replace(
        marker,
        marker + '\n#include "Widgets/Layout/SConstraintCanvas.h"',
        1)

print("[4/5] Replacing the old branching view with the large radial graph...")

start = text.find("void UInnerRealmSubsystem::RebuildCanvasWidget()")
end = text.find("\nvoid UInnerRealmSubsystem::RemoveEditorWidget()", start)

if start == -1 or end == -1:
    raise RuntimeError("Could not locate RebuildCanvasWidget().")

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

    // Semantic storage still keeps Earth -> Shape, but the Canvas presents
    // those two concepts as one visual construction node.
    const FSpellGraphNode* RootNode = nullptr;
    const FSpellGraphNode* ShapeNode = nullptr;

    if (Graph)
    {
        for (const FSpellGraphNode& Candidate : Graph->GetNodes())
        {
            if (!Candidate.ParentNodeId.IsValid())
            {
                RootNode = &Candidate;
                break;
            }
        }
    }

    if (Graph && Codex && RootNode)
    {
        for (const FSpellGraphNode& Candidate : Graph->GetNodes())
        {
            if (Candidate.ParentNodeId != RootNode->NodeId)
            {
                continue;
            }

            const FCodexEntry* CandidateEntry =
                Codex->FindEntry(Candidate.ConceptId);

            if (CandidateEntry &&
                CandidateEntry->Category == ECodexCategory::Shape)
            {
                ShapeNode = &Candidate;
                break;
            }
        }
    }

    // ------------------------------------------------------------------
    // CODEX PALETTE
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
                if (!Entry ||
                    !Graph->IsConceptSupported(Entry->ConceptId))
                {
                    continue;
                }

                if (!bAddedHeader)
                {
                    bAddedHeader = true;

                    PaletteList->AddSlot()
                        .AutoHeight()
                        .Padding(0, 9, 0, 3)
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

                PaletteList->AddSlot()
                    .AutoHeight()
                    .Padding(0, 1)
                [
                    SNew(SButton)
                    .IsFocusable(false)
                    .ContentPadding(FMargin(7.0f, 4.0f))
                    .ToolTipText(Entry->Description)
                    .OnClicked_Lambda([this, EntryId]()
                    {
                        USpellGraphSubsystem* CurrentGraph = GetSpellGraph();
                        UWorldCodexSubsystem* CurrentCodex = GetWorldCodex();

                        if (!CurrentGraph || !CurrentCodex)
                        {
                            return FReply::Handled();
                        }

                        const FCodexEntry* ChosenEntry =
                            CurrentCodex->FindEntry(EntryId);

                        if (!ChosenEntry)
                        {
                            return FReply::Handled();
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

                        // Step 1: choose the Tier-I Element. It stays pending
                        // until Shape is selected, because Element + Shape are
                        // one visual construction node in this design.
                        if (ChosenEntry->Category == ECodexCategory::Element)
                        {
                            if (CurrentGraph->GetNodes().Num() == 0)
                            {
                                PendingCanvasElement = EntryId;
                                SelectedCanvasNode.Invalidate();
                                ExpandedCanvasNodes.Reset();
                            }

                            RebuildCanvasWidget();
                            return FReply::Handled();
                        }

                        // Step 2: Element + Shape create one visual node.
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
                                        }
                                        else
                                        {
                                            CurrentGraph->ClearGraph();
                                        }
                                    }
                                }

                                RebuildCanvasWidget();
                                return FReply::Handled();
                            }

                            // Replacing the Shape updates the Shape part of
                            // the existing composite construction node.
                            if (CurrentRoot)
                            {
                                // Keep the stable GUID before mutating Nodes;
                                // removing the old Shape can invalidate pointers
                                // into the subsystem's TArray.
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
                                    CurrentGraph->RemoveSubtree(OldShapeId);
                                }

                                CurrentGraph->AddConcept(
                                    EntryId,
                                    CurrentRootId);

                                SelectedCanvasNode = CurrentRootId;
                            }

                            RebuildCanvasWidget();
                            return FReply::Handled();
                        }

                        if (!CurrentRoot)
                        {
                            RebuildCanvasWidget();
                            return FReply::Handled();
                        }

                        FGuid AttachParent = SelectedCanvasNode;

                        if (!AttachParent.IsValid())
                        {
                            AttachParent = CurrentRoot->NodeId;
                        }

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

                        // Shape parameters look like branches from the
                        // composite Earth+Shape node, while remaining
                        // semantically attached to the hidden Shape node.
                        if (ChosenEntry->Category ==
                                ECodexCategory::ShapeParameter &&
                            AttachParent == CurrentRoot->NodeId &&
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
                            // Keep the visual source selected so adding another
                            // branch does not require re-selecting it.
                            if (CurrentShapeId.IsValid() &&
                                AttachParent == CurrentShapeId)
                            {
                                SelectedCanvasNode = CurrentRoot->NodeId;
                            }
                            else
                            {
                                SelectedCanvasNode = AttachParent;
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
    // RADIAL LAYOUT
    // ------------------------------------------------------------------
    struct FVisualNodePlacement
    {
        FGuid NodeId;
        FVector2D Position = FVector2D::ZeroVector;
        FVector2D ParentPosition = FVector2D::ZeroVector;
        bool bHasParent = false;
    };

    struct FVisualSocketPlacement
    {
        FGuid ParentNodeId;
        FVector2D ParentPosition = FVector2D::ZeroVector;
        FVector2D Position = FVector2D::ZeroVector;
    };

    TArray<FVisualNodePlacement> VisualNodes;
    TArray<FVisualSocketPlacement> VisualSockets;
    TSet<FGuid> LayoutVisited;

    const float GraphWidth = 1280.0f;
    const float GraphHeight = 790.0f;
    const FVector2D GraphCenter(
        GraphWidth * 0.5f,
        GraphHeight * 0.5f);

    auto DirectionByIndex =
        [](const int32 Index) -> FVector2D
    {
        static const FVector2D Directions[] =
        {
            FVector2D( 0.0000f,  1.0000f), // down
            FVector2D( 0.0000f, -1.0000f), // up
            FVector2D(-1.0000f,  0.0000f), // left
            FVector2D( 1.0000f,  0.0000f), // right

            FVector2D(-0.7071f,  0.7071f),
            FVector2D( 0.7071f,  0.7071f),
            FVector2D(-0.7071f, -0.7071f),
            FVector2D( 0.7071f, -0.7071f),

            FVector2D( 0.3827f,  0.9239f),
            FVector2D(-0.3827f,  0.9239f),
            FVector2D( 0.3827f, -0.9239f),
            FVector2D(-0.3827f, -0.9239f),

            FVector2D(-0.9239f,  0.3827f),
            FVector2D( 0.9239f,  0.3827f),
            FVector2D(-0.9239f, -0.3827f),
            FVector2D( 0.9239f, -0.3827f)
        };

        return Directions[Index % UE_ARRAY_COUNT(Directions)];
    };

    auto IsPositionFree =
        [&VisualNodes, &VisualSockets](
            const FVector2D& Candidate) -> bool
    {
        constexpr float MinNodeDistance = 92.0f;

        for (const FVisualNodePlacement& Existing : VisualNodes)
        {
            if (FVector2D::Distance(
                    Existing.Position,
                    Candidate) < MinNodeDistance)
            {
                return false;
            }
        }

        for (const FVisualSocketPlacement& Existing : VisualSockets)
        {
            if (FVector2D::Distance(
                    Existing.Position,
                    Candidate) < 70.0f)
            {
                return false;
            }
        }

        return true;
    };

    auto FindOpenRadialPosition =
        [&DirectionByIndex,
         &IsPositionFree,
         GraphWidth,
         GraphHeight](
            const FVector2D& Origin,
            const FVector2D& BackToParent,
            int32& InOutDirectionCursor,
            const int32 Depth) -> FVector2D
    {
        const FVector2D BackNormal =
            BackToParent.IsNearlyZero()
                ? FVector2D::ZeroVector
                : BackToParent.GetSafeNormal();

        for (int32 Attempt = 0; Attempt < 64; ++Attempt)
        {
            const int32 DirectionIndex =
                InOutDirectionCursor++;

            const FVector2D Direction =
                DirectionByIndex(DirectionIndex);

            // The incoming parent line already occupies one side of a
            // Tier-II node. Do not send a new branch directly back through it.
            if (!BackNormal.IsNearlyZero() &&
                FVector2D::DotProduct(
                    Direction,
                    BackNormal) > 0.78f)
            {
                continue;
            }

            const int32 Ring = DirectionIndex / 16;

            const float Radius =
                150.0f +
                static_cast<float>(Depth) * 12.0f +
                static_cast<float>(Ring) * 82.0f;

            const FVector2D Candidate =
                Origin + Direction * Radius;

            if (Candidate.X < 55.0f ||
                Candidate.X > GraphWidth - 55.0f ||
                Candidate.Y < 55.0f ||
                Candidate.Y > GraphHeight - 55.0f)
            {
                continue;
            }

            if (IsPositionFree(Candidate))
            {
                return Candidate;
            }
        }

        return Origin + FVector2D(
            0.0f,
            155.0f + static_cast<float>(Depth) * 18.0f);
    };

    TFunction<void(
        const FGuid&,
        const FVector2D&,
        const FVector2D&,
        bool,
        int32)> LayoutNode;

    LayoutNode =
        [this,
         Graph,
         Codex,
         RootNode,
         ShapeNode,
         &VisualNodes,
         &VisualSockets,
         &LayoutVisited,
         &FindOpenRadialPosition,
         &LayoutNode](
            const FGuid& NodeId,
            const FVector2D& Position,
            const FVector2D& ParentPosition,
            const bool bHasParent,
            const int32 Depth)
    {
        if (!Graph ||
            !Codex ||
            LayoutVisited.Contains(NodeId))
        {
            return;
        }

        const FSpellGraphNode* Node =
            Graph->FindNode(NodeId);

        if (!Node)
        {
            return;
        }

        LayoutVisited.Add(NodeId);

        FVisualNodePlacement Placement;
        Placement.NodeId = NodeId;
        Placement.Position = Position;
        Placement.ParentPosition = ParentPosition;
        Placement.bHasParent = bHasParent;
        VisualNodes.Add(Placement);

        TArray<const FSpellGraphNode*> Children;

        if (RootNode &&
            NodeId == RootNode->NodeId)
        {
            // Earth children other than the hidden Shape.
            for (const FSpellGraphNode& Candidate :
                 Graph->GetNodes())
            {
                if (Candidate.ParentNodeId ==
                    RootNode->NodeId)
                {
                    if (ShapeNode &&
                        Candidate.NodeId ==
                            ShapeNode->NodeId)
                    {
                        continue;
                    }

                    Children.Add(&Candidate);
                }
            }

            // Shape parameters visually branch from the composite root.
            if (ShapeNode)
            {
                for (const FSpellGraphNode& Candidate :
                     Graph->GetNodes())
                {
                    if (Candidate.ParentNodeId ==
                        ShapeNode->NodeId)
                    {
                        Children.Add(&Candidate);
                    }
                }
            }
        }
        else
        {
            for (const FSpellGraphNode& Candidate :
                 Graph->GetNodes())
            {
                if (Candidate.ParentNodeId == NodeId)
                {
                    Children.Add(&Candidate);
                }
            }
        }

        Children.Sort([](
            const FSpellGraphNode& A,
            const FSpellGraphNode& B)
        {
            return A.Order < B.Order;
        });

        FVector2D BackToParent = FVector2D::ZeroVector;

        if (bHasParent)
        {
            BackToParent = ParentPosition - Position;
        }

        int32 DirectionCursor = 0;

        for (const FSpellGraphNode* Child : Children)
        {
            if (!Child)
            {
                continue;
            }

            const FVector2D ChildPosition =
                FindOpenRadialPosition(
                    Position,
                    BackToParent,
                    DirectionCursor,
                    Depth);

            LayoutNode(
                Child->NodeId,
                ChildPosition,
                Position,
                true,
                Depth + 1);
        }

        const FCodexEntry* Entry =
            Codex->FindEntry(Node->ConceptId);

        const bool bVisualRoot =
            RootNode &&
            NodeId == RootNode->NodeId;

        const bool bTerminal =
            !bVisualRoot &&
            Entry &&
            Entry->Tier == ECodexTier::TierIII;

        // Double-clicking opens exactly one empty branch. Once filled,
        // another empty branch remains available around the same node.
        if (!bTerminal &&
            ExpandedCanvasNodes.Contains(NodeId))
        {
            FVisualSocketPlacement Socket;
            Socket.ParentNodeId = NodeId;
            Socket.ParentPosition = Position;
            Socket.Position =
                FindOpenRadialPosition(
                    Position,
                    BackToParent,
                    DirectionCursor,
                    Depth);

            VisualSockets.Add(Socket);
        }
    };

    if (RootNode)
    {
        LayoutNode(
            RootNode->NodeId,
            GraphCenter,
            FVector2D::ZeroVector,
            false,
            0);
    }

    TSharedRef<SConstraintCanvas> RadialGraph =
        SNew(SConstraintCanvas);

    auto AddConnector =
        [BlackText, &RadialGraph](
            const FVector2D& A,
            const FVector2D& B)
    {
        const FVector2D Delta = B - A;
        const FVector2D Mid = (A + B) * 0.5f;

        FString Glyph;

        if (FMath::Abs(Delta.X) <
            FMath::Abs(Delta.Y) * 0.45f)
        {
            Glyph = TEXT("│\n│\n│");
        }
        else if (FMath::Abs(Delta.Y) <
                 FMath::Abs(Delta.X) * 0.45f)
        {
            Glyph = TEXT("────────");
        }
        else if ((Delta.X > 0.0f &&
                  Delta.Y > 0.0f) ||
                 (Delta.X < 0.0f &&
                  Delta.Y < 0.0f))
        {
            Glyph = TEXT("╲\n ╲\n  ╲");
        }
        else
        {
            Glyph = TEXT("  ╱\n ╱\n╱");
        }

        RadialGraph->AddSlot()
            .Anchors(FAnchors(0.0f, 0.0f))
            .Alignment(FVector2D(0.5f, 0.5f))
            .AutoSize(true)
            .Offset(FMargin(
                Mid.X,
                Mid.Y,
                0.0f,
                0.0f))
            .ZOrder(0.0f)
        [
            SNew(STextBlock)
            .Visibility(EVisibility::HitTestInvisible)
            .ColorAndOpacity(BlackText)
            .Justification(ETextJustify::Center)
            .Text(FText::FromString(Glyph))
        ];
    };

    for (const FVisualNodePlacement& Placement : VisualNodes)
    {
        if (Placement.bHasParent)
        {
            AddConnector(
                Placement.ParentPosition,
                Placement.Position);
        }
    }

    for (const FVisualSocketPlacement& Socket : VisualSockets)
    {
        AddConnector(
            Socket.ParentPosition,
            Socket.Position);
    }

    for (const FVisualSocketPlacement& Socket : VisualSockets)
    {
        const FGuid ParentId = Socket.ParentNodeId;

        RadialGraph->AddSlot()
            .Anchors(FAnchors(0.0f, 0.0f))
            .Alignment(FVector2D(0.5f, 0.5f))
            .AutoSize(true)
            .Offset(FMargin(
                Socket.Position.X,
                Socket.Position.Y,
                0.0f,
                0.0f))
            .ZOrder(1.0f)
        [
            SNew(SButton)
            .IsFocusable(false)
            .ContentPadding(FMargin(8.0f))
            .ToolTipText(FText::FromString(
                TEXT("Empty branch. Click it, then choose a Sign from the Codex palette.")))
            .OnClicked_Lambda([this, ParentId]()
            {
                SelectedCanvasNode = ParentId;
                return FReply::Handled();
            })
            [
                SNew(STextBlock)
                .ColorAndOpacity(BlackText)
                .Text(FText::FromString(TEXT("○")))
            ]
        ];
    }

    for (const FVisualNodePlacement& Placement : VisualNodes)
    {
        const FGuid VisualNodeId = Placement.NodeId;

        const FSpellGraphNode* Node =
            Graph
                ? Graph->FindNode(VisualNodeId)
                : nullptr;

        if (!Node || !Codex)
        {
            continue;
        }

        const bool bVisualRoot =
            RootNode &&
            VisualNodeId == RootNode->NodeId;

        const FCodexEntry* Entry =
            Codex->FindEntry(Node->ConceptId);

        if (!Entry)
        {
            continue;
        }

        FString DisplayGlyph = Entry->Sign.Glyph;
        FString TooltipTitle = Entry->DisplayName.ToString();
        ECodexTier VisualTier = Entry->Tier;

        if (bVisualRoot)
        {
            const FCodexEntry* ShapeEntry =
                ShapeNode
                    ? Codex->FindEntry(ShapeNode->ConceptId)
                    : nullptr;

            if (ShapeEntry)
            {
                DisplayGlyph = FString::Printf(
                    TEXT("%s   %s"),
                    *Entry->Sign.Glyph,
                    *ShapeEntry->Sign.Glyph);

                TooltipTitle = FString::Printf(
                    TEXT("%s %s"),
                    *Entry->DisplayName.ToString(),
                    *ShapeEntry->DisplayName.ToString());
            }
            else
            {
                DisplayGlyph = FString::Printf(
                    TEXT("%s   ?"),
                    *Entry->Sign.Glyph);
            }

            VisualTier = ECodexTier::TierI;
        }

        const bool bSelected =
            SelectedCanvasNode.IsValid() &&
            SelectedCanvasNode == VisualNodeId;

        const FLinearColor NodeColor =
            bSelected
                ? FLinearColor(0.62f, 0.82f, 0.64f, 0.99f)
                : FLinearColor(0.84f, 0.82f, 0.76f, 0.98f);

        FString TierLabel = TEXT("II");
        if (VisualTier == ECodexTier::TierI)
        {
            TierLabel = TEXT("I");
        }
        else if (VisualTier == ECodexTier::TierIII)
        {
            TierLabel = TEXT("III");
        }

        const FText Tooltip =
            FText::FromString(FString::Printf(
                TEXT("%s\nTier %s\n\nDOUBLE CLICK: open the next radial attachment line."),
                *TooltipTitle,
                *TierLabel));

        RadialGraph->AddSlot()
            .Anchors(FAnchors(0.0f, 0.0f))
            .Alignment(FVector2D(0.5f, 0.5f))
            .AutoSize(true)
            .Offset(FMargin(
                Placement.Position.X,
                Placement.Position.Y,
                0.0f,
                0.0f))
            .ZOrder(2.0f)
        [
            SNew(SBorder)
            .Padding(FMargin(
                bVisualRoot ? 16.0f : 12.0f,
                10.0f))
            .BorderBackgroundColor(NodeColor)
            .ToolTipText(Tooltip)
            .OnMouseDoubleClick_Lambda(
                [this,
                 VisualNodeId,
                 VisualTier](
                    const FGeometry&,
                    const FPointerEvent& Event)
                {
                    if (Event.GetEffectingButton() !=
                        EKeys::LeftMouseButton)
                    {
                        return FReply::Unhandled();
                    }

                    SelectedCanvasNode = VisualNodeId;

                    if (VisualTier != ECodexTier::TierIII)
                    {
                        ExpandedCanvasNodes.Add(VisualNodeId);
                    }

                    RebuildCanvasWidget();
                    return FReply::Handled();
                })
            [
                SNew(STextBlock)
                .ColorAndOpacity(BlackText)
                .Justification(ETextJustify::Center)
                .Text(FText::FromString(DisplayGlyph))
            ]
        ];
    }

    FString SelectedLabel = TEXT("NONE");

    if (Graph &&
        Codex &&
        RootNode &&
        SelectedCanvasNode.IsValid())
    {
        if (SelectedCanvasNode == RootNode->NodeId)
        {
            const FCodexEntry* RootEntry =
                Codex->FindEntry(RootNode->ConceptId);

            const FCodexEntry* ShapeEntry =
                ShapeNode
                    ? Codex->FindEntry(ShapeNode->ConceptId)
                    : nullptr;

            if (RootEntry && ShapeEntry)
            {
                SelectedLabel =
                    FString::Printf(
                        TEXT("%s %s"),
                        *RootEntry->DisplayName.ToString(),
                        *ShapeEntry->DisplayName.ToString());
            }
        }
        else if (const FSpellGraphNode* Selected =
                     Graph->FindNode(SelectedCanvasNode))
        {
            if (const FCodexEntry* SelectedEntry =
                    Codex->FindEntry(Selected->ConceptId))
            {
                SelectedLabel =
                    SelectedEntry->DisplayName.ToString();
            }
        }
    }

    FString FoundationStatus;

    if (!RootNode)
    {
        if (PendingCanvasElement ==
            FName(TEXT("element.earth")))
        {
            FoundationStatus =
                TEXT("EARTH SELECTED — now choose Sphere, Cube, or Cone. Element + Shape will become one construction node.");
        }
        else
        {
            FoundationStatus =
                TEXT("START: choose an Element, then a Shape. They will appear as one central construction node.");
        }
    }
    else
    {
        FoundationStatus =
            FString::Printf(
                TEXT("SELECTED ATTACHMENT SOURCE: %s"),
                *SelectedLabel);
    }

    const FText CompileStatus =
        Graph
            ? Graph->GetLastCompileResult().Message
            : FText::FromString(
                TEXT("SpellGraph subsystem unavailable."));

    TSharedRef<SWidget> GraphContent =
        SNew(SVerticalBox);

    if (RootNode)
    {
        GraphContent = RadialGraph;
    }
    else
    {
        GraphContent =
            SNew(SVerticalBox)

            + SVerticalBox::Slot()
            .AutoHeight()
            .HAlign(HAlign_Center)
            .Padding(0, 250, 0, 12)
            [
                SNew(STextBlock)
                .ColorAndOpacity(BlackText)
                .Text(FText::FromString(
                    PendingCanvasElement.IsNone()
                        ? TEXT("○")
                        : TEXT("[ E ]   +   [ ? ]")))
            ]

            + SVerticalBox::Slot()
            .AutoHeight()
            .HAlign(HAlign_Center)
            [
                SNew(STextBlock)
                .ColorAndOpacity(BlackText)
                .Text(FText::FromString(
                    PendingCanvasElement.IsNone()
                        ? TEXT("EMPTY CONSTRUCTION")
                        : TEXT("CHOOSE A SHAPE")))
            ];
    }

    CanvasWidget = SNew(SBox)
        .Visibility_Lambda([this]()
        {
            return ActivePage == EInnerRealmPage::Canvas
                ? EVisibility::Visible
                : EVisibility::Collapsed;
        })
        .HAlign(HAlign_Center)
        .VAlign(VAlign_Center)
        [
            SNew(SBox)
            .WidthOverride(1700.0f)
            .HeightOverride(920.0f)
            [
                SNew(SBorder)
                .Padding(FMargin(16.0f))
                .BorderBackgroundColor(
                    FLinearColor(0.92f, 0.90f, 0.84f, 0.995f))
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
                            TEXT("RUNE CANVAS / RADIAL SPELL STRUCTURE")))
                    ]

                    + SVerticalBox::Slot()
                    .AutoHeight()
                    .Padding(0, 0, 0, 6)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(BlackText)
                        .AutoWrapText(true)
                        .Text(FText::FromString(FoundationStatus))
                    ]

                    + SVerticalBox::Slot()
                    .FillHeight(1.0f)
                    [
                        SNew(SHorizontalBox)

                        + SHorizontalBox::Slot()
                        .FillWidth(0.22f)
                        .Padding(0, 0, 10, 0)
                        [
                            SNew(SBorder)
                            .Padding(FMargin(8.0f))
                            .BorderBackgroundColor(
                                FLinearColor(0.84f, 0.82f, 0.76f, 0.78f))
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

                        + SHorizontalBox::Slot()
                        .FillWidth(0.78f)
                        [
                            SNew(SBorder)
                            .Padding(FMargin(8.0f))
                            .BorderBackgroundColor(
                                FLinearColor(0.80f, 0.80f, 0.74f, 0.72f))
                            [
                                SNew(SVerticalBox)

                                + SVerticalBox::Slot()
                                .AutoHeight()
                                .Padding(0, 0, 0, 5)
                                [
                                    SNew(STextBlock)
                                    .ColorAndOpacity(BlackText)
                                    .Text(FText::FromString(
                                        TEXT("SPELL GRAPH — DOUBLE CLICK A NON-TERMINAL SIGN TO OPEN ITS NEXT RADIAL BRANCH")))
                                ]

                                + SVerticalBox::Slot()
                                .FillHeight(1.0f)
                                [
                                    SNew(SBox)
                                    .WidthOverride(GraphWidth)
                                    .HeightOverride(GraphHeight)
                                    [
                                        GraphContent
                                    ]
                                ]

                                + SVerticalBox::Slot()
                                .AutoHeight()
                                .Padding(0, 6, 0, 4)
                                [
                                    SNew(STextBlock)
                                    .ColorAndOpacity(BlackText)
                                    .AutoWrapText(true)
                                    .Text(CompileStatus)
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
                                                    ExpandedCanvasNodes.Remove(
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

                                            PendingCanvasElement = NAME_None;
                                            SelectedCanvasNode.Invalidate();
                                            ExpandedCanvasNodes.Reset();

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
                ]
            ]
        ];

    // Canvas sits above the preview/reference model and below the top
    // navigation (which remains at Z=5002).
    GEngine->GameViewport->AddViewportWidgetContent(
        CanvasWidget.ToSharedRef(),
        5001);
}
'''

text = text[:start] + new_method + text[end:]

print("[5/5] Verifying patch markers...")

required_tokens = [
    "EVisibility::SelfHitTestInvisible",
    "TSet<FGuid> ExpandedCanvasNodes",
    "SConstraintCanvas",
    "RUNE CANVAS / RADIAL SPELL STRUCTURE",
    "DOUBLE CLICK",
    "PendingCanvasElement",
    "5001"
]

combined = htext + "\n" + text

for token in required_tokens:
    if token not in combined:
        raise RuntimeError(f"Verification failed: missing {token}")

write(CPP, text)

print()
print("v0.14.2 radial-canvas patch applied.")
print("SPELL MODIFIER ready-slot overlay input fixed.")
print("Earth + Shape are one visual construction node.")
print("Non-terminal nodes reveal radial branch sockets on double-click.")
