@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS Gameplay v0.13 - Spell Workbench V1
echo   Shared 3D spell preview + player reference
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this ZIP into the TESTUNREALPROJECT root.
  pause
  exit /b 1
)

if not exist "PATCH_WORKBENCH_V1.ps1" (
  echo ERROR: PATCH_WORKBENCH_V1.ps1 is missing.
  pause
  exit /b 1
)

echo Close Unreal Editor before continuing.
pause

echo [1/5] Integrating Workbench hooks into InnerRealmSubsystem...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0PATCH_WORKBENCH_V1.ps1"
if errorlevel 1 (
  echo.
  echo PATCH FAILED. No rebuild was started.
  pause
  exit /b 1
)

echo [2/5] Clearing InnerRealm generated build products...
if exist "Plugins\InnerRealm\Binaries" rmdir /s /q "Plugins\InnerRealm\Binaries"
if exist "Plugins\InnerRealm\Intermediate" rmdir /s /q "Plugins\InnerRealm\Intermediate"

echo [3/5] Clearing SpellPreview generated build products...
if exist "Plugins\SpellPreview\Binaries" rmdir /s /q "Plugins\SpellPreview\Binaries"
if exist "Plugins\SpellPreview\Intermediate" rmdir /s /q "Plugins\SpellPreview\Intermediate"

echo [4/5] Clearing generated project build rules...
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [5/5] Opening project for Unreal's bundled rebuild...
echo If Unreal asks to rebuild missing modules, choose YES.
start "" "TESTUNREALPROJECT.uproject"

echo.
echo Expected Patch 1 behavior:
echo   TAB opens the existing editor on the LEFT.
echo   A new SPELL WORKBENCH / 3D PREVIEW frame appears on the RIGHT.
echo   Manny is visible as a size / placement reference.
echo   The persistent stored spell is visible next to Manny.
echo   Shape sliders update the preview live.
echo   Density changes grid density.
echo   Stored speed shows 0 / 1 / 2 / 3 rings.
echo   Distance moves the preview relative to Manny (visual distance clamps after 5m).
echo   Live top-down casting preview should remain unchanged.
echo.
echo If build fails, upload:
echo   %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
echo.
pause
endlocal
