#include "InnerRealmSubsystem.h"

#include "InnerRealmActor.h"
#include "EarthSpellMath.h"
#include "SpellParameterRanges.h"
#include "LiveSpellSessionSubsystem.h"
#include "SpellCreationSubsystem.h"
#include "SpellCastingBindingSubsystem.h"
#include "WorldCodexSubsystem.h"
#include "SpellGraphSubsystem.h"
#include "SpellLoadoutSubsystem.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PawnMovementComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Input/SInputKeySelector.h"
#include "Widgets/Input/SSlider.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SConstraintCanvas.h"
#include "Widgets/Layout/SScrollBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Text/STextBlock.h"
#include "Styling/CoreStyle.h"

namespace InnerRealmEditor
{
    static void GetDimensionRange(const EEarthSpellShape Shape, const int32 Index, float& OutMin, float& OutMax)
    {
        switch (Shape)
        {
            case EEarthSpellShape::Sphere:
                OutMin = SpellParameterRanges::MinSphereRadiusCm;
                OutMax = SpellParameterRanges::MaxSphereRadiusCm;
                break;
            case EEarthSpellShape::Cube:
                OutMin = SpellParameterRanges::MinCubeSideCm;
                OutMax = SpellParameterRanges::MaxCubeSideCm;
                break;
            case EEarthSpellShape::Cone:
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

void UInnerRealmSubsystem::Deinitialize()
{
    if (bActive)
    {
        ExitRealm();
    }
    RemoveEditorWidget();
    Super::Deinitialize();
}

void UInnerRealmSubsystem::Tick(float DeltaTime)
{
    UWorld* World = GetWorld();
    if (!World || !World->IsGameWorld())
    {
        return;
    }

    APlayerController* PC = World->GetFirstPlayerController();
    if (!PC)
    {
        return;
    }

    if (PC->WasInputKeyJustPressed(EKeys::Tab))
    {
        bActive ? ExitRealm() : EnterRealm();
    }
}

TStatId UInnerRealmSubsystem::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UInnerRealmSubsystem, STATGROUP_Tickables);
}

USpellCreationSubsystem* UInnerRealmSubsystem::GetSpellCreation() const
{
    UWorld* World = GetWorld();
    return World ? World->GetSubsystem<USpellCreationSubsystem>() : nullptr;
}

USpellCastingBindingSubsystem* UInnerRealmSubsystem::GetSpellBindings() const
{
    UWorld* World = GetWorld();
    return World ? World->GetSubsystem<USpellCastingBindingSubsystem>() : nullptr;
}

UWorldCodexSubsystem* UInnerRealmSubsystem::GetWorldCodex() const
{
    UWorld* World = GetWorld();
    return World ? World->GetSubsystem<UWorldCodexSubsystem>() : nullptr;
}

USpellGraphSubsystem* UInnerRealmSubsystem::GetSpellGraph() const
{
    UWorld* World = GetWorld();
    return World ? World->GetSubsystem<USpellGraphSubsystem>() : nullptr;
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
        TEXT("CONCEPT ID\n%s\n\nCATEGORY\n%s\n\nTIER\n%s\n\nSTATUS\n%s\n\nOWNING SYSTEM\n%s\n\nDESCRIPTION\n%s\n\nPROVIDES CAPABILITIES\n%s\n\nREQUIRES CAPABILITIES\n%s\n\nRELATIONSHIPS\n%s"),
        *Entry->ConceptId.ToString(),
        *CodexCategoryToText(Entry->Category).ToString(),
        *CodexTierToText(Entry->Tier).ToString(),
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

FEarthSpellDefinition UInnerRealmSubsystem::ReadSpell() const
{
    if (const USpellCreationSubsystem* SpellCreation = GetSpellCreation())
    {
        return SpellCreation->GetStoredSpellDefinition();
    }
    return FEarthSpellDefinition();
}

void UInnerRealmSubsystem::WriteSpell(const FEarthSpellDefinition& Spell)
{
    if (USpellCreationSubsystem* SpellCreation = GetSpellCreation())
    {
        SpellCreation->SetStoredSpellDefinition(Spell);
    }
}

void UInnerRealmSubsystem::SetShape(const EEarthSpellShape Shape)
{
    FEarthSpellDefinition Spell = ReadSpell();
    Spell.Shape = Shape;
    WriteSpell(Spell);
}

FText UInnerRealmSubsystem::GetShapeName() const
{
    switch (ReadSpell().Shape)
    {
        case EEarthSpellShape::Sphere: return FText::FromString(TEXT("SPHERE"));
        case EEarthSpellShape::Cube:   return FText::FromString(TEXT("CUBE"));
        case EEarthSpellShape::Cone:   return FText::FromString(TEXT("CONE"));
        default:                       return FText::FromString(TEXT("EARTH FORM"));
    }
}

FInputChord UInnerRealmSubsystem::GetBindingChord(const ESpellLiveAction Action) const
{
    if (const USpellCastingBindingSubsystem* Bindings = GetSpellBindings())
    {
        const FKey Key = Bindings->GetBinding(Action);
        if (Key.IsValid())
        {
            return FInputChord(Key);
        }
    }
    return FInputChord();
}

void UInnerRealmSubsystem::HandleBindingSelected(const ESpellLiveAction Action, const FInputChord& Chord)
{
    if (Chord.Key == EKeys::Tab)
    {
        ExitRealm();
        return;
    }

    USpellCastingBindingSubsystem* Bindings = GetSpellBindings();
    if (!Bindings)
    {
        return;
    }

    if (!Chord.Key.IsValid())
    {
        Bindings->ClearBinding(Action);
        return;
    }

    // Pressing the same assigned key again is the explicit empty/unassign gesture.
    if (Bindings->GetBinding(Action) == Chord.Key)
    {
        Bindings->ClearBinding(Action);
        return;
    }

    if (!Bindings->SetBinding(Action, Chord.Key) && GEngine)
    {
        GEngine->AddOnScreenDebugMessage(-1, 1.5f, FColor::Yellow,
            TEXT("That key is reserved for movement/camera/casting."));
    }
}

FText UInnerRealmSubsystem::GetCurrentSpellSummary() const
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
        TEXT("EARTH / %s / %s   |   x%d %s   |   speed %.0f m/s   |   density %.0f kg/m3   |   mass %.0f kg   |   distance %.1f m"),
        *GetShapeName().ToString(),
        Orientation,
        Spell.Amount,
        Spell.Amount > 1
            ? (Spell.Arrangement == ESpellArrangement::Circle ? TEXT("CIRCLE") : TEXT("LINE"))
            : TEXT("SINGLE"),
        Spell.SpeedMps,
        Spell.DensityKgPerM3,
        UEarthSpellMath::CalculateMassKg(Spell),
        Spell.DistanceM));
}

