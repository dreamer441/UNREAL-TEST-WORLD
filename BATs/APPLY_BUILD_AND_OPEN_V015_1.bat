@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS Gameplay v0.15.1
echo   Architecture Cleanup Phase 2 - Generic Workbench
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this ZIP into D:\TESTUNREALPROJECT\
  pause
  exit /b 1
)

if not exist "Plugins\InnerRealm\Source\InnerRealm\Private\UI\InnerRealmShellUI.h" (
  echo ERROR: v0.15.0 Architecture Cleanup Phase 1 must already be installed.
  pause
  exit /b 1
)

echo Close Unreal Editor before continuing.
pause

echo [1/4] Applying v0.15.1 generic Workbench cleanup...
py -3 "%~dp0PATCH_V015_1_GENERIC_WORKBENCH.py"
if errorlevel 1 (
  echo.
  echo PATCH FAILED.
  echo Copy the patch error and send it to ChatGPT.
  pause
  exit /b 1
)

echo [2/4] Clearing affected generated products...
for %%D in (InnerRealm SpellCreation SpellGraph SpellPreview LiveSpellCasting SpellExecution) do (
  if exist "Plugins\%%D\Binaries" rmdir /s /q "Plugins\%%D\Binaries"
  if exist "Plugins\%%D\Intermediate" rmdir /s /q "Plugins\%%D\Intermediate"
)
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [3/4] Building TESTUNREALPROJECTEditor with UE 5.8...
call "D:\UE_5.8\Engine\Build\BatchFiles\Build.bat" TESTUNREALPROJECTEditor Win64 Development -Project="%CD%\TESTUNREALPROJECT.uproject" -WaitMutex -NoHotReloadFromIDE
if errorlevel 1 (
  echo.
  echo ============================================================
  echo BUILD FAILED
  echo Send the FIRST meaningful compiler error, or:
  echo   %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
  echo ============================================================
  pause
  exit /b 1
)

echo [4/4] BUILD SUCCEEDED. Opening Unreal...
start "" "%CD%\TESTUNREALPROJECT.uproject"

echo.
echo ============================================================
echo REGRESSION TEST
echo ============================================================
echo.
echo SPELL MODIFIER:
echo   - Sphere / Cube / Cone selection
echo   - all dimension sliders
echo   - amount / line / circle
echo   - line axis / spacing / circle radius
echo   - instance orientation
echo   - motion direction
echo   - speed / density / hardness / toughness / elasticity
echo   - distance / orientation
echo.
echo SHARED READY SLOTS:
echo   - save from Spell Modifier
echo   - save from Rune Canvas
echo   - exit TAB, press number, SPACE cast
echo.
echo RUNE CANVAS:
echo   - existing graph still compiles and updates Workbench
echo.
echo This patch intentionally does NOT redesign Canvas or add features.
echo.
pause
endlocal
