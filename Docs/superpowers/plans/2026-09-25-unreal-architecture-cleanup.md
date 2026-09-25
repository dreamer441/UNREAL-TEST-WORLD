# Unreal Spell Architecture Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Earth-specific runtime construction path with generic spell contracts and a small execution module, while preserving the current playable Earth workflow and consolidating project tooling and documentation.

**Architecture:** SpellCreation becomes the owner of generic authoring contracts and explicit legacy Earth adapters. LiveSpellCasting becomes a pure transient state machine, SpellExecution owns cast input, placement, and dispatch, and EarthMagic remains the Earth-only realization boundary. PlayerViewModes is reduced to view/input coordination; InnerRealm actively suspends view and execution behavior through public APIs so the plugin graph stays acyclic.

**Tech Stack:** Unreal Engine 5.8, C++20/Unreal Build Tool, Unreal Automation Tests, Python editor utilities, Windows batch scripting, Git/GitHub.

## Global Constraints

- Target Unreal Engine installation is D:/UE_5.8; the target is TESTUNREALPROJECTEditor Win64 Development.
- The project is Windows-only and must use only built-in Unreal Engine facilities and existing project modules; add no third-party plugin or library.
- Keep Core, MaterialCore, PhysicalBody, and ImpactSystem generic and lightweight; do not add gameplay casting, UI, ticking, debug drawing, or Earth-specific dependencies to them.
- Every cross-plugin include must use an exported Public header and every Build.cs dependency must be explicit; do not rely on transitive plugin loading.
- New gameplay logic belongs in focused modules. Do not introduce a global registry, reflective discovery, singleton service locator, or broad runtime scan.
- Preserve the live grammar exactly: Empty -> ElementSelected -> ShapeSelected -> ModifierActive -> Cast; SPACE is inert until the ModifierActive gate is met.
- Preserve the existing default Earth values, including Toughness 0.40, and keep live SpeedMps at 0 until a Speed modifier is explicitly activated.
- Preserve current Blueprints and serialized compatibility by retaining FEarthSpellDefinition, EEarthSpellShape, UEarthSpellMath, AEarthSpellBody::Configure(const FEarthSpellDefinition&), and existing Blueprint-callable subsystem entry points as deprecated adapters. Do not replace existing reflected FEarthSpellDefinition properties in place.
- Put any future safe name-only redirect in tracked Plugins/SpellCreation/Config/DefaultSpellCreation.ini, never in the ignored machine-local Config/DefaultEngine.ini. The current compatibility-adapter migration needs no active redirect because old reflected names remain.
- Keep runtime output quiet by default. Diagnostics must use normal Unreal logging and be useful only for failures; no per-tick logging or debug drawing.
- Do not modify Content assets or DefaultInput.ini. Keep the Space mapping and continue suppressing template jumping through PlayerViewModes at runtime.
- Keep Config/DefaultEngine.ini ignored because it contains machine-specific credentials; maintain only Config/DefaultEngine.template.ini in Git.
- Generated Binaries, Intermediate, DerivedDataCache, Saved, PluginBuild, IDE state, logs, archives, and Python caches remain ignored and are never staged.
- PlayerViewModes and SpellExecution suspension APIs use balanced reference counts so a nested caller cannot prematurely restore game input or casting.

---

## File Structure

| Path | Responsibility |
| --- | --- |
| Plugins/SpellCreation/Source/SpellCreation/Public/SpellDefinition.h | Generic reflected element, shape, authored-definition, resolved-definition, and explicit legacy conversion contracts. |
| Plugins/SpellCreation/Source/SpellCreation/Public/SpellShapeMath.h and Private/SpellShapeMath.cpp | Generic shape volume and size math used to derive physical body state. |
| Plugins/SpellCreation/Source/SpellCreation/Public/SpellParameterRanges.h | Shared normalized-value ranges formerly owned by LiveSpellCasting. |
| Plugins/LiveSpellCasting/Source/LiveSpellCasting/Public/LiveSpellTypes.h | Reflected live-stage and live-parameter types shared by the state object and world-subsystem adapter. |
| Plugins/LiveSpellCasting/Source/LiveSpellCasting/Public/LiveSpellState.h and Private/LiveSpellState.cpp | Plain-C++ transient casting grammar and override state, without world, controller, or UObject state. |
| Plugins/LiveSpellCasting/Source/LiveSpellCasting/Public/LiveSpellSessionSubsystem.h and Private/LiveSpellSessionSubsystem.cpp | Thin world-subsystem adapter around FLiveSpellState. |
| Plugins/SpellExecution/ | New production-only input, placement, cast result, and element dispatch module. |
| Plugins/EarthMagic/Source/EarthMagic/Public/EarthSpellSpawner.h and Private/EarthSpellSpawner.cpp | Earth realization adapter called only by SpellExecution. |
| Plugins/PlayerViewModes/Source/PlayerViewModes/Public/PlayerViewInputSuspensionState.h | Small non-UObject reference-counted suspension state used by PlayerViewModes and its automation test. |
| Plugins/PlayerViewModes/Source/PlayerViewModes/Public/PlayerViewModeSubsystem.h | Public realm-input suspension API with no InnerRealm or binding dependency. |
| Plugins/InnerRealm/Source/InnerRealm/ | UI/editor surface that drives public suspension APIs and uses generic spell data. |
| Content/Python/amadeus_tools.py and Content/Python/init_unreal.py | Retained active editor helpers with current descriptions and menu labels. |
| AMADEUS_DEV.bat | The sole supported launch, rebuild, clean, log-open, and log-collection entry point. |
| Docs/Architecture.md, Docs/GettingStarted.md, Docs/Archive/ | Small current documentation surface and clearly separated historical material. |

## Dependency Target

~~~text
SpellCreation -> MaterialCore, PhysicalBody
LiveSpellCasting -> SpellCreation
PlayerViewModes -> Engine only
SpellCastingBindings -> SpellCreation, LiveSpellCasting, PlayerViewModes
SpellPreview -> SpellCreation, LiveSpellCasting, PlayerViewModes, SpellExecution
EarthMagic -> SpellCreation, MaterialCore, PhysicalBody, ImpactSystem, EarthFoundation
SpellExecution -> SpellCreation, LiveSpellCasting, PlayerViewModes, EarthMagic
InnerRealm -> SpellCreation, LiveSpellCasting, SpellCastingBindings,
              PlayerViewModes, SpellExecution
~~~

The arrow means "depends on." In particular, PlayerViewModes must not depend on InnerRealm or SpellCastingBindings, which prevents the old cycle.

