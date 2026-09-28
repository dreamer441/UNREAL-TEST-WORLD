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
preview_cpp = ROOT / "Plugins/SpellPreview/Source/SpellPreview/Private/SpellPreviewSubsystem.cpp"

for required in [inner_h, inner_cpp, inner_build, inner_plugin, preview_cpp]:
    if not required.exists():
        raise RuntimeError(f"Expected v0.13.3 file missing: {required}")

pattern_types = ROOT / "Plugins/SpellCreation/Source/SpellCreation/Public/SpellPatternTypes.h"
if not pattern_types.exists() or "ESpellPatternOrientation" not in read(pattern_types):
    raise RuntimeError("v0.13.4 requires the working v0.13.3 Pattern Orientation patch first.")

print("[1/6] Wiring WorldCodex into InnerRealm...")
add_build_dependency(inner_build, "WorldCodex")
add_plugin_dependency(inner_plugin, "WorldCodex")

print("[2/6] Extending InnerRealm state for Spell / Codex / Canvas pages...")
text = read(inner_h)
if "class UWorldCodexSubsystem;" not in text:
    text = text.replace("class USpellCastingBindingSubsystem;\n", "class USpellCastingBindingSubsystem;\nclass UWorldCodexSubsystem;\n", 1)

if "enum class EInnerRealmPage" not in text:
    marker = "enum class ESpellLiveAction : uint8;\n"
    addition = '''enum class ESpellLiveAction : uint8;\n\nenum class EInnerRealmPage : uint8\n{\n    Spell,\n    Codex,\n    Canvas\n};\n'''
    text = replace_once(text, marker, addition, "InnerRealm page enum")

if "IsSpellWorkbenchVisible" not in text:
    marker = '''    UFUNCTION(BlueprintPure, Category="Inner Realm")\n    bool IsActive() const { return bActive; }'''
    replacement = '''    UFUNCTION(BlueprintPure, Category="Inner Realm")\n    bool IsActive() const { return bActive; }\n\n    bool IsSpellWorkbenchVisible() const\n    {\n        return bActive && ActivePage == EInnerRealmPage::Spell;\n    }'''
    text = replace_once(text, marker, replacement, "Spell page visibility accessor")

if "NavigationWidget" not in text:
    marker = '''    bool bActive = false;\n    TSharedPtr<SWidget> EditorWidget;\n    TSharedPtr<SWidget> PreviewFrameWidget;'''
    replacement = '''    bool bActive = false;\n    EInnerRealmPage ActivePage = EInnerRealmPage::Spell;\n    FName SelectedCodexConcept = FName(TEXT("element.earth"));\n\n    TSharedPtr<SWidget> NavigationWidget;\n    TSharedPtr<SWidget> EditorWidget;\n    TSharedPtr<SWidget> PreviewFrameWidget;\n    TSharedPtr<SWidget> CodexWidget;\n    TSharedPtr<SWidget> CanvasWidget;'''
    text = replace_once(text, marker, replacement, "InnerRealm page/widget state")

if "GetWorldCodex() const" not in text:
    marker = '''    USpellCreationSubsystem* GetSpellCreation() const;\n    USpellCastingBindingSubsystem* GetSpellBindings() const;'''
    replacement = '''    USpellCreationSubsystem* GetSpellCreation() const;\n    USpellCastingBindingSubsystem* GetSpellBindings() const;\n    UWorldCodexSubsystem* GetWorldCodex() const;\n\n    FText GetSelectedCodexTitle() const;\n    FText GetSelectedCodexSign() const;\n    FText GetSelectedCodexDetails() const;'''
    text = replace_once(text, marker, replacement, "Codex helper declarations")

write(inner_h, text)

print("[3/6] Adding Codex access/detail presentation helpers...")
text = read(inner_cpp)
text = add_include(text, '#include "SpellCastingBindingSubsystem.h"', '#include "WorldCodexSubsystem.h"', "WorldCodex subsystem")

