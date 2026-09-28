@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS Gameplay v0.13.3
echo   Pattern Orientation / Instance Transforms
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this ZIP into D:\TESTUNREALPROJECT\
  pause
  exit /b 1
)

if not exist "Plugins\SpellPattern\SpellPattern.uplugin" (
  echo ERROR: v0.13.2.1 must be installed and working first.
  pause
  exit /b 1
)

echo Close Unreal Editor before continuing.
pause

echo [1/6] Applying v0.13.3 source patch...
py -3 "%~dp0PATCH_V013_3_PATTERN_ORIENTATION.py"
if errorlevel 1 (
  echo.
  echo PATCH FAILED. Copy the error text and send it to ChatGPT.
  pause
  exit /b 1
)

echo [2/6] Clearing affected generated products...
for %%D in (SpellPattern SpellCreation SpellExecution SpellPreview InnerRealm SpellLoadout) do (
  if exist "Plugins\%%D\Binaries" rmdir /s /q "Plugins\%%D\Binaries"
  if exist "Plugins\%%D\Intermediate" rmdir /s /q "Plugins\%%D\Intermediate"
)

echo [3/6] Clearing project build-rule cache...
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [4/6] Building TESTUNREALPROJECTEditor with UE 5.8...
if not exist "D:\UE_5.8\Engine\Build\BatchFiles\Build.bat" (
  echo ERROR: D:\UE_5.8\Engine\Build\BatchFiles\Build.bat not found.
  pause
  exit /b 1
)

call "D:\UE_5.8\Engine\Build\BatchFiles\Build.bat" TESTUNREALPROJECTEditor Win64 Development -Project="%CD%\TESTUNREALPROJECT.uproject" -WaitMutex -NoHotReloadFromIDE
if errorlevel 1 (
  echo.
  echo ============================================================
  echo BUILD FAILED
  echo Send the newest:
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
echo   TAB / WORKBENCH
echo     - Amount 2+
echo     - INSTANCE ORIENTATION appears
echo     - Shared / Outward / Inward / Tangent
echo     - preview rotates each copy immediately
echo.
echo   BEST VISUAL TEST
echo     - Cone
echo     - Spell Orientation = Forward / X
echo     - Amount = 8
echo     - Circle
echo     - switch Shared / Outward / Inward / Tangent
echo.
echo   READY SPELL
echo     - save pattern into a number slot
echo     - leave TAB
echo     - press slot number
echo     - live preview preserves instance orientation
echo     - SPACE casts the same transforms
echo.
echo IMPORTANT:
echo   Pattern Orientation changes facing only.
echo   Projectile movement direction is unchanged in this patch.
echo.
pause
endlocal