### Task 1: Introduce generic spell contracts with explicit Earth compatibility adapters

**Files:**
- Create: Plugins/SpellCreation/Source/SpellCreation/Public/SpellDefinition.h
- Create: Plugins/SpellCreation/Source/SpellCreation/Public/SpellShapeMath.h
- Create: Plugins/SpellCreation/Source/SpellCreation/Private/SpellShapeMath.cpp
- Create: Plugins/SpellCreation/Source/SpellCreation/Private/Tests/SpellDefinitionTests.cpp
- Create: Plugins/SpellCreation/Config/DefaultSpellCreation.ini
- Modify: Plugins/SpellCreation/Source/SpellCreation/SpellCreation.Build.cs
- Modify: Plugins/SpellCreation/Source/SpellCreation/Public/EarthSpellDefinition.h
- Modify: Plugins/SpellCreation/Source/SpellCreation/Public/EarthSpellMath.h
- Modify: Plugins/SpellCreation/Source/SpellCreation/Private/EarthSpellMath.cpp
- Modify: Plugins/SpellCreation/Source/SpellCreation/Public/SpellCreationSubsystem.h
- Modify: Plugins/SpellCreation/Source/SpellCreation/Private/SpellCreationSubsystem.cpp
- Modify: Plugins/SpellCreation/SpellCreation.uplugin

**Interfaces:**
- Consumes: FMaterialPhysicalProperties from MaterialCore and FPhysicalBodyState from PhysicalBody.
- Produces: ESpellElement, ESpellShape, FSpellShapeDefinition, FSpellDefinition, FResolvedSpell, FSpellDefinitionAdapter, FSpellShapeMath, and generic SpellCreation accessors.
- Compatibility surface: FEarthSpellDefinition, EEarthSpellShape, UEarthSpellMath, GetStoredSpellDefinition(), SetStoredSpellDefinition(), and ResetToDefaultEarthSpell() remain callable and delegate through FSpellDefinitionAdapter.

- [ ] **Step 1: Write the failing automation tests for conversion and physical derivation**

Create Plugins/SpellCreation/Source/SpellCreation/Private/Tests/SpellDefinitionTests.cpp with tests that construct a non-default FEarthSpellDefinition, convert it to FSpellDefinition, convert it back, and verify every mapped field. Add a second test that resolves a sphere with DensityKgPerM3 1600.0 and asserts that MassKg equals density times FSpellShapeMath::CalculateVolumeM3().

~~~cpp
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSpellDefinitionRoundTripTest,
    "AMADEUS.SpellCreation.LegacyRoundTrip",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSpellDefinitionRoundTripTest::RunTest(const FString&)
{
    FEarthSpellDefinition Legacy;
    Legacy.Shape = EEarthSpellShape::Cone;
    Legacy.ConeRadiusCm = 63.0f;
    Legacy.ConeHeightCm = 180.0f;
    Legacy.DistanceM = 7.5f;
    Legacy.SpeedMps = 0.0f;
    Legacy.DensityKgPerM3 = 1875.0f;
    Legacy.MassKg = 999.0f;
    Legacy.Hardness = 0.31f;
    Legacy.Toughness = 0.40f;
    Legacy.Elasticity = 0.12f;
    Legacy.Cohesion = 0.47f;
    Legacy.Rigidity = 0.66f;

    const FSpellDefinition Generic = FSpellDefinitionAdapter::FromLegacyEarth(Legacy);
    const FEarthSpellDefinition Restored = FSpellDefinitionAdapter::ToLegacyEarth(Generic);
    const FResolvedSpell Resolved = FSpellDefinitionAdapter::Resolve(Generic);
    TestEqual(TEXT("Element"), Generic.Element, ESpellElement::Earth);
    TestEqual(TEXT("Generic shape"), Generic.Shape, ESpellShape::Cone);
    TestEqual(TEXT("Generic cone radius"), Generic.ShapeDefinition.ConeRadiusCm, Legacy.ConeRadiusCm);
    TestEqual(TEXT("Generic cone height"), Generic.ShapeDefinition.ConeHeightCm, Legacy.ConeHeightCm);
    TestEqual(TEXT("Generic hardness"), Generic.Material.Hardness, Legacy.Hardness);
    TestEqual(TEXT("Generic toughness"), Generic.Material.Toughness, Legacy.Toughness);
    TestEqual(TEXT("Generic restitution"), Generic.Material.Restitution, Legacy.Elasticity);
    TestEqual(TEXT("Generic cohesion"), Generic.Material.Cohesion, Legacy.Cohesion);
    TestEqual(TEXT("Generic rigidity"), Generic.Material.Rigidity, Legacy.Rigidity);
    TestEqual(TEXT("Shape"), Restored.Shape, Legacy.Shape);
    TestEqual(TEXT("Cone radius"), Restored.ConeRadiusCm, Legacy.ConeRadiusCm);
    TestEqual(TEXT("Cone height"), Restored.ConeHeightCm, Legacy.ConeHeightCm);
    TestEqual(TEXT("Distance"), Restored.DistanceM, Legacy.DistanceM);
    TestEqual(TEXT("Speed"), Restored.SpeedMps, Legacy.SpeedMps);
    TestEqual(TEXT("Density"), Restored.DensityKgPerM3, Legacy.DensityKgPerM3);
    TestEqual(TEXT("Hardness"), Restored.Hardness, Legacy.Hardness);
    TestEqual(TEXT("Toughness"), Restored.Toughness, Legacy.Toughness);
    TestEqual(TEXT("Elasticity"), Restored.Elasticity, Legacy.Elasticity);
    TestEqual(TEXT("Cohesion"), Restored.Cohesion, Legacy.Cohesion);
    TestEqual(TEXT("Rigidity"), Restored.Rigidity, Legacy.Rigidity);
    TestTrue(TEXT("Mass is derived rather than restored"),
        !FMath::IsNearlyEqual(Resolved.Body.MassKg, Legacy.MassKg));
    TestEqual(TEXT("Resolved material copied"), Resolved.Body.Material.Toughness,
        Generic.Material.Toughness);
    return true;
}
~~~

- [ ] **Step 2: Run the new test target to verify the symbols are absent**

First compile the new test source:

~~~powershell
& 'D:/UE_5.8/Engine/Build/BatchFiles/Build.bat' TESTUNREALPROJECTEditor Win64 Development '-Project=D:/TESTUNREALPROJECT/TESTUNREALPROJECT.uproject' -WaitMutex -NoHotReloadFromIDE
~~~

Expected: compilation fails because FSpellDefinitionAdapter and FSpellShapeMath do not exist yet.

