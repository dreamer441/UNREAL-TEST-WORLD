from pathlib import Path

ROOT = Path(__file__).resolve().parent

INNER_H = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Public/InnerRealmSubsystem.h"
INNER_CPP = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Private/InnerRealmSubsystem.cpp"
CREATION_H = ROOT / "Plugins/SpellCreation/Source/SpellCreation/Public/SpellCreationSubsystem.h"
CREATION_CPP = ROOT / "Plugins/SpellCreation/Source/SpellCreation/Private/SpellCreationSubsystem.cpp"
ARCH_DOC = ROOT / "Docs/ARCHITECTURE_V1.md"

for path in [INNER_H, INNER_CPP, CREATION_H, CREATION_CPP, ARCH_DOC]:
    if not path.exists():
        raise RuntimeError(f"Expected file missing: {path}")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"Could not find expected block for: {label}")
    return text.replace(old, new, 1)


print("[1/6] Verifying v0.15.0 architecture-cleanup base...")

inner_h = read(INNER_H)
inner_cpp = read(INNER_CPP)
creation_h = read(CREATION_H)
creation_cpp = read(CREATION_CPP)

required_base_markers = [
    ("shared InnerRealm shell", "TSharedPtr<SWidget> ShellWidget;" in inner_h),
    ("shared shell callbacks", "FInnerRealmShellCallbacks ShellCallbacks;" in inner_cpp),
    ("graph compiler boundary", "FSpellGraphCompiler::Compile(Nodes, *Codex)" in read(
        ROOT / "Plugins/SpellGraph/Source/SpellGraph/Private/SpellGraphSubsystem.cpp"
    )),
]

failed = [name for name, ok in required_base_markers if not ok]
if failed:
    raise RuntimeError(
        "This patch expects the working v0.15.0 cleanup first. Missing: "
        + ", ".join(failed)
    )

print("[2/6] Moving InnerRealm Workbench onto canonical FSpellDefinition...")

inner_h = replace_once(
    inner_h,
    '#include "EarthSpellDefinition.h"',
    '#include "SpellDefinition.h"',
    "generic spell definition include",
)

inner_h = inner_h.replace(
    "    FEarthSpellDefinition ReadSpell() const;\n"
    "    void WriteSpell(const FEarthSpellDefinition& Spell);\n"
    "    void SetShape(EEarthSpellShape Shape);",
    "    FSpellDefinition ReadSpell() const;\n"
    "    void WriteSpell(const FSpellDefinition& Spell);\n"
    "    void SetShape(ESpellShape Shape);",
)

if "FEarthSpellDefinition ReadSpell()" in inner_h or "EEarthSpellShape Shape" in inner_h:
    raise RuntimeError("Could not convert InnerRealm spell API to FSpellDefinition.")

write(INNER_H, inner_h)

inner_cpp = replace_once(
    inner_cpp,
    '#include "EarthSpellMath.h"',
    '#include "SpellShapeMath.h"',
    "generic shape/mass math include",
)

inner_cpp = inner_cpp.replace("EEarthSpellShape", "ESpellShape")
inner_cpp = inner_cpp.replace("FEarthSpellDefinition", "FSpellDefinition")

old_read_write = '''FSpellDefinition UInnerRealmSubsystem::ReadSpell() const
{
    if (const USpellCreationSubsystem* SpellCreation = GetSpellCreation())
    {
        return SpellCreation->GetStoredSpellDefinition();
    }
    return FSpellDefinition();
}

void UInnerRealmSubsystem::WriteSpell(const FSpellDefinition& Spell)
{
    if (USpellCreationSubsystem* SpellCreation = GetSpellCreation())
    {
        SpellCreation->SetStoredSpellDefinition(Spell);
    }
}'''

new_read_write = '''FSpellDefinition UInnerRealmSubsystem::ReadSpell() const
{
    if (const USpellCreationSubsystem* SpellCreation = GetSpellCreation())
    {
        return SpellCreation->GetStoredGenericSpellDefinition();
    }
    return FSpellDefinition();
}

void UInnerRealmSubsystem::WriteSpell(const FSpellDefinition& Spell)
{
    if (USpellCreationSubsystem* SpellCreation = GetSpellCreation())
    {
        SpellCreation->SetStoredGenericSpellDefinition(Spell);
    }
}'''

inner_cpp = replace_once(
    inner_cpp,
    old_read_write,
    new_read_write,
    "canonical Workbench read/write",
)