AInnerRealmActor* UInnerRealmSubsystem::GetOrCreateRealmActor()
{
    if (RealmActor.IsValid())
    {
        return RealmActor.Get();
    }

    UWorld* World = GetWorld();
    if (!World)
    {
        return nullptr;
    }

    FActorSpawnParameters Params;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    AInnerRealmActor* Actor = World->SpawnActor<AInnerRealmActor>(
        AInnerRealmActor::StaticClass(), FVector::ZeroVector, FRotator::ZeroRotator, Params);
    if (Actor)
    {
        RealmActor = Actor;
    }
    return Actor;
}

void UInnerRealmSubsystem::EnterRealm()
{
    if (bActive)
    {
        return;
    }

    UWorld* World = GetWorld();
    APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;
    AInnerRealmActor* Realm = GetOrCreateRealmActor();
    if (!PC || !Realm)
    {
        return;
    }

    bActive = true;
    PreviousViewTarget = PC->GetViewTarget();
    if (ULiveSpellSessionSubsystem* LiveSession = World->GetSubsystem<ULiveSpellSessionSubsystem>())
    {
        LiveSession->ResetSession();
    }
    if (USpellCastingBindingSubsystem* Bindings = GetSpellBindings())
    {
        Bindings->SetSuspended(true);
    }

    CaptureAndFreezePlayer(PC);
    PositionRealmNearPlayer(Realm, PC);


    ApplyPlayerInputState(true);
    PC->SetViewTargetWithBlend(Realm, 0.15f);
    CreateEditorWidget();
}

void UInnerRealmSubsystem::ExitRealm()
{
    if (!bActive)
    {
        return;
    }

    UWorld* World = GetWorld();
    APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;


    RemoveEditorWidget();
    if (PC)
    {
        AActor* ReturnTarget = PreviousViewTarget.IsValid()
            ? PreviousViewTarget.Get()
            : Cast<AActor>(PC->GetPawn());
        if (ReturnTarget)
        {
            PC->SetViewTargetWithBlend(ReturnTarget, 0.15f);
        }
    }

    PreviousViewTarget.Reset();
    bActive = false;
    if (USpellCastingBindingSubsystem* Bindings = GetSpellBindings())
    {
        Bindings->SetSuspended(false);
    }
    ApplyPlayerInputState(false);
    RestoreFrozenPlayer();
}

void UInnerRealmSubsystem::CaptureAndFreezePlayer(APlayerController* PC)
{
    FrozenPawn.Reset();
    bSavedCharacterMovement = false;

    APawn* Pawn = PC ? PC->GetPawn() : nullptr;
    if (!Pawn)
    {
        return;
    }

    FrozenPawn = Pawn;
    FrozenPawnTransform = Pawn->GetActorTransform();

    if (ACharacter* Character = Cast<ACharacter>(Pawn))
    {
        if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
        {
            SavedMovementMode = static_cast<uint8>(Movement->MovementMode);
            SavedCustomMovementMode = Movement->CustomMovementMode;
            bSavedCharacterMovement = true;
            Movement->StopMovementImmediately();
            Movement->DisableMovement();
        }
    }
    else if (UPawnMovementComponent* Movement = Pawn->GetMovementComponent())
    {
        Movement->StopMovementImmediately();
        Movement->Deactivate();
    }
}

void UInnerRealmSubsystem::RestoreFrozenPlayer()
{
    APawn* Pawn = FrozenPawn.Get();
    if (!Pawn)
    {
        FrozenPawn.Reset();
        bSavedCharacterMovement = false;
        return;
    }

    Pawn->SetActorTransform(FrozenPawnTransform, false, nullptr, ETeleportType::TeleportPhysics);

    if (bSavedCharacterMovement)
    {
        if (ACharacter* Character = Cast<ACharacter>(Pawn))
        {
            if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
            {
                Movement->SetMovementMode(static_cast<EMovementMode>(SavedMovementMode), SavedCustomMovementMode);
            }
        }
    }
    else if (UPawnMovementComponent* Movement = Pawn->GetMovementComponent())
    {
        Movement->Activate(true);
    }

    FrozenPawn.Reset();
    bSavedCharacterMovement = false;
}

