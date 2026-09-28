@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS Gameplay v0.13.2
echo   Multiplicity + Pattern Resolver + Modifier Contract
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this ZIP into D:\TESTUNREALPROJECT\
  pause
  exit /b 1
)

if not exist "Plugins\SpellLoadout\SpellLoadout.uplugin" (
  echo ERROR: Install the working v0.13.1.1 patch first.
  pause
  exit /b 1
)

echo Close Unreal Editor before continuing.
pause

echo [1/6] Applying v0.13.2 source patch...
py -3 "%~dp0PATCH_V013_2_MULTIPLICITY.py"
if errorlevel 1 (
  echo.
  echo PATCH FAILED. Copy the error text and send it to ChatGPT.
  pause
  exit /b 1
)

echo [2/6] Clearing affected generated products...
for %%D in (SpellPattern SpellCreation SpellExecution SpellPreview InnerRealm SpellLoadout LiveSpellCasting) do (
  if exist "Plugins\%%D\Binaries" rmdir /s /q "Plugins\%%D\Binaries"
  if exist "Plugins\%%D\Intermediate" rmdir /s /q "Plugins\%%D\Intermediate"
)

echo [3/6] Clearing project build-rule cache...
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [4/6] Building TESTUNREALPROJECTEditor with UE 5.8...
if not exist "D:\UE_5.8\Engine\Build\BatchFiles\Build.bat" (
  echo ERROR: UE 5.8 Build.bat was not found.
  pause
  exit /b 1
)

call "D:\UE_5.8\Engine\Build\BatchFiles\Build.bat" TESTUNREALPROJECTEditor Win64 Development -Project="%CD%\TESTUNREALPROJECT.uproject" -WaitMutex -NoHotReloadFromIDE
if errorlevel 1 (
  echo.
  echo ============================================================
  echo BUILD FAILED
  echo Send:
  echo   %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
  echo ============================================================
  pause
  exit /b 1
)

echo [5/6] BUILD SUCCEEDED.
echo [6/6] Opening Unreal...
start "" "%CD%\TESTUNREALPROJECT.uproject"

echo.
echo TEST:
echo   - TAB: MULTIPLE OBJECTS section
echo   - Amount 1 = one object
echo   - Amount 2+ = Line or Circle
echo   - Line: Forward / Right / Up + Spacing
echo   - Circle: Radius
echo   - Workbench preview updates all objects
echo   - Save pattern to a ready slot, leave TAB, press number, SPACE
echo   - all realized objects share current Orientation
echo.
pause
endlocal
