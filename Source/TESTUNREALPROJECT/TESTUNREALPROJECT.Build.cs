using UnrealBuildTool;

/** Minimal project module required to build the project's runtime plugins. */
public class TESTUNREALPROJECT : ModuleRules
{
    public TESTUNREALPROJECT(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "InputCore"
        });
    }
}