Then run:

~~~powershell
& 'D:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' 'D:/TESTUNREALPROJECT/TESTUNREALPROJECT.uproject' -unattended -nop4 -nullrhi '-ExecCmds=Automation RunTests AMADEUS.SpellCreation.LegacyRoundTrip; Quit' '-TestExit=Automation Test Queue Empty'
~~~

Expected: after implementation, the named automation test is discovered and passes.

- [ ] **Step 3: Add generic reflected contracts, math, and adapters**

Define the generic public surface in SpellDefinition.h. Keep units aligned with the existing Earth contract: shape dimensions are centimeters, distance is meters, and speed is meters per second.

~~~cpp
UENUM(BlueprintType)
enum class ESpellElement : uint8 { Earth };

UENUM(BlueprintType)
enum class ESpellShape : uint8 { Sphere, Cube, Cone };

USTRUCT(BlueprintType)
struct SPELLCREATION_API FSpellShapeDefinition
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Shape") float SphereRadiusCm = 22.0f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Shape") float CubeXcm = 100.0f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Shape") float CubeYcm = 100.0f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Shape") float CubeZcm = 100.0f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Shape") float ConeRadiusCm = 40.0f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell|Shape") float ConeHeightCm = 120.0f;
};

USTRUCT(BlueprintType)
struct SPELLCREATION_API FSpellDefinition
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell") ESpellElement Element = ESpellElement::Earth;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell") ESpellShape Shape = ESpellShape::Sphere;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell") FSpellShapeDefinition ShapeDefinition;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell") FMaterialPhysicalProperties Material;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell") float DistanceM = 3.0f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spell") float SpeedMps = 30.0f;
};

USTRUCT(BlueprintType)
struct SPELLCREATION_API FResolvedSpell
{
    GENERATED_BODY()
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Spell") FSpellDefinition Definition;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Spell") FPhysicalBodyState Body;
};

struct SPELLCREATION_API FSpellDefinitionAdapter
{
    static FSpellDefinition FromLegacyEarth(const FEarthSpellDefinition& Legacy);
    static FEarthSpellDefinition ToLegacyEarth(const FSpellDefinition& Definition);
    static FResolvedSpell Resolve(const FSpellDefinition& Definition);
};

struct SPELLCREATION_API FSpellShapeMath
{
    static float CalculateVolumeM3(const FSpellDefinition& Definition);
    static float CalculateDensityKgPerM3(const FSpellDefinition& Definition);
    static float CalculateMassKg(const FSpellDefinition& Definition);
    static float CalculateContactRadiusCm(const FSpellDefinition& Definition);
    static FVector CalculateHalfExtentsCm(const FSpellDefinition& Definition);
};
~~~

Map Legacy.DensityKgPerM3, Hardness, Toughness, Elasticity, Cohesion, and Rigidity to Material.DensityKgPerM3, Hardness, Toughness, Restitution, Cohesion, and Rigidity respectively. Initialize generic Material.Toughness to 0.40f explicitly. Resolution copies the normalized generic material into FResolvedSpell.Body.Material, derives Body.VolumeM3 with the existing sphere/cube/cone formulae, derives Body.ContactRadiusCm and half extents with the existing minimum dimensions, and sets Body.MassKg to max(density times volume, 0.01). Resolution leaves Body.VelocityCmS at zero and Body.bAffectedByGravity true; SpellExecution supplies directional launch from Definition.SpeedMps. Do not retain legacy MassKg as authored state.

Keep FEarthSpellDefinition and EEarthSpellShape in EarthSpellDefinition.h, mark their comments Deprecated, and leave their properties intact. Implement all five UEarthSpellMath Blueprint wrappers as deprecated adapters that convert to FSpellDefinition and call the identically purposed FSpellShapeMath method. Add DefaultSpellCreation.ini with the explanatory comment that no active structural redirects are safe while the legacy reflected types are retained.

- [ ] **Step 4: Convert SpellCreation storage while preserving its old Blueprint API**

Retain the existing reflected UPROPERTY named StoredSpell with type FEarthSpellDefinition as a synchronized deprecated compatibility shadow. Add a second UPROPERTY named StoredGenericSpell with type FSpellDefinition as the canonical value. Every legacy or generic setter updates both values through FSpellDefinitionAdapter, so existing reflected storage is never retyped in place. Add generic accessors with distinct names and implement old functions as adapters.

~~~cpp
UFUNCTION(BlueprintPure, Category="Spell Creation")
FSpellDefinition GetStoredGenericSpellDefinition() const { return StoredGenericSpell; }

UFUNCTION(BlueprintCallable, Category="Spell Creation")
void SetStoredGenericSpellDefinition(const FSpellDefinition& NewSpell);

UFUNCTION(BlueprintPure, Category="Spell Creation")
FEarthSpellDefinition GetStoredSpellDefinition() const
{
    return StoredSpell;
}

UFUNCTION(BlueprintCallable, Category="Spell Creation")
void SetStoredSpellDefinition(const FEarthSpellDefinition& NewSpell)
{
    SetStoredGenericSpellDefinition(FSpellDefinitionAdapter::FromLegacyEarth(NewSpell));
}
~~~

Add MaterialCore and PhysicalBody to SpellCreation.Build.cs PublicDependencyModuleNames, add them to SpellCreation.uplugin Plugins, and include only their Public headers. Normalize finite, non-negative dimensions, distance, speed, and physical properties before resolving mass.

- [ ] **Step 5: Run tests, compile, and commit the isolated contract change**

Run:

~~~powershell
& 'D:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' 'D:/TESTUNREALPROJECT/TESTUNREALPROJECT.uproject' -unattended -nop4 -nullrhi '-ExecCmds=Automation RunTests AMADEUS.SpellCreation; Quit' '-TestExit=Automation Test Queue Empty'
git diff --check
git add Plugins/SpellCreation
git commit -m "feat: add generic spell definition contracts"
~~~

Expected: automation tests pass and git diff --check prints no whitespace errors.

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

### Task 3: Create SpellExecution and move the production SPACE cast path

