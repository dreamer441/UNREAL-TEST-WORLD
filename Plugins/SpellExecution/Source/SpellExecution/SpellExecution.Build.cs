using UnrealBuildTool;

public class SpellExecution : ModuleRules
{
    public SpellExecution(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core", "CoreUObject", "Engine", "InputCore",
            "SpellCreation", "LiveSpellCasting", "PlayerViewModes", "EarthMagic"
        });
    }
}
