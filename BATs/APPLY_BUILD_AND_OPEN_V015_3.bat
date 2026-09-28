@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS Gameplay v0.15.3
echo   Rune Canvas Manual Branches + Category Palette
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this ZIP into D:\TESTUNREALPROJECT\
  pause
  exit /b 1
)

if not exist "Plugins\InnerRealm\Source\InnerRealm\Private\UI\RuneCanvasUI.cpp" (
  echo ERROR: v0.15.2 Presentation Split must already be installed.
  pause
  exit /b 1
)

echo Close Unreal Editor before continuing.
pause

echo [1/4] Applying v0.15.3 Canvas interaction cleanup...
py -3 "%~dp0PATCH_V015_3_MANUAL_BRANCH_CATEGORIES.py"
if errorlevel 1 (
  echo.
  echo PATCH FAILED.
  echo Copy the patch error and send it to ChatGPT.
  pause
  exit /b 1
)

echo [2/4] Clearing affected generated products...
if exist "Plugins\InnerRealm\Binaries" rmdir /s /q "Plugins\InnerRealm\Binaries"
if exist "Plugins\InnerRealm\Intermediate" rmdir /s /q "Plugins\InnerRealm\Intermediate"
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
echo TEST
echo ============================================================
echo.
echo START:
echo   CATEGORIES -^> ELEMENT -^> Earth
echo   CATEGORIES -^> SHAPE -^> Cube
echo   One combined Earth + Cube node appears.
echo.
echo MANUAL BRANCH:
echo   Do nothing: NO empty line should exist.
echo   Double-click Earth+Cube: exactly ONE empty line appears.
echo   CATEGORIES -^> SHAPE PARAMETERS
echo   Only Cube X / Cube Y / Cube Z should be shown.
echo   Choose Cube X: it attaches and the empty line is CONSUMED.
echo   No new empty line should appear automatically.
echo.
echo SECOND BRANCH:
echo   Double-click Earth+Cube again.
echo   A new free radial line appears.
echo   Choose another category / Sign.
echo.
echo TERMINAL:
echo   Double-click Cube X.
echo   CATEGORIES -^> VALUE -^> choose a magnitude.
echo   Tier III remains terminal.
echo.
pause
endlocal
