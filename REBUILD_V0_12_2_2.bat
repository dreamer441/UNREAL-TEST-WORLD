@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS v0.12.2.2 - live speed zero-state fix
echo ============================================================
echo.
if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this patch into the project root alongside TESTUNREALPROJECT.uproject.
  pause
  exit /b 1
)
if not exist "Plugins\LiveSpellCasting\Source\LiveSpellCasting\Private\LiveSpellSessionSubsystem.cpp" (
  echo ERROR: LiveSpellCasting patch file was not merged correctly.
  pause
  exit /b 1
)
if not exist "Plugins\SpellPreview\Source\SpellPreview\Private\SpellPreviewSubsystem.cpp" (
  echo ERROR: SpellPreview patch file was not merged correctly.
  pause
  exit /b 1
)

echo Close Unreal Editor and any running game instances before continuing.
pause

echo [1/4] Clearing LiveSpellCasting generated build products...
if exist "Plugins\LiveSpellCasting\Binaries" rmdir /s /q "Plugins\LiveSpellCasting\Binaries"
if exist "Plugins\LiveSpellCasting\Intermediate" rmdir /s /q "Plugins\LiveSpellCasting\Intermediate"

echo [2/4] Clearing SpellPreview generated build products...
if exist "Plugins\SpellPreview\Binaries" rmdir /s /q "Plugins\SpellPreview\Binaries"
if exist "Plugins\SpellPreview\Intermediate" rmdir /s /q "Plugins\SpellPreview\Intermediate"

echo [3/4] Clearing generated project build rules...
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [4/4] Opening project for Unreal's bundled rebuild...
echo If prompted to rebuild missing modules, select YES.
start "" "TESTUNREALPROJECT.uproject"

echo.
echo Expected live-speed behavior:
echo   element + shape = 0 m/s and 0 rings
 echo   Speed key low = 1 ring
 echo   Speed key medium = 2 rings
 echo   Speed key high = 3 rings
 echo   reset/new spell = back to 0 m/s and 0 rings
 echo.
echo If build fails, upload: %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
pause
