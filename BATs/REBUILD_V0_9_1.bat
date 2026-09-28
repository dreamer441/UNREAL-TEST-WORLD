@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   ProjectX - v0.9.1 camera sensitivity / sprint / Space
 echo ============================================================
echo.
if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract patch into your project root next to TESTUNREALPROJECT.uproject.
  pause
  exit /b 1
)
if not exist "Plugins\PlayerViewModes\Source\PlayerViewModes\Private\PlayerViewModeSubsystem.cpp" (
  echo ERROR: PlayerViewModes source file not found. ZIP folder structure was not merged.
  pause
  exit /b 1
)
if not exist "Plugins\EarthTestHarness\Source\EarthTestHarness\Private\EarthTestInputSubsystem.cpp" (
  echo ERROR: EarthTestHarness source file not found. ZIP folder structure was not merged.
  pause
  exit /b 1
)
if not exist "Plugins\InnerRealm\Source\InnerRealm\Private\InnerRealmSubsystem.cpp" (
  echo ERROR: InnerRealm source file not found. ZIP folder structure was not merged.
  pause
  exit /b 1
)

echo Close Unreal Editor completely before continuing.
pause

echo [1/5] Clearing PlayerViewModes generated files...
if exist "Plugins\PlayerViewModes\Binaries" rmdir /s /q "Plugins\PlayerViewModes\Binaries"
if exist "Plugins\PlayerViewModes\Intermediate" rmdir /s /q "Plugins\PlayerViewModes\Intermediate"
echo [2/5] Clearing EarthTestHarness generated files...
if exist "Plugins\EarthTestHarness\Binaries" rmdir /s /q "Plugins\EarthTestHarness\Binaries"
if exist "Plugins\EarthTestHarness\Intermediate" rmdir /s /q "Plugins\EarthTestHarness\Intermediate"
echo [3/5] Clearing InnerRealm generated files...
if exist "Plugins\InnerRealm\Binaries" rmdir /s /q "Plugins\InnerRealm\Binaries"
if exist "Plugins\InnerRealm\Intermediate" rmdir /s /q "Plugins\InnerRealm\Intermediate"
echo [4/5] Clearing old project build rules...
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"
echo [5/5] Opening project with Unreal's installed toolchain...
echo If Unreal asks to rebuild missing modules, click YES.
start "" "TESTUNREALPROJECT.uproject"
echo.
echo If compilation fails, please upload:
echo %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
pause
