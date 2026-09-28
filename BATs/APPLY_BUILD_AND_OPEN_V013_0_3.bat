@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS v0.13.0.3 - Current Cleanup Branch Compatibility
echo   Base: codex/unreal-architecture-cleanup @ 960313b
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this ZIP into D:\TESTUNREALPROJECT\
  pause
  exit /b 1
)

if not exist "Plugins\SpellExecution\Source\SpellExecution\Public\SpellCastPlacement.h" (
  echo ERROR: This patch requires the current cleanup branch with SpellExecution.
  pause
  exit /b 1
)

echo Close Unreal Editor before continuing.
pause

echo [1/5] Applying generic FResolvedSpell placement compatibility fix...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0PATCH_V013_CURRENT_BRANCH_COMPAT.ps1"
if errorlevel 1 (
  echo.
  echo PATCH FAILED.
  pause
  exit /b 1
)

echo [2/5] Clearing affected SpellPreview build products...
if exist "Plugins\SpellPreview\Binaries" rmdir /s /q "Plugins\SpellPreview\Binaries"
if exist "Plugins\SpellPreview\Intermediate" rmdir /s /q "Plugins\SpellPreview\Intermediate"

echo [3/5] Clearing project build-rule cache...
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [4/5] Building TESTUNREALPROJECTEditor with UE 5.8...
if not exist "D:\UE_5.8\Engine\Build\BatchFiles\Build.bat" (
  echo ERROR: D:\UE_5.8\Engine\Build\BatchFiles\Build.bat not found.
  pause
  exit /b 1
)

call "D:\UE_5.8\Engine\Build\BatchFiles\Build.bat" TESTUNREALPROJECTEditor Win64 Development -Project="%CD%\TESTUNREALPROJECT.uproject" -WaitMutex -NoHotReloadFromIDE
if errorlevel 1 (
  echo.
  echo ============================================================
  echo BUILD FAILED
  echo Send me the newest:
  echo   %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
  echo ============================================================
  pause
  exit /b 1
)

echo [5/5] BUILD SUCCEEDED.
echo.
echo Opening Unreal...
start "" "%CD%\TESTUNREALPROJECT.uproject"

echo.
echo Test:
echo   1. TAB opens Workbench.
echo   2. Left-side existing controls still work.
echo   3. Right-side preview shows Manny plus stored spell.
echo   4. Shape / size / density / speed / distance update preview.
echo   5. Exit TAB and verify preview disappears.
echo   6. Top-down live spell construction still previews and casts normally.
echo.
pause
endlocal
