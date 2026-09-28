@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS v0.12.1 - strict casting hierarchy
echo ============================================================
echo.
if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this patch into the project root alongside TESTUNREALPROJECT.uproject.
  pause
  exit /b 1
)
if not exist "Plugins\LiveSpellCasting\Source\LiveSpellCasting\Public\LiveSpellSessionSubsystem.h" (
  echo ERROR: LiveSpellCasting patch files were not merged correctly.
  pause
  exit /b 1
)

echo Close Unreal Editor and any running game instances before continuing.
pause

echo [1/3] Clearing affected gameplay plugin build products...
for %%P in (LiveSpellCasting SpellCastingBindings SpellPreview EarthTestHarness) do (
  if exist "Plugins\%%P\Binaries" rmdir /s /q "Plugins\%%P\Binaries"
  if exist "Plugins\%%P\Intermediate" rmdir /s /q "Plugins\%%P\Intermediate"
)

echo [2/3] Clearing generated project build rules...
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [3/3] Opening project for Unreal's bundled rebuild...
echo If prompted to rebuild missing modules, select YES.
start "" "TESTUNREALPROJECT.uproject"

echo.
echo Gameplay check:
echo   1. Press a modifier first - nothing should happen.
echo   2. Press a shape first - nothing should happen.
echo   3. Press Earth - aura appears.
echo   4. Press shape - ghost shape appears.
echo   5. SPACE now - nothing should cast yet.
echo   6. Hold any valid modifier - spell becomes cast-ready.
echo   7. SPACE - spell casts once and session resets.
echo.
echo If build fails, upload: %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
pause
