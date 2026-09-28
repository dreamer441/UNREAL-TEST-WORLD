@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS Gameplay v0.15.2
echo   Architecture Cleanup Phase 3A - Presentation Split
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this ZIP into D:\TESTUNREALPROJECT\
  pause
  exit /b 1
)

if not exist "Plugins\InnerRealm\Source\InnerRealm\Private\UI\InnerRealmShellUI.h" (
  echo ERROR: v0.15.0 Architecture Cleanup must already be installed.
  pause
  exit /b 1
)

echo Close Unreal Editor before continuing.
pause

echo [1/4] Splitting InnerRealm presentation source...
py -3 "%~dp0PATCH_V015_2_PRESENTATION_SPLIT.py"
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
echo REGRESSION TEST
echo ============================================================
echo.
echo This patch should NOT change behavior.
echo.
echo Check:
echo   - TAB enter / exit
echo   - SPELL MODIFIER controls
echo   - shared ready slots
echo   - CODEX browsing
echo   - RUNE CANVAS creation / radial layout
echo   - compile/apply
echo   - number key load + SPACE cast
echo.
echo If all of those behave exactly as before, Phase 3A is complete.
echo.
pause
endlocal