**Files:**
- Create: Plugins/SpellExecution/SpellExecution.uplugin
- Create: Plugins/SpellExecution/Source/SpellExecution/SpellExecution.Build.cs
- Create: Plugins/SpellExecution/Source/SpellExecution/Public/SpellExecutionSubsystem.h
- Create: Plugins/SpellExecution/Source/SpellExecution/Public/SpellCastPlacement.h
- Create: Plugins/SpellExecution/Source/SpellExecution/Private/SpellExecutionModule.cpp
- Create: Plugins/SpellExecution/Source/SpellExecution/Private/SpellExecutionSubsystem.cpp
- Create: Plugins/SpellExecution/Source/SpellExecution/Private/SpellCastPlacement.cpp
- Create: Plugins/SpellExecution/Source/SpellExecution/Private/Tests/SpellExecutionTests.cpp
- Create: Plugins/EarthMagic/Source/EarthMagic/Public/EarthSpellSpawner.h
- Create: Plugins/EarthMagic/Source/EarthMagic/Private/EarthSpellSpawner.cpp
- Modify: Plugins/EarthMagic/Source/EarthMagic/Public/EarthSpellBody.h
- Modify: Plugins/EarthMagic/Source/EarthMagic/Private/EarthSpellBody.cpp
- Modify: Plugins/EarthMagic/Source/EarthMagic/Public/EarthSpellShapeBuilder.h
- Modify: Plugins/EarthMagic/Source/EarthMagic/Private/EarthSpellShapeBuilder.cpp
- Modify: Plugins/EarthMagic/Source/EarthMagic/Public/EarthSpellDamageGeometry.h
- Modify: Plugins/EarthMagic/Source/EarthMagic/Private/EarthSpellDamageGeometry.cpp
- Modify: Plugins/EarthMagic/EarthMagic.uplugin
- Modify: Plugins/EarthMagic/Source/EarthMagic/EarthMagic.Build.cs
- Modify: Plugins/SpellPreview/Source/SpellPreview/Private/SpellPreviewSubsystem.cpp
- Modify: Plugins/SpellPreview/SpellPreview.uplugin
- Modify: Plugins/SpellPreview/Source/SpellPreview/SpellPreview.Build.cs
- Modify: TESTUNREALPROJECT.uproject
- Delete: Plugins/LiveSpellCasting/Source/LiveSpellCasting/Public/SpellCastPlacement.h
- Delete: Plugins/LiveSpellCasting/Source/LiveSpellCasting/Private/SpellCastPlacement.cpp
- Delete: Plugins/EarthTestHarness/EarthTestHarness.uplugin
- Delete: Plugins/EarthTestHarness/Source/EarthTestHarness/EarthTestHarness.Build.cs
- Delete: Plugins/EarthTestHarness/Source/EarthTestHarness/Public/EarthTestInputSubsystem.h
- Delete: Plugins/EarthTestHarness/Source/EarthTestHarness/Private/EarthTestHarnessModule.cpp
- Delete: Plugins/EarthTestHarness/Source/EarthTestHarness/Private/EarthTestInputSubsystem.cpp

**Interfaces:**
- Consumes: ULiveSpellSessionSubsystem::CanCast(), ResolveGenericSpell(), UPlayerViewModeSubsystem::GetTopDownCastRay(), FSpellCastPlacement, and FEarthSpellSpawner.
- Produces: USpellExecutionSubsystem::SetExecutionSuspended(bool), ExecuteLiveSpell(), FSpellExecutionResult, and the relocated placement contract.
- Ownership rule: SpellExecution chooses the explicit Earth route; EarthMagic owns the Earth actor spawn/configure/launch implementation.

- [ ] **Step 1: Write a failing test for execution-result guards**

Define an enum with NoWorld, NoController, NoLiveConstruction, PlacementFailed, UnsupportedElement, SpawnFailed, and Executed. Add an automation integration test with a test world whose live session has not reached ModifierActive: record its generation, invoke ExecuteLiveSpell(), then assert NoLiveConstruction, unchanged generation, and no AEarthSpellBody actor. This proves the guard does not consume construction or spawn an actor.

~~~cpp
FSpellExecutionResult Result =
    FSpellExecutionResult::ForOutcome(ESpellExecutionOutcome::NoLiveConstruction);
TestEqual(TEXT("No live construction is reported"),
    Result.Outcome, ESpellExecutionOutcome::NoLiveConstruction);
TestFalse(TEXT("No actor was spawned"), Result.bConsumedConstruction);
~~~

- [ ] **Step 2: Run the test to verify the module and result type do not exist**

First compile the new test source:

~~~powershell
& 'D:/UE_5.8/Engine/Build/BatchFiles/Build.bat' TESTUNREALPROJECTEditor Win64 Development '-Project=D:/TESTUNREALPROJECT/TESTUNREALPROJECT.uproject' -WaitMutex -NoHotReloadFromIDE
~~~

Expected: compilation fails because SpellExecution and FSpellExecutionResult have not been created.

Then run:

~~~powershell
& 'D:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' 'D:/TESTUNREALPROJECT/TESTUNREALPROJECT.uproject' -unattended -nop4 -nullrhi '-ExecCmds=Automation RunTests AMADEUS.SpellExecution; Quit' '-TestExit=Automation Test Queue Empty'
~~~

Expected: after implementation, the named automation test is discovered and passes.

- [ ] **Step 3: Add the focused plugin, generic placement, and explicit Earth dispatch**

Create the plugin with direct Core, CoreUObject, Engine, InputCore, SpellCreation, LiveSpellCasting, PlayerViewModes, and EarthMagic dependencies in Build.cs. Its .uplugin descriptor lists only the project plugins SpellCreation, LiveSpellCasting, PlayerViewModes, and EarthMagic. Move FSpellCastPlacement and FResolvedSpellCastPlacement unchanged from LiveSpellCasting, except its Resolve signature now receives FResolvedSpell and reads Spell.Definition.

~~~cpp
UENUM()
enum class ESpellExecutionOutcome : uint8
{
    NoWorld, NoController, ExecutionSuspended, NoLiveConstruction,
    PlacementFailed, UnsupportedElement, SpawnFailed, Executed
};

struct SPELLEXECUTION_API FSpellExecutionResult
{
    ESpellExecutionOutcome Outcome = ESpellExecutionOutcome::NoWorld;
    bool bConsumedConstruction = false;
    static FSpellExecutionResult ForOutcome(
        ESpellExecutionOutcome InOutcome,
        bool bInConsumedConstruction = false)
    {
        return { InOutcome, bInConsumedConstruction };
    }
};

UCLASS()
class SPELLEXECUTION_API USpellExecutionSubsystem : public UTickableWorldSubsystem
{
    GENERATED_BODY()
public:
    virtual void Tick(float DeltaSeconds) override;
    virtual TStatId GetStatId() const override;
    void SetExecutionSuspended(bool bInSuspended);
    bool IsExecutionSuspended() const { return ExecutionSuspensionDepth > 0; }
    FSpellExecutionResult ExecuteLiveSpell();
private:
    int32 ExecutionSuspensionDepth = 0;
};
~~~

