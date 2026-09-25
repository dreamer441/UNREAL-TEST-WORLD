#include "Misc/AutomationTest.h"
#include "LiveSpellState.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FLiveSpellStateGrammarTest, "AMADEUS.LiveSpell.Grammar", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FLiveSpellStateGrammarTest::RunTest(const FString&)
{
    FLiveSpellState State;
    State.SelectShape(ESpellShape::Sphere);
    State.SetParameterNormalized(ELiveSpellParameter::Speed, 0.5f);
    TestFalse(TEXT("Invalid order cannot cast"), State.CanCast());
    State.SelectElement(ESpellElement::Earth);
    State.SelectShape(ESpellShape::Sphere);
    State.SetParameterNormalized(ELiveSpellParameter::Density, 0.5f);
    TestTrue(TEXT("Valid grammar can cast"), State.CanCast());
    TestEqual(TEXT("Speed remains zero without speed modifier"), State.Resolve(FSpellDefinition()).Definition.SpeedMps, 0.0f);
    State.Reset();
    State.SelectElement(ESpellElement::Earth);
    State.SelectShape(ESpellShape::Sphere);
    State.SetParameterNormalized(ELiveSpellParameter::Speed, 0.5f);
    TestTrue(TEXT("Explicit speed is positive"), State.Resolve(FSpellDefinition()).Definition.SpeedMps > 0.0f);
    return true;
}
#endif