for old, new in [
    ("Spell.SphereRadiusCm", "Spell.ShapeDefinition.SphereRadiusCm"),
    ("Spell.CubeXcm", "Spell.ShapeDefinition.CubeXcm"),
    ("Spell.CubeYcm", "Spell.ShapeDefinition.CubeYcm"),
    ("Spell.CubeZcm", "Spell.ShapeDefinition.CubeZcm"),
    ("Spell.ConeRadiusCm", "Spell.ShapeDefinition.ConeRadiusCm"),
    ("Spell.ConeHeightCm", "Spell.ShapeDefinition.ConeHeightCm"),
]:
    inner_cpp = inner_cpp.replace(old, new)

for old, new in [
    ("ReadSpell().DensityKgPerM3", "ReadSpell().Material.DensityKgPerM3"),
    ("Spell.DensityKgPerM3", "Spell.Material.DensityKgPerM3"),
    ("ReadSpell().Hardness", "ReadSpell().Material.Hardness"),
    ("Spell.Hardness", "Spell.Material.Hardness"),
    ("ReadSpell().Toughness", "ReadSpell().Material.Toughness"),
    ("Spell.Toughness", "Spell.Material.Toughness"),
    ("ReadSpell().Elasticity", "ReadSpell().Material.Restitution"),
    ("Spell.Elasticity", "Spell.Material.Restitution"),
]:
    inner_cpp = inner_cpp.replace(old, new)

for old, new in [
    ("ReadSpell().PatternOrientation", "ReadSpell().Pattern.InstanceOrientation"),
    ("Spell.PatternOrientation", "Spell.Pattern.InstanceOrientation"),
    ("ReadSpell().PatternAxis", "ReadSpell().Pattern.LineAxis"),
    ("Spell.PatternAxis", "Spell.Pattern.LineAxis"),
    ("ReadSpell().CircleRadiusCm", "ReadSpell().Pattern.CircleRadiusCm"),
    ("Spell.CircleRadiusCm", "Spell.Pattern.CircleRadiusCm"),
    ("ReadSpell().SpacingCm", "ReadSpell().Pattern.SpacingCm"),
    ("Spell.SpacingCm", "Spell.Pattern.SpacingCm"),
    ("ReadSpell().Arrangement", "ReadSpell().Pattern.Arrangement"),
    ("Spell.Arrangement", "Spell.Pattern.Arrangement"),
    ("ReadSpell().Amount", "ReadSpell().Pattern.Amount"),
    ("Spell.Amount", "Spell.Pattern.Amount"),
]:
    inner_cpp = inner_cpp.replace(old, new)

inner_cpp = inner_cpp.replace(
    "UEarthSpellMath::CalculateMassKg(ReadSpell())",
    "FSpellShapeMath::CalculateMassKg(ReadSpell())",
)
inner_cpp = inner_cpp.replace(
    "UEarthSpellMath::CalculateMassKg(Spell)",
    "FSpellShapeMath::CalculateMassKg(Spell)",
)

write(INNER_CPP, inner_cpp)

print("[3/6] Removing synchronized legacy shadow state from SpellCreation...")

old_private = '''private:
    UPROPERTY()
    FEarthSpellDefinition StoredSpell;

    /** Canonical runtime value; StoredSpell retains the original reflected type. */
    UPROPERTY()
    FSpellDefinition StoredGenericSpell;'''

new_private = '''private:
    /** Canonical single-spell runtime value. */
    UPROPERTY()
    FSpellDefinition StoredGenericSpell;'''

creation_h = replace_once(
    creation_h,
    old_private,
    new_private,
    "remove legacy stored shadow",
)

legacy_getter = '''    UFUNCTION(BlueprintPure, Category="Spell Creation")
    FEarthSpellDefinition GetStoredSpellDefinition() const
    {
        return FSpellDefinitionAdapter::ToLegacyEarth(StoredGenericSpell);
    }'''

compat_getter = '''    /**
     * Compatibility projection for older Earth-specific Blueprint/UI callers.
     * New code should use GetStoredGenericSpellDefinition().
     */
    UFUNCTION(BlueprintPure, Category="Spell Creation")
    FEarthSpellDefinition GetStoredSpellDefinition() const
    {
        return FSpellDefinitionAdapter::ToLegacyEarth(StoredGenericSpell);
    }'''

if compat_getter not in creation_h:
    creation_h = replace_once(
        creation_h,
        legacy_getter,
        compat_getter,
        "legacy compatibility getter comment",
    )

write(CREATION_H, creation_h)