SetExecutionSuspended(true) increments the depth and false decrements it only when positive. Both Tick and ExecuteLiveSpell immediately return ExecutionSuspended while IsExecutionSuspended() is true. Tick then checks IsGameWorld(), obtains the first player controller, and reacts to WasInputKeyJustPressed(EKeys::SpaceBar). ExecuteLiveSpell preserves all remaining guards, derives camera aim with the PlayerView top-down override, resolves placement, and calls a direct switch on Resolved.Definition.Element. The Earth branch passes the three primitive placement values to FEarthSpellSpawner::SpawnAndLaunch; no registry or discovery mechanism is introduced.

- [ ] **Step 4: Move Earth realization behind a dedicated spawner and update consumers**

Define the Earth-only API:

~~~cpp
struct EARTHMAGIC_API FEarthSpellSpawner
{
    static AEarthSpellBody* SpawnAndLaunch(
        UWorld* World,
        APlayerController* Controller,
        const FResolvedSpell& Spell,
        const FVector& SpawnLocation,
        const FRotator& SpawnRotation,
        const FVector& LaunchDirection);
};
~~~

Put FActorSpawnParameters, AdjustIfPossibleButAlwaysSpawn, AEarthSpellBody::ConfigureResolvedSpell(), and Launch() inside that function. EarthMagic receives only SpellCreation contracts and Engine value types; it must not include SpellExecution or LiveSpellCasting. Keep AEarthSpellBody::Configure(const FEarthSpellDefinition&) BlueprintCallable and retain its reflected FEarthSpellDefinition Spell property unchanged as the serialized compatibility surface. Add a distinctly named generic ConfigureResolvedSpell(const FResolvedSpell&) method which updates transient generic runtime state; Configure maps its legacy input and delegates. Change FEarthSpellShapeBuilder and FEarthSpellDamageGeometry to accept generic shape/resolved data while retaining their Earth-specific names. Only reset the live session after FEarthSpellSpawner returns a non-null actor. Change SpellPreview to include the new public SpellCastPlacement.h and consume FResolvedSpell.Definition.Shape and Definition.Material.DensityKgPerM3. Remove the old placement files from LiveSpellCasting after all references move.

In the same atomic cutover, add explicit Enabled true entries for LiveSpellCasting, SpellPreview, and SpellExecution to TESTUNREALPROJECT.uproject, remove EarthTestHarness from it, and delete the listed harness descriptor and sources. This guarantees there is one active SPACE executor after the build; do not leave the old harness loaded beside SpellExecution.

- [ ] **Step 5: Test, compile, and commit the executable path**

Run:

~~~powershell
rg -n "SpellCastPlacement" Plugins
& 'D:/UE_5.8/Engine/Build/BatchFiles/Build.bat' TESTUNREALPROJECTEditor Win64 Development '-Project=D:/TESTUNREALPROJECT/TESTUNREALPROJECT.uproject' -WaitMutex -NoHotReloadFromIDE
& 'D:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' 'D:/TESTUNREALPROJECT/TESTUNREALPROJECT.uproject' -unattended -nop4 -nullrhi '-ExecCmds=Automation RunTests AMADEUS.SpellExecution; Quit' '-TestExit=Automation Test Queue Empty'
rg -n "EarthTestHarness|UEarthTestInputSubsystem|EarthTestInputSubsystem" TESTUNREALPROJECT.uproject Plugins
git diff --check
git add TESTUNREALPROJECT.uproject Plugins/SpellExecution Plugins/EarthMagic Plugins/SpellPreview Plugins/LiveSpellCasting
git add -u -- Plugins/EarthTestHarness
git commit -m "feat: add generic spell execution"
~~~

Expected: the only FSpellCastPlacement declaration is in SpellExecution, the final harness search has no matches, tests pass, and the old production casting behavior is preserved.

### Task 4: Invert player-view ownership and migrate binding and realm callers

**Files:**
- Modify: Plugins/PlayerViewModes/Source/PlayerViewModes/PlayerViewModes.Build.cs
- Modify: Plugins/PlayerViewModes/PlayerViewModes.uplugin
- Modify: Plugins/PlayerViewModes/Source/PlayerViewModes/Public/PlayerViewModeSubsystem.h
- Modify: Plugins/PlayerViewModes/Source/PlayerViewModes/Private/PlayerViewModeSubsystem.cpp
- Modify: Plugins/SpellCastingBindings/Source/SpellCastingBindings/SpellCastingBindings.Build.cs
- Modify: Plugins/SpellCastingBindings/SpellCastingBindings.uplugin
- Modify: Plugins/SpellCastingBindings/Source/SpellCastingBindings/Public/SpellCastingBindingSubsystem.h
- Modify: Plugins/SpellCastingBindings/Source/SpellCastingBindings/Private/SpellCastingBindingSubsystem.cpp
- Modify: Plugins/InnerRealm/Source/InnerRealm/InnerRealm.Build.cs
- Modify: Plugins/InnerRealm/InnerRealm.uplugin
- Modify: Plugins/InnerRealm/Source/InnerRealm/Public/InnerRealmSubsystem.h
- Modify: Plugins/InnerRealm/Source/InnerRealm/Private/InnerRealmSubsystem.cpp
- Create: Plugins/PlayerViewModes/Source/PlayerViewModes/Public/PlayerViewInputSuspensionState.h
- Create: Plugins/PlayerViewModes/Source/PlayerViewModes/Private/Tests/PlayerViewModeTests.cpp

**Interfaces:**
- Consumes: UPlayerViewModeSubsystem::IsTopDown() and SetOuterWorldInputSuspended(bool) from PlayerViewModes.
- Produces: PlayerViewModes with no includes or dependencies on InnerRealm or SpellCastingBindings; InnerRealm calls both PlayerViewModes and SpellExecution suspension APIs.

- [ ] **Step 1: Write a failing public-API test for nested realm suspension**

Test FPlayerViewInputSuspensionState directly: calling SetSuspended(true) twice leaves it suspended, then calling false twice restores it only after the second release. The subsystem test uses that state to assert it acquires and releases its engine input lock only on the two outer transitions.

~~~cpp
FPlayerViewInputSuspensionState State;
State.SetSuspended(true);
State.SetSuspended(true);
TestTrue(TEXT("Nested suspension remains active"), State.IsSuspended());
State.SetSuspended(false);
TestTrue(TEXT("First release preserves nested suspension"), State.IsSuspended());
State.SetSuspended(false);
TestFalse(TEXT("Second release restores"), State.IsSuspended());
~~~

