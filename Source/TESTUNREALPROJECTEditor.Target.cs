using UnrealBuildTool;
using System.Collections.Generic;

/** Build target for the Unreal Editor project. */
public class TESTUNREALPROJECTEditorTarget : TargetRules
{
    public TESTUNREALPROJECTEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V7;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;
        CppStandard = CppStandardVersion.Cpp20;
        ExtraModuleNames.AddRange(new string[] { "TESTUNREALPROJECT" });
    }
}