void UInnerRealmSubsystem::PositionRealmNearPlayer(AInnerRealmActor* Realm, APlayerController* PC)
{
    if (!Realm)
    {
        return;
    }

    FVector Base = FVector::ZeroVector;
    if (PC && PC->GetPawn())
    {
        Base = PC->GetPawn()->GetActorLocation();
    }
    Realm->SetActorLocation(Base + FVector(0.0f, 0.0f, 10000.0f));
}

void UInnerRealmSubsystem::ApplyPlayerInputState(const bool bEntering)
{
    UWorld* World = GetWorld();
    APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;
    if (!PC)
    {
        return;
    }

    PC->SetIgnoreMoveInput(bEntering);
    PC->SetIgnoreLookInput(bEntering);
    PC->bShowMouseCursor = bEntering;

    if (bEntering)
    {
        FInputModeGameAndUI Mode;
        Mode.SetHideCursorDuringCapture(false);
        Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
        PC->SetInputMode(Mode);
    }
    else
    {
        PC->SetInputMode(FInputModeGameOnly());
        PC->bShowMouseCursor = false;
    }
}

float UInnerRealmSubsystem::GetSpeedSlider() const
{
    return SpellParameterRanges::Normalize(ReadSpell().SpeedMps, SpellParameterRanges::MinSpeedMps, SpellParameterRanges::MaxSpeedMps);
}

float UInnerRealmSubsystem::GetDistanceSlider() const
{
    return SpellParameterRanges::Normalize(ReadSpell().DistanceM, SpellParameterRanges::MinDistanceM, SpellParameterRanges::MaxDistanceM);
}

float UInnerRealmSubsystem::GetDensitySlider() const
{
    return SpellParameterRanges::Normalize(ReadSpell().DensityKgPerM3, SpellParameterRanges::MinDensityKgPerM3, SpellParameterRanges::MaxDensityKgPerM3);
}

float UInnerRealmSubsystem::GetHardnessSlider() const { return ReadSpell().Hardness; }
float UInnerRealmSubsystem::GetToughnessSlider() const { return ReadSpell().Toughness; }
float UInnerRealmSubsystem::GetElasticitySlider() const { return ReadSpell().Elasticity; }

void UInnerRealmSubsystem::SetSpeedSlider(const float Value)
{
    FEarthSpellDefinition Spell = ReadSpell();
    Spell.SpeedMps = SpellParameterRanges::Denormalize(Value, SpellParameterRanges::MinSpeedMps, SpellParameterRanges::MaxSpeedMps);
    WriteSpell(Spell);
}

void UInnerRealmSubsystem::SetDistanceSlider(const float Value)
{
    FEarthSpellDefinition Spell = ReadSpell();
    Spell.DistanceM = SpellParameterRanges::Denormalize(Value, SpellParameterRanges::MinDistanceM, SpellParameterRanges::MaxDistanceM);
    WriteSpell(Spell);
}

void UInnerRealmSubsystem::SetDensitySlider(const float Value)
{
    FEarthSpellDefinition Spell = ReadSpell();
    Spell.DensityKgPerM3 = SpellParameterRanges::Denormalize(Value, SpellParameterRanges::MinDensityKgPerM3, SpellParameterRanges::MaxDensityKgPerM3);
    WriteSpell(Spell);
}

void UInnerRealmSubsystem::SetHardnessSlider(const float Value)
{
    FEarthSpellDefinition Spell = ReadSpell();
    Spell.Hardness = FMath::Clamp(Value, 0.0f, 1.0f);
    WriteSpell(Spell);
}

void UInnerRealmSubsystem::SetToughnessSlider(const float Value)
{
    FEarthSpellDefinition Spell = ReadSpell();
    Spell.Toughness = FMath::Clamp(Value, 0.0f, 1.0f);
    WriteSpell(Spell);
}

void UInnerRealmSubsystem::SetElasticitySlider(const float Value)
{
    FEarthSpellDefinition Spell = ReadSpell();
    Spell.Elasticity = FMath::Clamp(Value, 0.0f, 1.0f);
    WriteSpell(Spell);
}

float UInnerRealmSubsystem::GetDimensionSlider(const int32 Index) const
{
    const FEarthSpellDefinition Spell = ReadSpell();
    float Value = Spell.SphereRadiusCm;

    if (Spell.Shape == EEarthSpellShape::Cube)
    {
        Value = Index == 0 ? Spell.CubeXcm : (Index == 1 ? Spell.CubeYcm : Spell.CubeZcm);
    }
    else if (Spell.Shape == EEarthSpellShape::Cone)
    {
        Value = Index == 0 ? Spell.ConeRadiusCm : Spell.ConeHeightCm;
    }

    float Min = 0.0f;
    float Max = 1.0f;
    InnerRealmEditor::GetDimensionRange(Spell.Shape, Index, Min, Max);
    return SpellParameterRanges::Normalize(Value, Min, Max);
}

void UInnerRealmSubsystem::SetDimensionSlider(const int32 Index, const float SliderValue)
{
    FEarthSpellDefinition Spell = ReadSpell();
    float Min = 0.0f;
    float Max = 1.0f;
    InnerRealmEditor::GetDimensionRange(Spell.Shape, Index, Min, Max);
    const float Value = SpellParameterRanges::Denormalize(SliderValue, Min, Max);

    if (Spell.Shape == EEarthSpellShape::Sphere)
    {
        Spell.SphereRadiusCm = Value;
    }
    else if (Spell.Shape == EEarthSpellShape::Cube)
    {
        if (Index == 0) Spell.CubeXcm = Value;
        else if (Index == 1) Spell.CubeYcm = Value;
        else Spell.CubeZcm = Value;
    }
    else
    {
        if (Index == 0) Spell.ConeRadiusCm = Value;
        else Spell.ConeHeightCm = Value;
    }

    WriteSpell(Spell);
}

