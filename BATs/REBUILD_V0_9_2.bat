@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS v0.9.2 - view recovery and smoother orbit
 echo ============================================================
echo.
if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this patch into the project root alongside TESTUNREALPROJECT.uproject.
  pause
  exit /b 1
)
if not exist "Plugins\PlayerViewModes\Source\PlayerViewModes\Private\PlayerViewModeSubsystem.cpp" (
  echo ERROR: PlayerViewModes source not found. The patch folder structure was not merged.
  pause
  exit /b 1
)
if not exist "Plugins\PlayerViewModes\Source\PlayerViewModes\Private\PlayerTopDownCamera.cpp" (
  echo ERROR: PlayerTopDownCamera source not found. The patch folder structure was not merged.
  pause
  exit /b 1
)

echo Close Unreal Editor and any running game instances before continuing.
pause

echo [1/3] Clearing only PlayerViewModes compiled output...
if exist "Plugins\PlayerViewModes\Binaries" rmdir /s /q "Plugins\PlayerViewModes\Binaries"
if exist "Plugins\PlayerViewModes\Intermediate" rmdir /s /q "Plugins\PlayerViewModes\Intermediate"
echo [2/3] Clearing generated project build rules...
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"
echo [3/3] Opening the project for Unreal's bundled rebuild...
echo If prompted to rebuild missing modules, select YES.
start "" "TESTUNREALPROJECT.uproject"
echo.
echo If the build fails, upload: %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
pause
