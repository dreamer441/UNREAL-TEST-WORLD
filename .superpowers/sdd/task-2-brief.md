### Task 2: Extract the pure live construction state machine

**Files:**
- Create: Plugins/SpellCreation/Source/SpellCreation/Public/SpellParameterRanges.h
- Create: Plugins/LiveSpellCasting/Source/LiveSpellCasting/Public/LiveSpellTypes.h
- Create: Plugins/LiveSpellCasting/Source/LiveSpellCasting/Public/LiveSpellState.h
- Create: Plugins/LiveSpellCasting/Source/LiveSpellCasting/Private/LiveSpellState.cpp
- Create: Plugins/LiveSpellCasting/Source/LiveSpellCasting/Private/Tests/LiveSpellStateTests.cpp
- Modify: Plugins/LiveSpellCasting/Source/LiveSpellCasting/Public/LiveSpellSessionSubsystem.h
- Modify: Plugins/LiveSpellCasting/Source/LiveSpellCasting/Private/LiveSpellSessionSubsystem.cpp
- Modify: Plugins/LiveSpellCasting/Source/LiveSpellCasting/LiveSpellCasting.Build.cs
- Modify: Plugins/SpellPreview/Source/SpellPreview/Private/SpellPreviewSubsystem.cpp
- Modify: Plugins/InnerRealm/Source/InnerRealm/Private/InnerRealmSubsystem.cpp
- Delete: Plugins/LiveSpellCasting/Source/LiveSpellCasting/Public/LiveSpellRanges.h

**Interfaces:**
- Consumes: FSpellDefinition, FResolvedSpell, ESpellElement, ESpellShape, and SpellParameterRanges from Task 1.
- Produces: LiveSpellTypes.h with ELiveSpellParameter and ELiveSpellStage, plus FLiveSpellState with Reset(), SelectElement(), SelectShape(), SetParameterNormalized(), CanCast(), Resolve(), GetStage(), HasConstruction(), HasElement(), HasExplicitShape(), HasModifier(), IsParameterActive(), GetParameterNormalized(), GetResolvedShape(), and GetGeneration().
- Compatibility surface: ULiveSpellSessionSubsystem retains SelectEarth(), SelectShape(EEarthSpellShape), SetParameterNormalized(ELiveSpellParameter, float), and ResolveSpell() as adapters.

- [ ] **Step 1: Write failing grammar and speed-zero tests**

Create a test that follows the invalid sequence Empty -> shape -> modifier -> cast and asserts CanCast() remains false. Then select Earth, select Sphere, set Speed to 0.5, assert CanCast() is true, resolve, and assert SpeedMps is positive. Reset, repeat Earth + Sphere + Density only, resolve, and assert SpeedMps is exactly 0.0f.

~~~cpp
FLiveSpellState State;
const FSpellDefinition DefaultDefinition;
State.SelectShape(ESpellShape::Sphere);
State.SetParameterNormalized(ELiveSpellParameter::Speed, 0.5f);
TestFalse(TEXT("Invalid order cannot cast"), State.CanCast());

State.SelectElement(ESpellElement::Earth);
State.SelectShape(ESpellShape::Sphere);
State.SetParameterNormalized(ELiveSpellParameter::Density, 0.5f);
const FResolvedSpell SlowSpell = State.Resolve(DefaultDefinition);
TestEqual(TEXT("Unmodified speed stays zero"), SlowSpell.Definition.SpeedMps, 0.0f);
~~~

- [ ] **Step 2: Run the test to verify FLiveSpellState is unavailable**

First compile the new test source:

~~~powershell
& 'D:/UE_5.8/Engine/Build/BatchFiles/Build.bat' TESTUNREALPROJECTEditor Win64 Development '-Project=D:/TESTUNREALPROJECT/TESTUNREALPROJECT.uproject' -WaitMutex -NoHotReloadFromIDE
~~~

Expected: compilation fails because LiveSpellTypes.h and LiveSpellState.h are not present.

Then run:

~~~powershell
& 'D:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' 'D:/TESTUNREALPROJECT/TESTUNREALPROJECT.uproject' -unattended -nop4 -nullrhi '-ExecCmds=Automation RunTests AMADEUS.LiveSpell; Quit' '-TestExit=Automation Test Queue Empty'
~~~

