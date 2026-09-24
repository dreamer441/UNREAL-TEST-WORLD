@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS v0.11.1 - editor + live casting feel patch
echo ============================================================
echo.
if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this patch into the project root alongside TESTUNREALPROJECT.uproject.
  pause
  exit /b 1
)
if not exist "Plugins\SpellCastingBindings\Source\SpellCastingBindings\Public\LiveSpellTuning.h" (
  echo ERROR: v0.11.1 patch files were not merged correctly.
  pause
  exit /b 1
)

echo Close Unreal Editor and any running game instances before continuing.
pause

echo [1/4] Clearing changed plugin build products...
for %%P in (SpellCastingBindings InnerRealm PlayerViewModes) do (
  if exist "Plugins\%%P\Binaries" rmdir /s /q "Plugins\%%P\Binaries"
  if exist "Plugins\%%P\Intermediate" rmdir /s /q "Plugins\%%P\Intermediate"
)

echo [2/4] Clearing directly dependent gameplay modules...
for %%P in (EarthTestHarness) do (
  if exist "Plugins\%%P\Binaries" rmdir /s /q "Plugins\%%P\Binaries"
  if exist "Plugins\%%P\Intermediate" rmdir /s /q "Plugins\%%P\Intermediate"
)

echo [3/4] Clearing generated project build rules...
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [4/4] Opening project for Unreal's bundled rebuild...
echo If prompted to rebuild missing modules, select YES.
start "" "TESTUNREALPROJECT.uproject"

echo.
echo Test:
echo   TAB -> old slider editor + key boxes should both be present
echo   SHIFT -> top-down should be farther and faster to orbit
echo   Hold A 1s / 2s / 3s -> size difference should be obvious
echo   Hold S for different durations -> speed difference should be obvious
echo.
echo If build fails, upload: %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
pause
