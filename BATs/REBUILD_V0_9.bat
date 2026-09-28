@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo  ProjectX - Gameplay v0.9 camera + movement rebuild
 echo ============================================================
echo.
if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this patch beside TESTUNREALPROJECT.uproject.
  pause
  exit /b 1
)
if not exist "Plugins\PlayerViewModes\Source\PlayerViewModes\Private\PlayerViewModeSubsystem.cpp" (
  echo ERROR: PlayerViewModes source is missing. Check that the ZIP folders were merged.
  pause
  exit /b 1
)
echo Make sure Unreal Editor is CLOSED before proceeding.
pause

echo [1/4] Clearing PlayerViewModes generated build files...
if exist "Plugins\PlayerViewModes\Binaries" rmdir /s /q "Plugins\PlayerViewModes\Binaries"
if exist "Plugins\PlayerViewModes\Intermediate" rmdir /s /q "Plugins\PlayerViewModes\Intermediate"

echo [2/4] Clearing EarthTestHarness generated build files...
if exist "Plugins\EarthTestHarness\Binaries" rmdir /s /q "Plugins\EarthTestHarness\Binaries"
if exist "Plugins\EarthTestHarness\Intermediate" rmdir /s /q "Plugins\EarthTestHarness\Intermediate"

echo [3/4] Clearing stale project build rules...
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [4/4] Opening project with Unreal's installed toolchain...
echo If Unreal asks to rebuild missing modules, click YES.
start "" "TESTUNREALPROJECT.uproject"
echo.
echo If compilation fails, send the latest:
echo %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
pause