EVisibility UInnerRealmSubsystem::GetDimensionVisibility(const int32 Index) const
{
    const EEarthSpellShape Shape = ReadSpell().Shape;
    if (Shape == EEarthSpellShape::Sphere && Index > 0) return EVisibility::Collapsed;
    if (Shape == EEarthSpellShape::Cone && Index > 1) return EVisibility::Collapsed;
    return EVisibility::Visible;
}

FText UInnerRealmSubsystem::GetDimensionLabel(const int32 Index) const
{
    const FEarthSpellDefinition Spell = ReadSpell();
    FString Name;
    float Value = 0.0f;

    if (Spell.Shape == EEarthSpellShape::Sphere)
    {
        Name = TEXT("Radius");
        Value = Spell.SphereRadiusCm;
    }
    else if (Spell.Shape == EEarthSpellShape::Cube)
    {
        if (Index == 0) { Name = TEXT("X"); Value = Spell.CubeXcm; }
        else if (Index == 1) { Name = TEXT("Y"); Value = Spell.CubeYcm; }
        else { Name = TEXT("Z"); Value = Spell.CubeZcm; }
    }
    else
    {
        if (Index == 0) { Name = TEXT("Radius"); Value = Spell.ConeRadiusCm; }
        else { Name = TEXT("Height"); Value = Spell.ConeHeightCm; }
    }

    return FText::FromString(FString::Printf(TEXT("%s: %.0f cm"), *Name, Value));
}