- [ ] **Step 2: Run the test to verify the API is absent**

Run:

~~~powershell
& 'D:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' 'D:/TESTUNREALPROJECT/TESTUNREALPROJECT.uproject' -unattended -nop4 -nullrhi '-ExecCmds=Automation RunTests AMADEUS.PlayerView; Quit' '-TestExit=Automation Test Queue Empty'
~~~

Expected: compilation fails because FPlayerViewInputSuspensionState and SetOuterWorldInputSuspended are absent.

- [ ] **Step 3: Make PlayerViewModes independent and expose the realm-facing input API**

Remove InnerRealmSubsystem.h and SpellCastingBindingSubsystem.h includes, all GetSubsystem calls for those modules, their Build.cs dependencies, and their .uplugin dependencies before adding the reversed edges in SpellCastingBindings and InnerRealm. This order prevents an intermediate UBT cycle. Add a reference-counted public API so nested callers cannot incorrectly release each other's engine input lock:

~~~cpp
struct PLAYERVIEWMODES_API FPlayerViewInputSuspensionState
{
    void SetSuspended(bool bSuspended)
    {
        Depth = bSuspended ? Depth + 1 : FMath::Max(0, Depth - 1);
    }
    bool IsSuspended() const { return Depth > 0; }
private:
    int32 Depth = 0;
};

UFUNCTION(BlueprintCallable, Category="Player View")
void SetOuterWorldInputSuspended(bool bSuspended);

UFUNCTION(BlueprintPure, Category="Player View")
bool IsOuterWorldInputSuspended() const;
~~~

The implementation increments a private counter on true and decrements only when positive on false. On the 0-to-1 transition, preserve the existing PlayerView input/camera state and acquire its engine locks. On the 1-to-0 transition, restore state and release only its own locks. While suspended, Tick does not switch or process outer-world controls.

- [ ] **Step 4: Update bindings and InnerRealm to the new dependency directions**

Add PlayerViewModes as a direct public dependency of SpellCastingBindings. Replace direct top-down input ownership with a read of UPlayerViewModeSubsystem::IsTopDown(), while retaining its existing binding map and hold behavior. Make shape actions call ULiveSpellSessionSubsystem::SelectGenericShape(ESpellShape::Sphere/Cube/Cone).

Add PlayerViewModes and SpellExecution direct dependencies to InnerRealm. Add private bOwnsPlayerViewSuspension and bOwnsExecutionSuspension flags, both initialized false. When TAB opens the realm, call the APIs only when their matching flag is false, then set that flag true:

~~~cpp
Views->SetOuterWorldInputSuspended(true);
Executor->SetExecutionSuspended(true);
~~~

When TAB closes or the subsystem deinitializes, call each false API only when its matching ownership flag is true, then clear the flag. This makes close followed by deinitialization release each reference exactly once. Convert InnerRealm's selector, dimension, summary, and material UI branches from EEarthSpellShape and FEarthSpellDefinition field access to ESpellShape and FSpellDefinition fields. Keep the visible labels and control behavior unchanged.

- [ ] **Step 5: Test the graph, compile, and commit**

Run:

~~~powershell
rg -n "InnerRealmSubsystem|SpellCastingBindingSubsystem" Plugins/PlayerViewModes
& 'D:/UE_5.8/Engine/Build/BatchFiles/Build.bat' TESTUNREALPROJECTEditor Win64 Development '-Project=D:/TESTUNREALPROJECT/TESTUNREALPROJECT.uproject' -WaitMutex -NoHotReloadFromIDE
& 'D:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' 'D:/TESTUNREALPROJECT/TESTUNREALPROJECT.uproject' -unattended -nop4 -nullrhi '-ExecCmds=Automation RunTests AMADEUS.PlayerView+AMADEUS.LiveSpell; Quit' '-TestExit=Automation Test Queue Empty'
git diff --check
git add Plugins/PlayerViewModes Plugins/SpellCastingBindings Plugins/InnerRealm
git commit -m "refactor: decouple player view from spell UI"
~~~

Expected: rg returns no PlayerViewModes dependency on InnerRealm or bindings, and the updated automation suites pass.

### Task 5: Verify the production module graph and refresh active editor utilities

**Files:**
- Modify: Plugins/LiveSpellCasting/LiveSpellCasting.uplugin
- Modify: Plugins/SpellPreview/SpellPreview.uplugin
- Modify: Content/Python/amadeus_tools.py
- Modify: Content/Python/init_unreal.py

**Interfaces:**
- Consumes: the complete SpellExecution runtime path from Task 3.
- Produces: verified explicit production dependencies and retained, accurately described active AMADEUS editor helpers.

- [ ] **Step 1: Audit the completed atomic executor cutover**

Run these reference searches:

~~~powershell
rg -n "EarthTestHarness|UEarthTestInputSubsystem|EarthTestInputSubsystem" TESTUNREALPROJECT.uproject Plugins Content Config Docs
rg -n "LiveSpellCasting|SpellPreview|SpellExecution" TESTUNREALPROJECT.uproject
~~~

Expected: the first command has no matches; the second command shows all three explicitly enabled production plugins.

- [ ] **Step 2: Verify direct descriptor dependencies**

Check every direct source-module include introduced in Tasks 1 through 4 has a matching Build.cs and .uplugin dependency. In particular, SpellPreview declares SpellExecution and SpellCreation, LiveSpellCasting declares SpellCreation, and no descriptor refers to EarthTestHarness. Do not disable EarthFoundation, MaterialCore, PhysicalBody, ImpactSystem, EarthMagic, PlayerViewModes, SpellCastingBindings, SpellCreation, or InnerRealm.

- [ ] **Step 3: Keep active editor utilities and correct their descriptions**

Retain the AMADEUS editor menu registration and the selected Earth block helper in Content/Python. Remove the unregistered legacy dent helper only if its function name has no remaining menu reference. Replace stale user-facing strings about E/F1 controls, mass controls, and old vertex-dent behavior with descriptions of the current selected-block material and impact helpers. Preserve the /Script/EarthFoundation.EarthBlockActor reference.

- [ ] **Step 4: Rebuild and commit the graph verification and utility cleanup**

Run:

