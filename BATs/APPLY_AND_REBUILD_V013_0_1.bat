@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS v0.13.0.1 - Workbench dependency-cycle fix
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this ZIP into D:\TESTUNREALPROJECT\
  pause
  exit /b 1
)

echo Close Unreal Editor before continuing.
pause

echo [1/5] Applying dependency-direction fix...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0PATCH_V013_DEPENDENCY_CYCLE.ps1"
if errorlevel 1 (
  echo.
  echo PATCH FAILED.
  pause
  exit /b 1
)

echo [2/5] Clearing InnerRealm generated products...
if exist "Plugins\InnerRealm\Binaries" rmdir /s /q "Plugins\InnerRealm\Binaries"
if exist "Plugins\InnerRealm\Intermediate" rmdir /s /q "Plugins\InnerRealm\Intermediate"

echo [3/5] Clearing SpellPreview generated products...
if exist "Plugins\SpellPreview\Binaries" rmdir /s /q "Plugins\SpellPreview\Binaries"
if exist "Plugins\SpellPreview\Intermediate" rmdir /s /q "Plugins\SpellPreview\Intermediate"

echo [4/5] Clearing project build-rule cache...
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [5/5] Opening project for Unreal rebuild...
start "" "TESTUNREALPROJECT.uproject"

echo.
echo Expected dependency direction after this fix:
echo   SpellPreview -^> InnerRealm
echo   PlayerViewModes -^> InnerRealm
echo   InnerRealm DOES NOT depend on SpellPreview
echo.
echo If build fails again, upload:
echo   %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
echo.
pause
endlocal
