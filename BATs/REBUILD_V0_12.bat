@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS v0.12 - live casting session + preview
echo ============================================================
echo.
if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this patch into the project root alongside TESTUNREALPROJECT.uproject.
  pause
  exit /b 1
)
if not exist "Plugins\LiveSpellCasting\Source\LiveSpellCasting\Public\LiveSpellSessionSubsystem.h" (
  echo ERROR: v0.12 LiveSpellCasting files were not merged correctly.
  pause
  exit /b 1
)
if not exist "Plugins\SpellPreview\Source\SpellPreview\Public\SpellPreviewSubsystem.h" (
  echo ERROR: v0.12 SpellPreview files were not merged correctly.
  pause
  exit /b 1
)

echo Close Unreal Editor and any running game instances before continuing.
pause

echo [1/4] Clearing changed/new gameplay plugin build products...
for %%P in (LiveSpellCasting SpellPreview SpellCastingBindings InnerRealm EarthTestHarness SpellCreation PlayerViewModes EarthMagic) do (
  if exist "Plugins\%%P\Binaries" rmdir /s /q "Plugins\%%P\Binaries"
  if exist "Plugins\%%P\Intermediate" rmdir /s /q "Plugins\%%P\Intermediate"
)

echo [2/4] Clearing generated project build rules...
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [3/4] Opening project for Unreal's bundled rebuild...
echo If prompted to rebuild missing modules, select YES.
start "" "TESTUNREALPROJECT.uproject"

echo [4/4] Gameplay checks after build:
echo   TAB: text should be black; sliders + per-option key boxes remain.
echo   In a binding box, press its existing key again: binding should become empty.
echo   Top-down, SPACE before any construction: nothing should cast.
echo   Q: green Earth aura. Shape key: ghost preview. Hold dimension key: preview grows.
echo   SPACE: one spell casts; live aura/preview reset; SPACE again does nothing.
echo   Spawn should always be in front of the character, not behind the camera.
echo.
echo If build fails, upload: %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
pause
