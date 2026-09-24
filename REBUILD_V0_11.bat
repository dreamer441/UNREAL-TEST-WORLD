@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS v0.11 - clean live casting rebuild
echo ============================================================
echo.
if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this patch into the project root alongside TESTUNREALPROJECT.uproject.
  pause
  exit /b 1
)
if not exist "Plugins\SpellCastingBindings\Source\SpellCastingBindings\Private\SpellCastingBindingSubsystem.cpp" (
  echo ERROR: SpellCastingBindings source not found. Patch folders were not merged correctly.
  pause
  exit /b 1
)

echo Close Unreal Editor and any running game instances before continuing.
pause

echo [1/5] Clearing live casting modules...
for %%P in (SpellCastingBindings InnerRealm SpellCreation EarthMagic) do (
  if exist "Plugins\%%P\Binaries" rmdir /s /q "Plugins\%%P\Binaries"
  if exist "Plugins\%%P\Intermediate" rmdir /s /q "Plugins\%%P\Intermediate"
)

echo [2/5] Clearing dependent gameplay modules...
for %%P in (EarthTestHarness PlayerViewModes) do (
  if exist "Plugins\%%P\Binaries" rmdir /s /q "Plugins\%%P\Binaries"
  if exist "Plugins\%%P\Intermediate" rmdir /s /q "Plugins\%%P\Intermediate"
)

echo [3/5] Clearing generated project build rules...
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [4/5] Removing stale v0.10 module binaries if present...
if exist "Plugins\SpellCastingBindings\Binaries" rmdir /s /q "Plugins\SpellCastingBindings\Binaries"

echo [5/5] Opening project for Unreal's bundled rebuild...
echo If prompted to rebuild missing modules, select YES.
start "" "TESTUNREALPROJECT.uproject"

echo.
echo Test after build:
echo   SHIFT -> top-down
echo   TAB -> assign keys in meditation realm
echo   TAB -> return
echo   Q + hold A/S/D for different times + SPACE
echo.
echo If build fails, upload: %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
pause
