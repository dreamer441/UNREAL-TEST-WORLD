@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS v0.10 - live spell slider key bindings
 echo ============================================================
echo.
if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this patch into the project root alongside TESTUNREALPROJECT.uproject.
  pause
  exit /b 1
)
if not exist "Plugins\SpellCastingBindings\Source\SpellCastingBindings\Private\SpellCastingBindingSubsystem.cpp" (
  echo ERROR: SpellCastingBindings source not found. The patch folder structure was not merged.
  pause
  exit /b 1
)

echo Close Unreal Editor and any running game instances before continuing.
pause

echo [1/4] Clearing SpellCastingBindings compiled output...
if exist "Plugins\SpellCastingBindings\Binaries" rmdir /s /q "Plugins\SpellCastingBindings\Binaries"
if exist "Plugins\SpellCastingBindings\Intermediate" rmdir /s /q "Plugins\SpellCastingBindings\Intermediate"
echo [2/4] Clearing InnerRealm and PlayerViewModes compiled output...
if exist "Plugins\InnerRealm\Binaries" rmdir /s /q "Plugins\InnerRealm\Binaries"
if exist "Plugins\InnerRealm\Intermediate" rmdir /s /q "Plugins\InnerRealm\Intermediate"
if exist "Plugins\PlayerViewModes\Binaries" rmdir /s /q "Plugins\PlayerViewModes\Binaries"
if exist "Plugins\PlayerViewModes\Intermediate" rmdir /s /q "Plugins\PlayerViewModes\Intermediate"
echo [3/4] Clearing generated project build rules...
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"
echo [4/4] Opening the project for Unreal's bundled rebuild...
echo If prompted to rebuild missing modules, select YES.
start "" "TESTUNREALPROJECT.uproject"
echo.
echo If the build fails, upload: %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
pause