if "UWorldCodexSubsystem* UInnerRealmSubsystem::GetWorldCodex() const" not in text:
    marker = '''USpellCastingBindingSubsystem* UInnerRealmSubsystem::GetSpellBindings() const\n{\n    UWorld* World = GetWorld();\n    return World ? World->GetSubsystem<USpellCastingBindingSubsystem>() : nullptr;\n}\n'''
    addition = marker + r'''
UWorldCodexSubsystem* UInnerRealmSubsystem::GetWorldCodex() const
{
    UWorld* World = GetWorld();
    return World ? World->GetSubsystem<UWorldCodexSubsystem>() : nullptr;
}

FText UInnerRealmSubsystem::GetSelectedCodexTitle() const
{
    const UWorldCodexSubsystem* Codex = GetWorldCodex();
    const FCodexEntry* Entry = Codex ? Codex->FindEntry(SelectedCodexConcept) : nullptr;
    return Entry ? Entry->DisplayName : FText::FromString(TEXT("CODEX"));
}

FText UInnerRealmSubsystem::GetSelectedCodexSign() const
{
    const UWorldCodexSubsystem* Codex = GetWorldCodex();
    const FCodexEntry* Entry = Codex ? Codex->FindEntry(SelectedCodexConcept) : nullptr;
    return Entry
        ? FText::FromString(FString::Printf(TEXT("SIGN  [ %s ]"), *Entry->Sign.Glyph))
        : FText::GetEmpty();
}

FText UInnerRealmSubsystem::GetSelectedCodexDetails() const
{
    const UWorldCodexSubsystem* Codex = GetWorldCodex();
    const FCodexEntry* Entry = Codex ? Codex->FindEntry(SelectedCodexConcept) : nullptr;
    if (!Entry)
    {
        return FText::FromString(TEXT("Select a Codex entry."));
    }

    auto JoinNames = [](const TArray<FName>& Names) -> FString
    {
        if (Names.Num() == 0) return TEXT("-");
        TArray<FString> Parts;
        Parts.Reserve(Names.Num());
        for (const FName Name : Names) Parts.Add(Name.ToString());
        return FString::Join(Parts, TEXT(", "));
    };

    TArray<FString> RelationLines;
    for (const FCodexRelation& Relation : Entry->Relationships)
    {
        RelationLines.Add(FString::Printf(
            TEXT("%s -> %s"),
            *Relation.Relation.ToString(),
            *Relation.TargetConceptId.ToString()));
    }

    const FString Relations = RelationLines.Num() > 0
        ? FString::Join(RelationLines, TEXT("\n"))
        : TEXT("-");

    FString Details = FString::Printf(
        TEXT("CONCEPT ID\n%s\n\nCATEGORY\n%s\n\nSTATUS\n%s\n\nOWNING SYSTEM\n%s\n\nDESCRIPTION\n%s\n\nPROVIDES CAPABILITIES\n%s\n\nREQUIRES CAPABILITIES\n%s\n\nRELATIONSHIPS\n%s"),
        *Entry->ConceptId.ToString(),
        *CodexCategoryToText(Entry->Category).ToString(),
        *CodexImplementationStateToText(Entry->ImplementationState).ToString(),
        *Entry->OwningSystem.ToString(),
        *Entry->Description.ToString(),
        *JoinNames(Entry->ProvidesCapabilities),
        *JoinNames(Entry->RequiresCapabilities),
        *Relations);

    if (!Entry->DeveloperNotes.IsEmpty())
    {
        Details += FString::Printf(TEXT("\n\nDEVELOPER NOTE\n%s"), *Entry->DeveloperNotes.ToString());
    }

    return FText::FromString(Details);
}
'''
    text = replace_once(text, marker, addition, "Codex helper implementations")

