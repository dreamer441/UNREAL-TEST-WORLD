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

Store FSpellDefinition as the canonical UPROPERTY. Add generic accessors with distinct names and implement old functions as adapters.

~~~cpp
UFUNCTION(BlueprintPure, Category="Spell Creation")
FSpellDefinition GetStoredGenericSpellDefinition() const { return StoredSpell; }

UFUNCTION(BlueprintCallable, Category="Spell Creation")
void SetStoredGenericSpellDefinition(const FSpellDefinition& NewSpell);

UFUNCTION(BlueprintPure, Category="Spell Creation")
FEarthSpellDefinition GetStoredSpellDefinition() const
{
    return FSpellDefinitionAdapter::ToLegacyEarth(StoredSpell);
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
