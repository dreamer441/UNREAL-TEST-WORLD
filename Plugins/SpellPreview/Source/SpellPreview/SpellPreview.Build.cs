using UnrealBuildTool;

public class SpellPreview : ModuleRules
{
    public SpellPreview(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core", "CoreUObject", "Engine", "SpellCreation", "LiveSpellCasting", "PlayerViewModes"
        });
    }
}