~~~powershell
& 'D:/UE_5.8/Engine/Build/BatchFiles/Build.bat' TESTUNREALPROJECTEditor Win64 Development '-Project=D:/TESTUNREALPROJECT/TESTUNREALPROJECT.uproject' -WaitMutex -NoHotReloadFromIDE
rg -n "EarthTestHarness|UEarthTestInputSubsystem|EarthTestInputSubsystem" TESTUNREALPROJECT.uproject Plugins Content Config Docs
git diff --check
git add Plugins/LiveSpellCasting/LiveSpellCasting.uplugin Plugins/SpellPreview/SpellPreview.uplugin Content/Python
git commit -m "chore: verify production module graph"
~~~

Expected: the build succeeds and the final rg command produces no matches.

### Task 6: Consolidate developer tooling and documentation without losing history

**Files:**
- Create: AMADEUS_DEV.bat
- Create: Docs/Architecture.md
- Create: Docs/GettingStarted.md
- Create: Docs/Archive/Architecture/
- Create: Docs/Archive/Changelog/
- Create: Docs/Archive/Migrations/
- Modify: .gitignore
- Move: root ARCHITECTURE_*.md and EARTH_COLLISIONS_V0_8_2.md and IMPACT_CALCULATION_V0_5.md to Docs/Archive/Architecture/
- Move: root CHANGELOG_V0_*.md and CHANGELOG_V0_*.txt to Docs/Archive/Changelog/
- Move: root FIX_V0_4_1.txt, FIX_V0_5_1.txt, FIX_V0_7_3.txt, INSTALL_EARTH_V0_1.txt, INSTALL_EARTH_V0_2.txt, INSTALL_MATERIAL_INTERACTION_V0_3.txt, INSTALL_MATERIAL_INTERACTION_V0_3_1.txt, INSTALL_README.txt, INSTALL_V0_4.txt, README.txt, and README_FIX.txt to Docs/Archive/Migrations/
- Delete: root COLLECT_V0_5_BUILD_LOG.bat, COLLECT_V0_7_BUILD_LOG.bat, FORCE_REBUILD_EARTH_v031.bat, MIGRATE_AND_REBUILD_V0_4.bat, PATCH_AMADEUS_RUNTIME_INCLUDE.bat, PATCH_AMADEUS_RUNTIME_SLATE_INCLUDE.bat, REBUILD_V0_4_1.bat, REBUILD_V0_4_2.bat, REBUILD_V0_4_3.bat, REBUILD_V0_5.bat, REBUILD_V0_5_1.bat, REBUILD_V0_6.bat, REBUILD_V0_7.bat, REBUILD_V0_7_2.bat, REBUILD_V0_7_3.bat, REBUILD_V0_7_FIXED.bat, REBUILD_V0_8.bat, REBUILD_V0_8_1.bat, REBUILD_V0_8_2.bat, REBUILD_V0_9.bat, REBUILD_V0_9_1.bat, REBUILD_V0_9_2.bat, REBUILD_V0_10.bat, REBUILD_V0_11.bat, REBUILD_V0_11_1.bat, REBUILD_V0_12.bat, REBUILD_V0_12_1.bat, REBUILD_V0_12_2.bat, REBUILD_V0_12_2_1.bat, and REBUILD_V0_12_2_2.bat
- Delete: ignored root Config.zip, V0_5_BUILD_LOG.txt, V0_7_BUILD_LOG.txt, assign, old, return, size, speed, and top-down

**Interfaces:**
- Consumes: project root path and D:/UE_5.8 only.
- Produces: one stable command-line and interactive development entry point; compact current docs and preserved, non-active history.

- [ ] **Step 1: Write an argument-validation smoke test for the new batch entry point**

From a command prompt, run AMADEUS_DEV.bat help and an unknown argument. Verify help lists launch, rebuild, clean-plugins, full-clean, open-log, collect-log, and help. Verify an unknown argument exits nonzero without deleting files.

~~~powershell
cmd /c D:/TESTUNREALPROJECT/AMADEUS_DEV.bat help
cmd /c D:/TESTUNREALPROJECT/AMADEUS_DEV.bat not-a-command
~~~

Expected: help exits 0; not-a-command exits nonzero and prints the same command list.

- [ ] **Step 2: Implement the rooted, safe batch command dispatcher**

Set ROOT from %~dp0 and UPROJECT to %ROOT%TESTUNREALPROJECT.uproject. Validate that UPROJECT, D:/UE_5.8/Engine/Build/BatchFiles/Build.bat, and D:/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe exist before running an engine operation. Implement:

~~~text
launch         start UnrealEditor.exe with the project
rebuild        remove root Binaries/Intermediate and each plugin Binaries/Intermediate,
               then call Build.bat TESTUNREALPROJECTEditor Win64 Development
clean-plugins  remove only Plugins/*/Binaries and Plugins/*/Intermediate
full-clean     ask for an explicit Y confirmation, then additionally remove root
               Binaries, Intermediate, DerivedDataCache, PluginBuild, Saved, and .vs
open-log       open the most recent UnrealBuildTool log when it exists
collect-log    copy the most recent UnrealBuildTool log to ignored BuildLogs/UnrealBuildTool-Log.txt
help           print usage
no arguments   show a numbered interactive menu that dispatches the same commands
~~~

Full-clean must never target Content, Config, Source, TESTUNREALPROJECT.uproject, Docs, or .git. Use built-in Windows commands only; do not invoke a system dotnet installation.

- [ ] **Step 3: Write current architecture and getting-started documents**

Docs/Architecture.md must describe the approved dependency target, generic-versus-Earth responsibilities, compatibility adapter rationale, data flow from input to execution, and the no-private-header rule. Docs/GettingStarted.md must show the three safe day-to-day commands:

~~~text
AMADEUS_DEV.bat launch
AMADEUS_DEV.bat rebuild
AMADEUS_DEV.bat collect-log
~~~

It must also state that DefaultEngine.template.ini is the shareable configuration starting point and DefaultEngine.ini stays local.

- [ ] **Step 4: Archive historical documents and delete superseded launchers and junk**

Move these architecture files into Docs/Archive/Architecture/: ARCHITECTURE_CASTING_HIERARCHY_V0_12_1.md, ARCHITECTURE_EARTH_V0_1.md, ARCHITECTURE_EARTH_V0_2.md, ARCHITECTURE_FOUNDATION_V0_4.md, ARCHITECTURE_FOUNDATION_V0_4_2.md, ARCHITECTURE_FOUNDATION_V0_4_3.md, ARCHITECTURE_GAMEPLAY_V0_7.md, ARCHITECTURE_GAMEPLAY_V0_8.md, ARCHITECTURE_INNER_DIMENSION_V0_6.md, ARCHITECTURE_LIVE_CASTING_V0_12.md, ARCHITECTURE_MATERIAL_INTERACTION_V0_3.md, ARCHITECTURE_MATERIAL_INTERACTION_V0_3_1.md, ARCHITECTURE_PLAYER_MOVEMENT_V0_9.md, ARCHITECTURE_SPELL_CASTING_V0_10.md, ARCHITECTURE_SPELL_CASTING_V0_11.md, EARTH_COLLISIONS_V0_8_2.md, and IMPACT_CALCULATION_V0_5.md.

