@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS v0.13.0.2 - cleaned spell-range API fix
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this ZIP into D:\TESTUNREALPROJECT\
  pause
  exit /b 1
)

echo Close Unreal Editor before continuing.
pause

echo [1/4] Updating SpellPreview to SpellParameterRanges...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0PATCH_V013_SPELL_PARAMETER_RANGES.ps1"
if errorlevel 1 (
  echo PATCH FAILED.
  pause
  exit /b 1
)

echo [2/4] Clearing SpellPreview generated products...
if exist "Plugins\SpellPreview\Binaries" rmdir /s /q "Plugins\SpellPreview\Binaries"
if exist "Plugins\SpellPreview\Intermediate" rmdir /s /q "Plugins\SpellPreview\Intermediate"

echo [3/4] Clearing project build-rule cache...
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [4/4] Opening project for rebuild...
start "" "TESTUNREALPROJECT.uproject"

echo.
echo If the build fails again, send the NEW UnrealBuildTool Log.txt.
echo.
pause
endlocal
