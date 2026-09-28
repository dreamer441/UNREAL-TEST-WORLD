@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS Gameplay v0.13.1.0
echo   Ready Spell Slots + Orientation
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this ZIP into D:\TESTUNREALPROJECT\
  pause
  exit /b 1
)

echo Close Unreal Editor before continuing.
pause

echo [1/6] Applying current-branch source patch...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0PATCH_V013_READY_SLOTS_AND_ORIENTATION.ps1"
if errorlevel 1 (
  echo.
  echo PATCH FAILED.
  pause
  exit /b 1
)

echo [2/6] Clearing SpellLoadout generated products...
if exist "Plugins\SpellLoadout\Binaries" rmdir /s /q "Plugins\SpellLoadout\Binaries"
if exist "Plugins\SpellLoadout\Intermediate" rmdir /s /q "Plugins\SpellLoadout\Intermediate"

echo [3/6] Clearing affected plugin generated products...
for %%D in (InnerRealm EarthTestHarness LiveSpellCasting SpellPreview SpellCreation SpellExecution) do (
  if exist "Plugins\%%D\Binaries" rmdir /s /q "Plugins\%%D\Binaries"
  if exist "Plugins\%%D\Intermediate" rmdir /s /q "Plugins\%%D\Intermediate"
)

echo [4/6] Clearing project build-rule cache...
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [5/6] Building TESTUNREALPROJECTEditor with UE 5.8...
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

echo [6/6] BUILD SUCCEEDED.
echo Opening Unreal...
start "" "%CD%\TESTUNREALPROJECT.uproject"

echo.
echo Quick test:
echo   - TAB opens Workbench
echo   - right frame shows 1..0 slot buttons
echo   - clicking a slot saves the current spell
echo   - orientation row exists in the left editor
echo   - number key in gameplay loads a prepared spell
echo   - SPACE casts it
pause
endlocal
