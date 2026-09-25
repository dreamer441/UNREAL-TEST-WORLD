using UnrealBuildTool;
using System.Collections.Generic;

/** Build target for the playable project. */
public class TESTUNREALPROJECTTarget : TargetRules
{
    public TESTUNREALPROJECTTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V7;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;
        CppStandard = CppStandardVersion.Cpp20;
        ExtraModuleNames.AddRange(new string[] { "TESTUNREALPROJECT" });
    }
}
