@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS Gameplay v0.14.0.1
echo   Rune Canvas Input / Hit-Test Fix
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this ZIP into D:\TESTUNREALPROJECT\
  pause
  exit /b 1
)

if not exist "Plugins\SpellGraph\SpellGraph.uplugin" (
  echo ERROR: v0.14.0 Rune Canvas must already be installed.
  pause
  exit /b 1
)

echo Close Unreal Editor before continuing.
pause

echo [1/4] Applying Canvas input fix...
py -3 "%~dp0PATCH_V014_0_1_CANVAS_INPUT_FIX.py"
if errorlevel 1 (
  echo.
  echo PATCH FAILED. Copy the error text and send it to ChatGPT.
  pause
  exit /b 1
)

echo [2/4] Clearing InnerRealm generated products...
if exist "Plugins\InnerRealm\Binaries" rmdir /s /q "Plugins\InnerRealm\Binaries"
if exist "Plugins\InnerRealm\Intermediate" rmdir /s /q "Plugins\InnerRealm\Intermediate"
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [3/4] Building TESTUNREALPROJECTEditor...
call "D:\UE_5.8\Engine\Build\BatchFiles\Build.bat" TESTUNREALPROJECTEditor Win64 Development -Project="%CD%\TESTUNREALPROJECT.uproject" -WaitMutex -NoHotReloadFromIDE
if errorlevel 1 (
  echo.
  echo ============================================================
  echo BUILD FAILED
  echo Send the first meaningful compiler error or:
  echo   %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
  echo ============================================================
  pause
  exit /b 1
)

echo [4/4] BUILD SUCCEEDED. Opening Unreal...
start "" "%CD%\TESTUNREALPROJECT.uproject"

echo.
echo TEST:
echo   TAB -^> RUNE CANVAS
echo   1. Click Earth in the left palette.
echo   2. Earth should appear in SEMANTIC GRAPH and become selected.
echo   3. Click Sphere.
echo   4. Select Earth again, then add Speed / Amount / Circle etc.
echo   5. Select a Tier-II node and attach a Tier-III value.
echo.
echo The 3D preview remains visible but no longer catches Canvas mouse input.
echo.
pause
endlocal