print("[4/6] Adding top navigation and Codex/Canvas templates...")
if ".Visibility_Lambda([this]() { return ActivePage == EInnerRealmPage::Spell" not in text:
    text = replace_once(
        text,
        '''    EditorWidget = SNew(SBox)\n        .HAlign(HAlign_Left)\n        .VAlign(VAlign_Center)''',
        '''    EditorWidget = SNew(SBox)\n        .Visibility_Lambda([this]() { return ActivePage == EInnerRealmPage::Spell ? EVisibility::Visible : EVisibility::Collapsed; })\n        .HAlign(HAlign_Left)\n        .VAlign(VAlign_Center)''',
        "Spell editor page visibility")

if "PreviewFrameWidget = SNew(SBox)\n        .Visibility_Lambda" not in text:
    text = replace_once(
        text,
        '''    PreviewFrameWidget = SNew(SBox)\n        .HAlign(HAlign_Right)\n        .VAlign(VAlign_Center)''',
        '''    PreviewFrameWidget = SNew(SBox)\n        .Visibility_Lambda([this]() { return ActivePage == EInnerRealmPage::Spell ? EVisibility::Visible : EVisibility::Collapsed; })\n        .HAlign(HAlign_Right)\n        .VAlign(VAlign_Center)''',
        "Spell preview page visibility")

