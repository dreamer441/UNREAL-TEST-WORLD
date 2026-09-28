from pathlib import Path

ROOT = Path(__file__).resolve().parent
CPP = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Private/InnerRealmSubsystem.cpp"

if not CPP.exists():
    raise RuntimeError(f"Expected file missing: {CPP}")

text = CPP.read_text(encoding="utf-8").replace("\r\n", "\n")

start_marker = '''                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
                        [ Section(TEXT("MULTIPLE OBJECTS")) ]'''

end_marker = '''                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
                        [ Section(TEXT("SIZE / SHAPE DIMENSIONS")) ]'''

start = text.find(start_marker)
if start < 0:
    raise RuntimeError("Could not find MULTIPLE OBJECTS section start.")

end = text.find(end_marker, start)
if end < 0:
    raise RuntimeError("Could not find SIZE / SHAPE DIMENSIONS section after MULTIPLE OBJECTS.")

fixed_block = r'''                        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 3)
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

'''

text = text[:start] + fixed_block + text[end:]

check_start = text.find(start_marker)
check_end = text.find(end_marker, check_start)
section = text[check_start:check_end]

if ".Padding(0,3)\n                        .Visibility_Lambda" in section:
    raise RuntimeError("Slot-level Visibility_Lambda remains after patch.")
if ".Padding(0,0,0,9)\n                        .Visibility_Lambda" in section:
    raise RuntimeError("Slot-level Visibility_Lambda remains after patch.")

CPP.write_text(text, encoding="utf-8", newline="\n")

print("v0.13.2.1 Slate visibility fix applied.")
print("Conditional visibility is now attached to child SBox widgets.")