void UInnerRealmSubsystem::CreateEditorWidget()
{
    if (EditorWidget.IsValid() || !GEngine || !GEngine->GameViewport)
    {
        return;
    }

    static FTextBlockStyle BlackKeyTextStyle = FCoreStyle::Get().GetWidgetStyle<FTextBlockStyle>("NormalText");
    BlackKeyTextStyle.SetColorAndOpacity(FSlateColor(FLinearColor::Black));
    const FSlateColor BlackText(FLinearColor::Black);

    auto MakeBindSelector = [this](const ESpellLiveAction Action) -> TSharedRef<SWidget>
    {
        return SNew(SBox)
            .WidthOverride(92.0f)
            [
                SNew(SInputKeySelector)
                .SelectedKey_Lambda([this, Action]() { return GetBindingChord(Action); })
                .OnKeySelected_Lambda([this, Action](const FInputChord& Chord)
                {
                    HandleBindingSelected(Action, Chord);
                })
                .AllowGamepadKeys(false)
                .AllowModifierKeys(false)
                .EscapeCancelsSelection(true)
                .KeySelectionText(FText::FromString(TEXT("key")))
                .NoKeySpecifiedText(FText::FromString(TEXT("+")))
                .TextStyle(&BlackKeyTextStyle)
                .Margin(FMargin(6.0f, 3.0f))
            ];
    };

    auto MakeShapeControl = [this, &MakeBindSelector, BlackText](
        const ESpellLiveAction Action,
        const EEarthSpellShape Shape,
        const TCHAR* Label) -> TSharedRef<SWidget>
    {
        return SNew(SHorizontalBox)
            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0, 2, 8, 2)
            [ MakeBindSelector(Action) ]
            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0, 2)
            [
                SNew(SButton)
                .IsFocusable(false)
                .ContentPadding(FMargin(12.0f, 6.0f))
                .OnClicked_Lambda([this, Shape]()
                {
                    SetShape(Shape);
                    return FReply::Handled();
                })
                [
                    SNew(STextBlock)
                    .ColorAndOpacity(BlackText)
                    .Text_Lambda([this, Shape, Label]()
                    {
                        return FText::FromString(ReadSpell().Shape == Shape
                            ? FString::Printf(TEXT("[ %s ]"), Label)
                            : FString(Label));
                    })
                ]
            ];
    };

    auto MakeOrientationControl = [this, BlackText](
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

    auto MakeDimension = [this, &MakeBindSelector, BlackText](
        const EEarthSpellShape Shape,
        const int32 Index,
        const ESpellLiveAction Action) -> TSharedRef<SWidget>
    {
        return SNew(SVerticalBox)
            .Visibility_Lambda([this, Shape]()
            {
                return ReadSpell().Shape == Shape ? EVisibility::Visible : EVisibility::Collapsed;
            })
            + SVerticalBox::Slot().AutoHeight().Padding(0, 3)
            [
                SNew(SHorizontalBox)
                + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0, 0, 8, 0)
                [ MakeBindSelector(Action) ]
                + SHorizontalBox::Slot().FillWidth(1.0f).VAlign(VAlign_Center)
                [
                    SNew(STextBlock)
                    .ColorAndOpacity(BlackText)
                    .Text_Lambda([this, Index]() { return GetDimensionLabel(Index); })
                ]
            ]
            + SVerticalBox::Slot().AutoHeight().Padding(100, 0, 0, 9)
            [
                SNew(SSlider)
                .IsFocusable(false)
                .Value_Lambda([this, Index]() { return GetDimensionSlider(Index); })
                .OnValueChanged_Lambda([this, Index](float V) { SetDimensionSlider(Index, V); })
            ];
    };

    auto Section = [BlackText](const TCHAR* Title) -> TSharedRef<SWidget>
    {
        return SNew(SBorder)
            .Padding(FMargin(8.0f, 6.0f))
            .BorderBackgroundColor(FLinearColor(0.78f, 0.76f, 0.70f, 0.96f))
            [
                SNew(STextBlock)
                .ColorAndOpacity(BlackText)
                .Text(FText::FromString(Title))
            ];
    };

    auto MakeArrangementControl = [this, BlackText](
        const ESpellArrangement Arrangement,
        const TCHAR* Label) -> TSharedRef<SWidget>
    {
        return SNew(SButton)
            .IsFocusable(false)
            .OnClicked_Lambda([this, Arrangement]()
            {
                FEarthSpellDefinition Spell = ReadSpell();
                Spell.Arrangement = Arrangement;
                WriteSpell(Spell);
                return FReply::Handled();
            })
            [
                SNew(STextBlock)
                .ColorAndOpacity(BlackText)
                .Text_Lambda([this, Arrangement, Label]()
                {
                    return FText::FromString(ReadSpell().Arrangement == Arrangement
                        ? FString::Printf(TEXT("[ %s ]"), Label)
                        : FString(Label));
                })
            ];
    };

    auto MakePatternAxisControl = [this, BlackText](
        const ESpellPatternAxis Axis,
        const TCHAR* Label) -> TSharedRef<SWidget>
    {
        return SNew(SButton)
            .IsFocusable(false)
            .OnClicked_Lambda([this, Axis]()
            {
                FEarthSpellDefinition Spell = ReadSpell();
                Spell.PatternAxis = Axis;
                WriteSpell(Spell);
                return FReply::Handled();
            })
            [
                SNew(STextBlock)
                .ColorAndOpacity(BlackText)
                .Text_Lambda([this, Axis, Label]()
                {
                    return FText::FromString(ReadSpell().PatternAxis == Axis
                        ? FString::Printf(TEXT("[ %s ]"), Label)
                        : FString(Label));
                })
            ];
    };

    auto MakePatternOrientationControl = [this, BlackText](
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

    auto MakeMotionDirectionControl = [this, BlackText](
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

    auto MakeReadySlot = [this, BlackText](const int32 SlotIndex, const TCHAR* Label) -> TSharedRef<SWidget>
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

    EditorWidget = SNew(SBox)
        .Visibility_Lambda([this]()
        {
            return ActivePage == EInnerRealmPage::Spell
                ? EVisibility::SelfHitTestInvisible
                : EVisibility::Collapsed;
        })
        .HAlign(HAlign_Left)
        .VAlign(VAlign_Center)
        [
            SNew(SBorder)
            .Padding(FMargin(24.0f))
            .BorderBackgroundColor(FLinearColor(0.92f, 0.90f, 0.84f, 0.96f))
            [
                SNew(SBox)
                .WidthOverride(820.0f)
                .HeightOverride(760.0f)
                [
                    SNew(SScrollBox)
                    + SScrollBox::Slot()
                    [
                        SNew(SVerticalBox)

                        + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0, 0, 0, 4)
                        [ SNew(STextBlock).ColorAndOpacity(BlackText).Text(FText::FromString(TEXT("MEDITATION REALM / EARTH SPELL CONSTRUCTION"))) ]

                        + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0, 0, 0, 8)
                        [ SNew(STextBlock).ColorAndOpacity(BlackText).Text(FText::FromString(TEXT("Sliders are persistent defaults. Key boxes configure temporary live overrides. Press the same assigned key again to clear it."))) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 7)
                        [ SNew(STextBlock).ColorAndOpacity(BlackText).Text(FText::FromString(TEXT("LIVE HOLD: unpressed = TAB default; press starts at minimum; 1 s small, 2 s medium, 3 s maximum."))) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 14)
                        [ SNew(STextBlock).ColorAndOpacity(BlackText).Text_Lambda([this]() { return GetCurrentSpellSummary(); }) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 3)
                        [ Section(TEXT("ELEMENT")) ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0, 4, 0, 8)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0, 0, 8, 0)
                            [ MakeBindSelector(ESpellLiveAction::SelectEarth) ]
                            + SHorizontalBox::Slot().FillWidth(1.0f).VAlign(VAlign_Center)
                            [ SNew(STextBlock).ColorAndOpacity(BlackText).Text(FText::FromString(TEXT("EARTH  (tap = select; green aura confirms it)"))) ]
                        ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
                        [ Section(TEXT("SHAPE")) ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0, 4, 0, 4)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().Padding(0,0,14,0)[MakeShapeControl(ESpellLiveAction::SelectSphere, EEarthSpellShape::Sphere, TEXT("Sphere"))]
                            + SHorizontalBox::Slot().AutoWidth().Padding(0,0,14,0)[MakeShapeControl(ESpellLiveAction::SelectCube, EEarthSpellShape::Cube, TEXT("Cube"))]
                            + SHorizontalBox::Slot().AutoWidth()[MakeShapeControl(ESpellLiveAction::SelectCone, EEarthSpellShape::Cone, TEXT("Cone"))]
                        ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
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

                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
                        [ Section(TEXT("MULTIPLE OBJECTS")) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        [
                            SNew(STextBlock)
                            .ColorAndOpacity(BlackText)
                            .Text_Lambda([this]()
                            {
                                return FText::FromString(FString::Printf(
                                    TEXT("Amount: %d   (1 = single object; pattern activates above 1)"),
                                    ReadSpell().Amount));
                            })
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,9)
                        [
                            SNew(SSlider)
                            .IsFocusable(false)
                            .Value_Lambda([this]()
                            {
                                return static_cast<float>(ReadSpell().Amount - SpellPatternRanges::MinAmount)
                                    / static_cast<float>(SpellPatternRanges::MaxAmount - SpellPatternRanges::MinAmount);
                            })
                            .OnValueChanged_Lambda([this](float V)
                            {
                                FEarthSpellDefinition Spell = ReadSpell();
                                Spell.Amount = FMath::Clamp(
                                    FMath::RoundToInt(FMath::Lerp(
                                        static_cast<float>(SpellPatternRanges::MinAmount),
                                        static_cast<float>(SpellPatternRanges::MaxAmount),
                                        V)),
                                    SpellPatternRanges::MinAmount,
                                    SpellPatternRanges::MaxAmount);
                                WriteSpell(Spell);
                            })
                        ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
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
                                + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,12,0)
                                [
                                    SNew(STextBlock)
                                    .ColorAndOpacity(BlackText)
                                    .Text(FText::FromString(TEXT("Arrangement:")))
                                ]
                                + SHorizontalBox::Slot().AutoWidth().Padding(0,0,10,0)
                                [ MakeArrangementControl(ESpellArrangement::Line, TEXT("Line")) ]
                                + SHorizontalBox::Slot().AutoWidth()
                                [ MakeArrangementControl(ESpellArrangement::Circle, TEXT("Circle")) ]
                            ]
                        ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        [
                            SNew(SBox)
                            .Visibility_Lambda([this]()
                            {
                                const FEarthSpellDefinition Spell = ReadSpell();
                                return Spell.Amount > 1 && Spell.Arrangement == ESpellArrangement::Line
                                    ? EVisibility::Visible : EVisibility::Collapsed;
                            })
                            [
                                SNew(SHorizontalBox)
                                + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,12,0)
                                [
                                    SNew(STextBlock)
                                    .ColorAndOpacity(BlackText)
                                    .Text(FText::FromString(TEXT("Line axis:")))
                                ]
                                + SHorizontalBox::Slot().AutoWidth().Padding(0,0,10,0)
                                [ MakePatternAxisControl(ESpellPatternAxis::Forward, TEXT("Forward")) ]
                                + SHorizontalBox::Slot().AutoWidth().Padding(0,0,10,0)
                                [ MakePatternAxisControl(ESpellPatternAxis::Right, TEXT("Right")) ]
                                + SHorizontalBox::Slot().AutoWidth()
                                [ MakePatternAxisControl(ESpellPatternAxis::Up, TEXT("Up")) ]
                            ]
                        ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        [
                            SNew(SBox)
                            .Visibility_Lambda([this]()
                            {
                                const FEarthSpellDefinition Spell = ReadSpell();
                                return Spell.Amount > 1 && Spell.Arrangement == ESpellArrangement::Line
                                    ? EVisibility::Visible : EVisibility::Collapsed;
                            })
                            [
                                SNew(STextBlock)
                                .ColorAndOpacity(BlackText)
                                .Text_Lambda([this]()
                                {
                                    return FText::FromString(FString::Printf(
                                        TEXT("Spacing: %.0f cm"),
                                        ReadSpell().SpacingCm));
                                })
                            ]
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,9)
                        [
                            SNew(SBox)
                            .Visibility_Lambda([this]()
                            {
                                const FEarthSpellDefinition Spell = ReadSpell();
                                return Spell.Amount > 1 && Spell.Arrangement == ESpellArrangement::Line
                                    ? EVisibility::Visible : EVisibility::Collapsed;
                            })
                            [
                                SNew(SSlider)
                                .IsFocusable(false)
                                .Value_Lambda([this]()
                                {
                                    return SpellParameterRanges::Normalize(
                                        ReadSpell().SpacingCm,
                                        SpellPatternRanges::MinSpacingCm,
                                        SpellPatternRanges::MaxSpacingCm);
                                })
                                .OnValueChanged_Lambda([this](float V)
                                {
                                    FEarthSpellDefinition Spell = ReadSpell();
                                    Spell.SpacingCm = SpellParameterRanges::Denormalize(
                                        V,
                                        SpellPatternRanges::MinSpacingCm,
                                        SpellPatternRanges::MaxSpacingCm);
                                    WriteSpell(Spell);
                                })
                            ]
                        ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        [
                            SNew(SBox)
                            .Visibility_Lambda([this]()
                            {
                                const FEarthSpellDefinition Spell = ReadSpell();
                                return Spell.Amount > 1 && Spell.Arrangement == ESpellArrangement::Circle
                                    ? EVisibility::Visible : EVisibility::Collapsed;
                            })
                            [
                                SNew(STextBlock)
                                .ColorAndOpacity(BlackText)
                                .Text_Lambda([this]()
                                {
                                    return FText::FromString(FString::Printf(
                                        TEXT("Circle radius: %.0f cm"),
                                        ReadSpell().CircleRadiusCm));
                                })
                            ]
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,9)
                        [
                            SNew(SBox)
                            .Visibility_Lambda([this]()
                            {
                                const FEarthSpellDefinition Spell = ReadSpell();
                                return Spell.Amount > 1 && Spell.Arrangement == ESpellArrangement::Circle
                                    ? EVisibility::Visible : EVisibility::Collapsed;
                            })
                            [
                                SNew(SSlider)
                                .IsFocusable(false)
                                .Value_Lambda([this]()
                                {
                                    return SpellParameterRanges::Normalize(
                                        ReadSpell().CircleRadiusCm,
                                        SpellPatternRanges::MinCircleRadiusCm,
                                        SpellPatternRanges::MaxCircleRadiusCm);
                                })
                                .OnValueChanged_Lambda([this](float V)
                                {
                                    FEarthSpellDefinition Spell = ReadSpell();
                                    Spell.CircleRadiusCm = SpellParameterRanges::Denormalize(
                                        V,
                                        SpellPatternRanges::MinCircleRadiusCm,
                                        SpellPatternRanges::MaxCircleRadiusCm);
                                    WriteSpell(Spell);
                                })
                            ]
                        ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,7,0,3)
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

                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
                        [ Section(TEXT("SIZE / SHAPE DIMENSIONS")) ]
                        + SVerticalBox::Slot().AutoHeight()[MakeDimension(EEarthSpellShape::Sphere, 0, ESpellLiveAction::SphereRadius)]
                        + SVerticalBox::Slot().AutoHeight()[MakeDimension(EEarthSpellShape::Cube, 0, ESpellLiveAction::CubeX)]
                        + SVerticalBox::Slot().AutoHeight()[MakeDimension(EEarthSpellShape::Cube, 1, ESpellLiveAction::CubeY)]
                        + SVerticalBox::Slot().AutoHeight()[MakeDimension(EEarthSpellShape::Cube, 2, ESpellLiveAction::CubeZ)]
                        + SVerticalBox::Slot().AutoHeight()[MakeDimension(EEarthSpellShape::Cone, 0, ESpellLiveAction::ConeRadius)]
                        + SVerticalBox::Slot().AutoHeight()[MakeDimension(EEarthSpellShape::Cone, 1, ESpellLiveAction::ConeHeight)]

                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
                        [ Section(TEXT("MOTION / MATERIAL")) ]

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
                        ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,8,0)[MakeBindSelector(ESpellLiveAction::Speed)]
                            + SHorizontalBox::Slot().FillWidth(1.0f).VAlign(VAlign_Center)
                            [ SNew(STextBlock).ColorAndOpacity(BlackText).Text_Lambda([this](){ return FText::FromString(FString::Printf(TEXT("Speed: %.1f m/s   (0 = create; gravity still applies)"), ReadSpell().SpeedMps)); }) ]
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(100,0,0,9)
                        [ SNew(SSlider).IsFocusable(false).Value_Lambda([this](){ return GetSpeedSlider(); }).OnValueChanged_Lambda([this](float V){ SetSpeedSlider(V); }) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,8,0)[MakeBindSelector(ESpellLiveAction::Density)]
                            + SHorizontalBox::Slot().FillWidth(1.0f).VAlign(VAlign_Center)
                            [ SNew(STextBlock).ColorAndOpacity(BlackText).Text_Lambda([this](){ return FText::FromString(FString::Printf(TEXT("Density: %.0f kg/m3   |   derived mass: %.1f kg"), ReadSpell().DensityKgPerM3, UEarthSpellMath::CalculateMassKg(ReadSpell()))); }) ]
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(100,0,0,9)
                        [ SNew(SSlider).IsFocusable(false).Value_Lambda([this](){ return GetDensitySlider(); }).OnValueChanged_Lambda([this](float V){ SetDensitySlider(V); }) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,8,0)[MakeBindSelector(ESpellLiveAction::Hardness)]
                            + SHorizontalBox::Slot().FillWidth(1.0f).VAlign(VAlign_Center)
                            [ SNew(STextBlock).ColorAndOpacity(BlackText).Text_Lambda([this](){ return FText::FromString(FString::Printf(TEXT("Hardness: %.2f"), ReadSpell().Hardness)); }) ]
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(100,0,0,9)
                        [ SNew(SSlider).IsFocusable(false).Value_Lambda([this](){ return GetHardnessSlider(); }).OnValueChanged_Lambda([this](float V){ SetHardnessSlider(V); }) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,8,0)[MakeBindSelector(ESpellLiveAction::Toughness)]
                            + SHorizontalBox::Slot().FillWidth(1.0f).VAlign(VAlign_Center)
                            [ SNew(STextBlock).ColorAndOpacity(BlackText).Text_Lambda([this](){ return FText::FromString(FString::Printf(TEXT("Toughness: %.2f"), ReadSpell().Toughness)); }) ]
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(100,0,0,9)
                        [ SNew(SSlider).IsFocusable(false).Value_Lambda([this](){ return GetToughnessSlider(); }).OnValueChanged_Lambda([this](float V){ SetToughnessSlider(V); }) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,8,0)[MakeBindSelector(ESpellLiveAction::Elasticity)]
                            + SHorizontalBox::Slot().FillWidth(1.0f).VAlign(VAlign_Center)
                            [ SNew(STextBlock).ColorAndOpacity(BlackText).Text_Lambda([this](){ return FText::FromString(FString::Printf(TEXT("Elasticity: %.2f"), ReadSpell().Elasticity)); }) ]
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(100,0,0,9)
                        [ SNew(SSlider).IsFocusable(false).Value_Lambda([this](){ return GetElasticitySlider(); }).OnValueChanged_Lambda([this](float V){ SetElasticitySlider(V); }) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,7,0,3)
                        [ Section(TEXT("SPATIAL")) ]
                        + SVerticalBox::Slot().AutoHeight().Padding(0,3)
                        [
                            SNew(SHorizontalBox)
                            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,8,0)[MakeBindSelector(ESpellLiveAction::Distance)]
                            + SHorizontalBox::Slot().FillWidth(1.0f).VAlign(VAlign_Center)
                            [ SNew(STextBlock).ColorAndOpacity(BlackText).Text_Lambda([this](){ return FText::FromString(FString::Printf(TEXT("Distance: %.1f m   (additional distance from safe point in front of character)"), ReadSpell().DistanceM)); }) ]
                        ]
                        + SVerticalBox::Slot().AutoHeight().Padding(100,0,0,9)
                        [ SNew(SSlider).IsFocusable(false).Value_Lambda([this](){ return GetDistanceSlider(); }).OnValueChanged_Lambda([this](float V){ SetDistanceSlider(V); }) ]

                        + SVerticalBox::Slot().AutoHeight().Padding(0,10,0,0)
                        [ SNew(STextBlock).ColorAndOpacity(BlackText).Text(FText::FromString(TEXT("DEFAULT LIVE TEST: Q Earth | A primary shape dimension | S Speed | D Density | SPACE casts only after construction starts."))) ]
                    ]
                ]
            ]
        ];

    GEngine->GameViewport->AddViewportWidgetContent(EditorWidget.ToSharedRef(), 5000);

    PreviewFrameWidget = SNew(SBox)
        .Visibility_Lambda([this]()
        {
            // The preview is display-only. When Rune Canvas is open it sits
            // above the Canvas in the viewport Z-order, so Visible would put
            // its full-screen root into the hit-test path and swallow clicks
            // intended for Canvas buttons underneath.
            //
            // HitTestInvisible keeps the 3D preview/frame visible while
            // allowing pointer input to pass through to the Rune Canvas.
            return (ActivePage == EInnerRealmPage::Spell ||
                    ActivePage == EInnerRealmPage::Canvas)
                ? EVisibility::SelfHitTestInvisible
                : EVisibility::Collapsed;
        })
        .HAlign(HAlign_Right)
        .VAlign(VAlign_Center)
        [
            SNew(SBox)
            .WidthOverride(520.0f)
            .HeightOverride(760.0f)
            [
                SNew(SBorder)
                .Padding(FMargin(16.0f))
                .BorderBackgroundColor(FLinearColor(0.05f, 0.08f, 0.05f, 0.12f))
                [
                    SNew(SVerticalBox)

                    + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0, 0, 0, 5)
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

                    + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0, 0, 0, 8)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(FSlateColor(FLinearColor(0.86f, 0.96f, 0.87f, 1.0f)))
                        .Text(FText::FromString(TEXT("SPELL WORKBENCH / 3D PREVIEW")))
                    ]

                    + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(FSlateColor(FLinearColor(0.72f, 0.88f, 0.74f, 1.0f)))
                        .Text_Lambda([this]() { return GetCurrentSpellSummary(); })
                    ]

                    + SVerticalBox::Slot().FillHeight(1.0f)
                    [
                        SNew(SBox)
                    ]

                    + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0, 8, 0, 0)
                    [
                        SNew(STextBlock)
                        .ColorAndOpacity(FSlateColor(FLinearColor(0.78f, 0.90f, 0.80f, 1.0f)))
                        .Text(FText::FromString(TEXT("Reference mannequin shows spell scale, distance, density grid and speed rings.")))
                    ]
                ]
            ]
        ];

    GEngine->GameViewport->AddViewportWidgetContent(PreviewFrameWidget.ToSharedRef(), 4999);

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
            ECodexCategory::Value,
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

                            if (SelectedCodexConcept == EntryId)
                            {
                                return FText::FromString(FString::Printf(
                                    TEXT("[ %s ]  %s"),
                                    *CurrentEntry->Sign.Glyph,
                                    *CurrentEntry->DisplayName.ToString()));
                            }

                            return FText::FromString(FString::Printf(
                                TEXT("  %s    %s"),
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

    RebuildCanvasWidget();

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
                [ MakePageButton(EInnerRealmPage::Canvas, TEXT("RUNE CANVAS")) ]
            ]
        ];

    GEngine->GameViewport->AddViewportWidgetContent(NavigationWidget.ToSharedRef(), 5002);
}

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