Move these changelogs into Docs/Archive/Changelog/: CHANGELOG_V0_4_2.txt, CHANGELOG_V0_4_3.txt, CHANGELOG_V0_5.txt, CHANGELOG_V0_6.txt, CHANGELOG_V0_7.txt, CHANGELOG_V0_8.txt, CHANGELOG_V0_8_1.txt, CHANGELOG_V0_9.txt, CHANGELOG_V0_9_1.md, CHANGELOG_V0_9_2.md, CHANGELOG_V0_11.md, CHANGELOG_V0_11_1.md, CHANGELOG_V0_12.md, CHANGELOG_V0_12_1.md, CHANGELOG_V0_12_2.md, CHANGELOG_V0_12_2_1.md, and CHANGELOG_V0_12_2_2.md.

Move the already enumerated migration/install files into Docs/Archive/Migrations/. Verify every listed old BAT file is superseded by AMADEUS_DEV.bat before removing it. Verify each deletion target is exactly the listed root-level ignored artifact; never remove Config/DefaultEngine.ini.

- [ ] **Step 5: Smoke-test the script, review ignored files, and commit**

Run:

~~~powershell
cmd /c D:/TESTUNREALPROJECT/AMADEUS_DEV.bat help
cmd /c D:/TESTUNREALPROJECT/AMADEUS_DEV.bat rebuild
git check-ignore Config/DefaultEngine.ini BuildLogs/UnrealBuildTool-Log.txt
git diff --check
git add .gitignore AMADEUS_DEV.bat Docs
git add -u -- '*.bat' '*.md' '*.txt' '*.zip' assign old return size speed top-down
git commit -m "chore: consolidate Unreal developer tooling"
~~~

Expected: help and rebuild complete, the two local paths are ignored, and only intended documentation/tooling files are staged.

### Task 7: Perform clean-build verification, playable regression, and final Git handoff

**Files:**
- Modify only when test evidence requires a narrowly scoped correction in the owning task's files.
- Do not add generated output, logs, local credentials, cache data, or packaged binaries.

**Interfaces:**
- Consumes: all production modules, AMADEUS_DEV.bat, and enabled plugin descriptors from Tasks 1 through 6.
- Produces: a reviewed clean build, automation evidence, manual behavior evidence, and a pushed implementation branch.

- [ ] **Step 1: Run a clean plugin rebuild and all AMADEUS automation tests**

Run:

~~~powershell
cmd /c D:/TESTUNREALPROJECT/AMADEUS_DEV.bat clean-plugins
cmd /c D:/TESTUNREALPROJECT/AMADEUS_DEV.bat rebuild
& 'D:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' 'D:/TESTUNREALPROJECT/TESTUNREALPROJECT.uproject' -unattended -nop4 -nullrhi '-ExecCmds=Automation RunTests AMADEUS; Quit' '-TestExit=Automation Test Queue Empty'
~~~

Expected: UBT and all AMADEUS automation tests succeed with no missing module, include, UHT, or redirected-type errors.

- [ ] **Step 2: Run the manual regression checklist in the editor**

Open the project using AMADEUS_DEV.bat launch and verify each item:

~~~text
1. SHIFT still switches third-person and top-down view.
2. TAB opens the realm, blocks outer movement/camera/casting, then restores prior view/input state on close.
3. Q selects Earth; a shape key selects Sphere, Cube, or Cone; an allowed held modifier completes the live grammar.
4. SPACE before ModifierActive spawns nothing; SPACE afterward spawns the selected Earth shape in both third-person and top-down aim.
5. A cast with no Speed modifier has no initial launch speed; a cast with Speed has the expected initial launch direction.
6. Successful casts reset only transient live state; failed placement/spawn does not reset it.
7. Earth impact/material behavior and active AMADEUS editor helpers remain usable.
~~~

- [ ] **Step 3: Audit module boundaries and staged content**

Run:

~~~powershell
rg -n '#include ".*Private/' Plugins
rg -n "EarthTestHarness|UEarthTestInputSubsystem|EarthTestInputSubsystem" TESTUNREALPROJECT.uproject Plugins Content Config Docs
git status --short
git diff --stat
git diff --cached --stat
~~~

Expected: no private cross-plugin include, no harness reference, and no generated/local-sensitive file staged.

- [ ] **Step 4: Push the reviewed implementation commits**

Task 7 must not introduce an unplanned catch-all source edit. If verification exposes a defect, stop this task, return to the owning task, add a precise corrective step and test there, and repeat its validation before restarting Task 7. When the clean build and regression checklist pass without a new correction, push the reviewed implementation commits:

~~~powershell
git push --set-upstream origin codex/unreal-architecture-cleanup
~~~

Expected: the remote reports the dedicated implementation branch is up to date after the push.

- [ ] **Step 5: Deliver the final implementation report**

Report the generic contract migration, new SpellExecution boundary, deleted harness, explicit plugin graph, tooling/documentation consolidation, test commands and results, manual regression results, commit hashes/messages, and push result. State any remaining Earth-only limitation explicitly: Earth is the sole currently realized element, and new elements require an explicit new branch plus their own realization module.

## Plan Self-Review

- Spec coverage: Tasks 1 and 2 cover generic contracts, legacy safety, shared ranges, and the pure live state machine. Task 3 covers the extracted production casting path, generic placement, preview migration, and Earth realization. Task 4 covers the dependency inversion and realm behavior. Task 5 covers descriptor activation and harness removal. Task 6 covers the exact tooling/documentation inventory. Task 7 covers clean builds, automation, manual behavior, staging, and push.
- Placeholder scan: the plan contains no deferred implementation markers; all required files, commands, state transitions, mappings, and validation conditions are named.
- Type consistency: FSpellDefinition and FResolvedSpell originate in Task 1; LiveSpellTypes and FLiveSpellState originate in Task 2; SpellExecution consumes ResolveGenericSpell(), FResolvedSpell, and its own placement types in Task 3; EarthMagic receives only FResolvedSpell plus Engine value types; PlayerView and InnerRealm use the exact balanced SetOuterWorldInputSuspended(bool) and SetExecutionSuspended(bool) contracts in Task 4.