if "NavigationWidget = SNew(SBox)" not in text:
    marker = '''    GEngine->GameViewport->AddViewportWidgetContent(PreviewFrameWidget.ToSharedRef(), 4999);\n}'''
    ui = r'''    GEngine->GameViewport->AddViewportWidgetContent(PreviewFrameWidget.ToSharedRef(), 4999);

    auto MakePageButton = [this, BlackText](
        const EInnerRealmPage Page,
        const TCHAR* Label) -> TSharedRef<SWidget>
    {
        return SNew(SBox)
            .WidthOverride(190.0f)
            [
                SNew(SButton)
                .IsFocusable(false)
                .ContentPadding(FMargin(14.0f, 7.0f))
                .OnClicked_Lambda([this, Page]()
                {
                    ActivePage = Page;
                    return FReply::Handled();
                })
                [
                    SNew(STextBlock)
                    .Justification(ETextJustify::Center)
                    .ColorAndOpacity(BlackText)
                    .Text_Lambda([this, Page, Label]()
                    {
                        return FText::FromString(
                            ActivePage == Page
                                ? FString::Printf(TEXT("[ %s ]"), Label)
                                : FString(Label));
                    })
                ]
            ];
    };

    TSharedRef<SVerticalBox> CodexList = SNew(SVerticalBox);
    if (UWorldCodexSubsystem* Codex = GetWorldCodex())
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
            ECodexCategory::Action,
            ECodexCategory::WorldObject,
            ECodexCategory::WorldState,
            ECodexCategory::Event,
            ECodexCategory::Logic,
            ECodexCategory::PhysicsConcept
        };

        for (const ECodexCategory Category : CategoryOrder)
        {
            const TArray<const FCodexEntry*> Entries = Codex->GetEntriesByCategory(Category);
            if (Entries.Num() == 0) continue;

            CodexList->AddSlot().AutoHeight().Padding(0, 9, 0, 4)
            [
                SNew(SBorder)
                .Padding(FMargin(7.0f, 5.0f))
                .BorderBackgroundColor(FLinearColor(0.78f, 0.76f, 0.70f, 0.96f))
                [
                    SNew(STextBlock)
                    .ColorAndOpacity(BlackText)
                    .Text(CodexCategoryToText(Category))
                ]
            ];

            for (const FCodexEntry* Entry : Entries)
            {
                if (!Entry) continue;
                const FName EntryId = Entry->ConceptId;

                CodexList->AddSlot().AutoHeight().Padding(0, 1)
                [
                    SNew(SButton)
                    .IsFocusable(false)
                    .ContentPadding(FMargin(8.0f, 5.0f))
                    .OnClicked_Lambda([this, EntryId]()
                    {
                        SelectedCodexConcept = EntryId;
                        return FReply::Handled();
                    })
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(BlackText)
                        .Text_Lambda([this, EntryId]()
                        {
                            const UWorldCodexSubsystem* CurrentCodex = GetWorldCodex();
                            const FCodexEntry* CurrentEntry = CurrentCodex
                                ? CurrentCodex->FindEntry(EntryId)
                                : nullptr;
                            if (!CurrentEntry) return FText::FromString(EntryId.ToString());

                            return FText::FromString(FString::Printf(
                                SelectedCodexConcept == EntryId
                                    ? TEXT("[ %s ]  %s")
                                    : TEXT("  %s    %s"),
                                *CurrentEntry->Sign.Glyph,
                                *CurrentEntry->DisplayName.ToString()));
                        })
                    ]
                ];
            }
        }
    }

    CodexWidget = SNew(SBox)
        .Visibility_Lambda([this]() { return ActivePage == EInnerRealmPage::Codex ? EVisibility::Visible : EVisibility::Collapsed; })
        .HAlign(HAlign_Center)
        .VAlign(VAlign_Center)
        [
            SNew(SBox)
            .WidthOverride(1340.0f)
            .HeightOverride(760.0f)
            [
                SNew(SBorder)
                .Padding(FMargin(20.0f))
                .BorderBackgroundColor(FLinearColor(0.92f, 0.90f, 0.84f, 0.98f))
                [
                    SNew(SHorizontalBox)
                    + SHorizontalBox::Slot().FillWidth(0.34f).Padding(0, 0, 18, 0)
                    [
                        SNew(SVerticalBox)
                        + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 8)
                        [
                            SNew(STextBlock)
                            .ColorAndOpacity(BlackText)
                            .Text(FText::FromString(TEXT("WORLD CODEX / CANONICAL VOCABULARY")))
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 8)
                        [
                            SNew(STextBlock)
                            .ColorAndOpacity(BlackText)
                            .AutoWrapText(true)
                            .Text(FText::FromString(TEXT("Everything meaningful in the world can receive a stable Concept ID and Sign. Implemented and future concepts live in the same dictionary.")))
                        ]
                        + SVerticalBox::Slot().FillHeight(1.0f)
                        [
                            SNew(SScrollBox)
                            + SScrollBox::Slot()
                            [
                                CodexList
                            ]
                        ]
                    ]
                    + SHorizontalBox::Slot().FillWidth(0.66f)
                    [
                        SNew(SBorder)
                        .Padding(FMargin(22.0f))
                        .BorderBackgroundColor(FLinearColor(0.82f, 0.81f, 0.75f, 0.70f))
                        [
                            SNew(SScrollBox)
                            + SScrollBox::Slot()
                            [
                                SNew(SVerticalBox)
                                + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 8)
                                [
                                    SNew(STextBlock)
                                    .ColorAndOpacity(BlackText)
                                    .Text_Lambda([this]() { return GetSelectedCodexTitle(); })
                                ]
                                + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 18)
                                [
                                    SNew(STextBlock)
                                    .ColorAndOpacity(BlackText)
                                    .Text_Lambda([this]() { return GetSelectedCodexSign(); })
                                ]
                                + SVerticalBox::Slot().AutoHeight()
                                [
                                    SNew(STextBlock)
                                    .ColorAndOpacity(BlackText)
                                    .AutoWrapText(true)
                                    .Text_Lambda([this]() { return GetSelectedCodexDetails(); })
                                ]
                            ]
                        ]
                    ]
                ]
            ]
        ];

    GEngine->GameViewport->AddViewportWidgetContent(CodexWidget.ToSharedRef(), 4998);

    CanvasWidget = SNew(SBox)
        .Visibility_Lambda([this]() { return ActivePage == EInnerRealmPage::Canvas ? EVisibility::Visible : EVisibility::Collapsed; })
        .HAlign(HAlign_Center)
        .VAlign(VAlign_Center)
        [
            SNew(SBox)
            .WidthOverride(1340.0f)
            .HeightOverride(760.0f)
            [
                SNew(SBorder)
                .Padding(FMargin(28.0f))
                .BorderBackgroundColor(FLinearColor(0.92f, 0.90f, 0.84f, 0.98f))
                [
                    SNew(SVerticalBox)
                    + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0, 170, 0, 18)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(BlackText)
                        .Text(FText::FromString(TEXT("RUNE CANVAS")))
                    ]
                    + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(BlackText)
                        .AutoWrapText(true)
                        .Text(FText::FromString(TEXT("Reserved for v0.14. The Canvas will arrange Codex Signs into a semantic Spell Graph and compile it into the existing spell systems.")))
                    ]
                ]
            ]
        ];

    GEngine->GameViewport->AddViewportWidgetContent(CanvasWidget.ToSharedRef(), 4997);

    NavigationWidget = SNew(SBox)
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
                [ MakePageButton(EInnerRealmPage::Canvas, TEXT("CANVAS / LATER")) ]
            ]
        ];

    GEngine->GameViewport->AddViewportWidgetContent(NavigationWidget.ToSharedRef(), 5002);
}'''
    text = replace_once(text, marker, ui, "InnerRealm top navigation / Codex / Canvas pages")