void UInnerRealmSubsystem::RemoveEditorWidget()
{
    if (EditorWidget.IsValid() && GEngine && GEngine->GameViewport)
    {
        GEngine->GameViewport->RemoveViewportWidgetContent(EditorWidget.ToSharedRef());
    }
    if (PreviewFrameWidget.IsValid() && GEngine && GEngine->GameViewport)
    {
        GEngine->GameViewport->RemoveViewportWidgetContent(PreviewFrameWidget.ToSharedRef());
    }
    if (CodexWidget.IsValid() && GEngine && GEngine->GameViewport)
    {
        GEngine->GameViewport->RemoveViewportWidgetContent(CodexWidget.ToSharedRef());
    }
    if (CanvasWidget.IsValid() && GEngine && GEngine->GameViewport)
    {
        GEngine->GameViewport->RemoveViewportWidgetContent(CanvasWidget.ToSharedRef());
    }
    if (NavigationWidget.IsValid() && GEngine && GEngine->GameViewport)
    {
        GEngine->GameViewport->RemoveViewportWidgetContent(NavigationWidget.ToSharedRef());
    }

    NavigationWidget.Reset();
    EditorWidget.Reset();
    PreviewFrameWidget.Reset();
    CodexWidget.Reset();
    CanvasWidget.Reset();
}
