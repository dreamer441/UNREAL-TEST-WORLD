@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo  ProjectX - v0.8.2 shared Earth collision patch rebuild
 echo ============================================================
echo.
if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this patch beside TESTUNREALPROJECT.uproject.
  pause
  exit /b 1
)
if not exist "Plugins\EarthMagic\Source\EarthMagic\Private\EarthSpellDamageGeometry.cpp" (
  echo ERROR: EarthMagic source patch missing. Check that the ZIP folders were merged.
  pause
  exit /b 1
)
echo Make sure Unreal Editor is CLOSED before proceeding.
pause

echo [1/3] Clearing only EarthMagic generated build files...
if exist "Plugins\EarthMagic\Binaries" rmdir /s /q "Plugins\EarthMagic\Binaries"
if exist "Plugins\EarthMagic\Intermediate" rmdir /s /q "Plugins\EarthMagic\Intermediate"

echo [2/3] Clearing stale project build rules...
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [3/3] Opening project with Unreal's installed toolchain...
echo If Unreal asks to rebuild missing modules, click YES.
start "" "TESTUNREALPROJECT.uproject"
echo.
echo If compilation fails, send the latest:
echo %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
pause