print("[5/6] Updating widget cleanup...")
if "CodexWidget.IsValid()" not in text:
    marker = '''    if (PreviewFrameWidget.IsValid() && GEngine && GEngine->GameViewport)\n    {\n        GEngine->GameViewport->RemoveViewportWidgetContent(PreviewFrameWidget.ToSharedRef());\n    }\n\n    EditorWidget.Reset();\n    PreviewFrameWidget.Reset();'''
    replacement = '''    if (PreviewFrameWidget.IsValid() && GEngine && GEngine->GameViewport)\n    {\n        GEngine->GameViewport->RemoveViewportWidgetContent(PreviewFrameWidget.ToSharedRef());\n    }\n    if (CodexWidget.IsValid() && GEngine && GEngine->GameViewport)\n    {\n        GEngine->GameViewport->RemoveViewportWidgetContent(CodexWidget.ToSharedRef());\n    }\n    if (CanvasWidget.IsValid() && GEngine && GEngine->GameViewport)\n    {\n        GEngine->GameViewport->RemoveViewportWidgetContent(CanvasWidget.ToSharedRef());\n    }\n    if (NavigationWidget.IsValid() && GEngine && GEngine->GameViewport)\n    {\n        GEngine->GameViewport->RemoveViewportWidgetContent(NavigationWidget.ToSharedRef());\n    }\n\n    NavigationWidget.Reset();\n    EditorWidget.Reset();\n    PreviewFrameWidget.Reset();\n    CodexWidget.Reset();\n    CanvasWidget.Reset();'''
    text = replace_once(text, marker, replacement, "InnerRealm page widget cleanup")

write(inner_cpp, text)

print("[6/6] Hiding 3D spell preview outside the Spell page...")
text = read(preview_cpp)
if "IsSpellWorkbenchVisible()" not in text:
    text = replace_once(
        text,
        "    if (InnerRealm && InnerRealm->IsActive())",
        "    if (InnerRealm && InnerRealm->IsSpellWorkbenchVisible())",
        "SpellPreview page visibility")
write(preview_cpp, text)

world_codex_h = ROOT / "Plugins/WorldCodex/Source/WorldCodex/Public/WorldCodexSubsystem.h"
if not world_codex_h.exists():
    raise RuntimeError("WorldCodex static files were not extracted from the ZIP.")

print()
print("v0.13.4 World Codex + TAB navigation patch applied successfully.")
print("Spell casting data/execution remains unchanged by this patch.")