creation_cpp = creation_cpp.replace(
    "    StoredSpell = FSpellDefinitionAdapter::ToLegacyEarth(StoredGenericSpell);\n",
    "",
)

creation_cpp = replace_once(
    creation_cpp,
    '''void USpellCreationSubsystem::ResetToDefaultEarthSpell()
{
    SetStoredSpellDefinition(FEarthSpellDefinition());
}''',
    '''void USpellCreationSubsystem::ResetToDefaultEarthSpell()
{
    // The generic default is currently Earth, so reset without going through
    // the legacy Earth compatibility adapter.
    SetStoredGenericSpellDefinition(FSpellDefinition());
}''',
    "generic default reset",
)

write(CREATION_CPP, creation_cpp)

print("[4/6] Updating architecture documentation...")

doc = read(ARCH_DOC)

old_phase2 = '''### Phase 2 — generic Workbench
- make Spell Modifier edit `FSpellDefinition` directly
- retain `FEarthSpellDefinition` only as a compatibility adapter'''

new_phase2 = '''### Phase 2 — generic Workbench — COMPLETE
- Spell Modifier reads/writes `FSpellDefinition` directly
- SpellCreation owns only one stored spell value: `FSpellDefinition`
- `FEarthSpellDefinition` remains only as a compatibility projection/adapter
- no new presentation code may depend on the legacy Earth spell struct'''

if new_phase2 not in doc:
    if old_phase2 in doc:
        doc = doc.replace(old_phase2, new_phase2, 1)
    else:
        raise RuntimeError("Could not find Phase 2 section in ARCHITECTURE_V1.md.")

if "### v0.15.1" not in doc:
    doc += '''

## Current cleanup status

### v0.15.0
- shared InnerRealm shell
- shared ready-spell bar
- preview made display-only
- graph compiler extracted from graph storage

### v0.15.1
- Spell Modifier migrated to canonical `FSpellDefinition`
- synchronized `StoredSpell` legacy shadow removed from SpellCreation
- legacy Earth definition retained only for compatibility callers
'''

write(ARCH_DOC, doc)

print("[5/6] Verifying no legacy spell representation remains in InnerRealm...")

inner_h = read(INNER_H)
inner_cpp = read(INNER_CPP)
creation_h = read(CREATION_H)
creation_cpp = read(CREATION_CPP)

checks = {
    "InnerRealm generic include":
        '#include "SpellDefinition.h"' in inner_h,
    "InnerRealm legacy include removed":
        "EarthSpellDefinition.h" not in inner_h,
    "InnerRealm legacy type removed":
        "FEarthSpellDefinition" not in inner_h and
        "FEarthSpellDefinition" not in inner_cpp,
    "InnerRealm legacy shape enum removed":
        "EEarthSpellShape" not in inner_h and
        "EEarthSpellShape" not in inner_cpp,
    "Workbench reads generic spell":
        "GetStoredGenericSpellDefinition()" in inner_cpp,
    "Workbench writes generic spell":
        "SetStoredGenericSpellDefinition(Spell)" in inner_cpp,
    "No Workbench legacy getter":
        "GetStoredSpellDefinition()" not in inner_cpp,
    "No Workbench legacy setter":
        "SetStoredSpellDefinition(Spell)" not in inner_cpp,
    "Generic mass math":
        "FSpellShapeMath::CalculateMassKg" in inner_cpp,
    "Legacy Earth mass math removed":
        "UEarthSpellMath" not in inner_cpp,
    "Canonical material access":
        "Material.DensityKgPerM3" in inner_cpp and
        "Material.Restitution" in inner_cpp,
    "Canonical pattern access":
        "Pattern.Amount" in inner_cpp and
        "Pattern.InstanceOrientation" in inner_cpp,
    "Legacy stored shadow removed":
        "FEarthSpellDefinition StoredSpell;" not in creation_h and
        "StoredSpell =" not in creation_cpp,
    "Compatibility API retained":
        "FEarthSpellDefinition GetStoredSpellDefinition() const" in creation_h,
}

failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise RuntimeError("Verification failed: " + ", ".join(failed))

print("[6/6] v0.15.1 generic Workbench cleanup applied successfully.")
print()
print("Canonical spell ownership now:")
print("  SpellCreation.StoredGenericSpell : FSpellDefinition")
print("  Spell Modifier                  : FSpellDefinition")
print("  Rune Graph compiler             : FSpellDefinition")
print("  Ready slots                     : FSpellDefinition")
print()
print("FEarthSpellDefinition remains only as a compatibility adapter for older callers.")
