@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS Gameplay v0.15.0
echo   Architecture Cleanup Phase 1
echo   Shared InnerRealm Shell + SpellGraph Compiler Boundary
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this ZIP into D:\TESTUNREALPROJECT\
  pause
  exit /b 1
)

if not exist "Plugins\SpellGraph\SpellGraph.uplugin" (
  echo ERROR: v0.14.x Rune Canvas snapshot is required.
  pause
  exit /b 1
)

for /f %%i in ('git rev-parse --short HEAD 2^>nul') do set HEADSHA=%%i
echo Current git HEAD: %HEADSHA%
echo Expected baseline: 58acd09

echo.
echo Close Unreal Editor before continuing.
pause

echo [1/5] Applying architecture cleanup...
py -3 "%~dp0PATCH_V015_0_ARCHITECTURE_CLEANUP.py"
if errorlevel 1 (
  echo.
  echo PATCH FAILED.
  echo Send the patch error text to ChatGPT.
  pause
  exit /b 1
)

echo [2/5] Clearing affected generated products...
for %%D in (InnerRealm SpellGraph SpellPreview SpellLoadout) do (
  if exist "Plugins\%%D\Binaries" rmdir /s /q "Plugins\%%D\Binaries"
  if exist "Plugins\%%D\Intermediate" rmdir /s /q "Plugins\%%D\Intermediate"
)
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [3/5] Building TESTUNREALPROJECTEditor with UE 5.8...
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
  echo Send the FIRST meaningful compiler error, or:
  echo   %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
  echo ============================================================
  pause
  exit /b 1
)

echo [4/5] BUILD SUCCEEDED.
echo [5/5] Opening Unreal...
start "" "%CD%\TESTUNREALPROJECT.uproject"

echo.
echo ============================================================
echo TEST CHECKLIST
ECHO ============================================================
echo.
echo SHARED READY-SPELL BAR:
echo   - TAB opens InnerRealm.
echo   - [1]...[0] are now in the shared top shell.
echo   - They stay clickable on SPELL MODIFIER, CODEX and RUNE CANVAS.
echo   - Save from SPELL MODIFIER, then leave TAB and press the number key.
echo   - Save from RUNE CANVAS, then leave TAB and press the number key.
echo.
echo PAGE NAVIGATION:
echo   - SPELL MODIFIER / CODEX / RUNE CANVAS still switch normally.
echo.
echo SPELL GRAPH:
echo   - Existing graph behavior should be unchanged.
echo   - Compile/apply should still update the canonical spell definition.
echo.
echo ARCHITECTURE:
echo   - Docs\ARCHITECTURE_V1.md records the new source-of-truth layout.
echo.
pause
endlocal
