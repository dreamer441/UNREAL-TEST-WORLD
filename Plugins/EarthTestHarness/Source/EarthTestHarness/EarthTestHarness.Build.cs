using UnrealBuildTool;
public class EarthTestHarness : ModuleRules
{
    public EarthTestHarness(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core", "CoreUObject", "Engine", "InputCore",
            "SpellCreation", "InnerRealm", "EarthMagic", "PlayerViewModes", "LiveSpellCasting"
        });
    }
}