Expected: after implementation, the named automation test is discovered and passes.

- [ ] **Step 3: Implement an engine-free state object and centralize ranges**

Move range constants and normalized interpolation functions into SpellParameterRanges.h in SpellCreation. Move the existing reflected ELiveSpellParameter and ELiveSpellStage definitions, with the same names and enumerator values, into LiveSpellTypes.h. Define the state object as plain C++ without UCLASS, UWorld, controller, input, widget, or subsystem state.

~~~cpp
class LIVESPELLCASTING_API FLiveSpellState
{
public:
    void Reset();
    void SelectElement(ESpellElement InElement);
    void SelectShape(ESpellShape InShape);
    void SetParameterNormalized(ELiveSpellParameter Parameter, float NormalizedValue);
    bool CanSelectShape() const;
    bool CanApplyModifier() const;
    bool CanCast() const;
    ELiveSpellStage GetStage() const;
    bool HasConstruction() const;
    bool HasElement() const;
    bool HasExplicitShape() const;
    bool HasModifier() const;
    bool IsParameterActive(ELiveSpellParameter Parameter) const;
    float GetParameterNormalized(ELiveSpellParameter Parameter) const;
    ESpellShape GetResolvedShape() const;
    FResolvedSpell Resolve(const FSpellDefinition& PersistentDefaults) const;
    uint32 GetGeneration() const { return Generation; }

private:
    ELiveSpellStage Stage = ELiveSpellStage::Empty;
    TOptional<ESpellElement> Element;
    TOptional<ESpellShape> Shape;
    TMap<ELiveSpellParameter, float> ParameterOverrides01;
    uint32 Generation = 0;
};
~~~

Selecting an element resets shape and overrides. Selecting a shape clears overrides. SetParameterNormalized clamps to [0, 1] and only operates after a shape has been chosen. Resolve applies only known parameter ranges, converts the completed FSpellDefinition with FSpellDefinitionAdapter::Resolve(), and forces SpeedMps to 0.0f unless ELiveSpellParameter::Speed has an override.

- [ ] **Step 4: Make the world subsystem a thin adapter and delete duplicate ranges**

Replace ULiveSpellSessionSubsystem state fields with FLiveSpellState State. Its existing Earth-shaped public functions convert EEarthSpellShape to ESpellShape and delegate. Make every existing query delegate to its matching State query, including stage, construction/element/shape/modifier gates, active normalized parameters, resolved shape, and generation. Add these generic non-Blueprint helpers for the new modules:

~~~cpp
void SelectElement(ESpellElement Element);
void SelectGenericShape(ESpellShape Shape);
FResolvedSpell ResolveGenericSpell() const;
~~~

Get persistent defaults from USpellCreationSubsystem::GetStoredGenericSpellDefinition(). Update SpellPreviewSubsystem.cpp and InnerRealmSubsystem.cpp in this task to include SpellParameterRanges.h and use the SpellParameterRanges namespace. Delete LiveSpellRanges.h only after rg confirms no include or symbol use remains anywhere in Plugins:

~~~powershell
rg -n "LiveSpellRanges" Plugins
~~~

Expected: no matches.

- [ ] **Step 5: Run tests, compile, and commit**

Run:

~~~powershell
& 'D:/UE_5.8/Engine/Build/BatchFiles/Build.bat' TESTUNREALPROJECTEditor Win64 Development '-Project=D:/TESTUNREALPROJECT/TESTUNREALPROJECT.uproject' -WaitMutex -NoHotReloadFromIDE
& 'D:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' 'D:/TESTUNREALPROJECT/TESTUNREALPROJECT.uproject' -unattended -nop4 -nullrhi '-ExecCmds=Automation RunTests AMADEUS.LiveSpell; Quit' '-TestExit=Automation Test Queue Empty'
git diff --check
git add Plugins/SpellCreation Plugins/LiveSpellCasting
git commit -m "refactor: extract live spell state"
~~~

Expected: all state-machine tests pass, including the SpeedMps zero rule.
