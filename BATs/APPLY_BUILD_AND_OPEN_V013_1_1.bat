@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS Gameplay v0.13.1.1
echo   Ready Spell Slots + Orientation - FIXED PATCH
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this ZIP into D:\TESTUNREALPROJECT\
  pause
  exit /b 1
)

echo Close Unreal Editor before continuing.
pause

echo [1/6] Applying source patch with Python...
where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python launcher "py" was not found.
  echo Run manually with:
  echo   python PATCH_V013_1_1_READY_SLOTS_ORIENTATION.py
  pause
  exit /b 1
)

py -3 "%~dp0PATCH_V013_1_1_READY_SLOTS_ORIENTATION.py"
if errorlevel 1 (
  echo.
  echo PATCH FAILED. Copy the error text and send it to ChatGPT.
  pause
  exit /b 1
)

echo [2/6] Clearing affected plugin generated products...
for %%D in (SpellLoadout SpellCreation LiveSpellCasting SpellExecution InnerRealm SpellPreview SpellCastingBindings) do (
  if exist "Plugins\%%D\Binaries" rmdir /s /q "Plugins\%%D\Binaries"
  if exist "Plugins\%%D\Intermediate" rmdir /s /q "Plugins\%%D\Intermediate"
)

echo [3/6] Clearing project build-rule cache...
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [4/6] Building TESTUNREALPROJECTEditor with UE 5.8...
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
  echo Send the newest:
  echo   %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
  echo ============================================================
  pause
  exit /b 1
)

echo [5/6] BUILD SUCCEEDED.
echo [6/6] Opening Unreal...
start "" "%CD%\TESTUNREALPROJECT.uproject"

echo.
echo TEST:
echo   TAB:
echo     - 10 boxes 1..0 appear above right Workbench preview
echo     - click a box to save current spell; saved box shows *
echo     - Orientation shows Forward/X, Right/Y, Up/Z
echo.
echo   GAME:
echo     - press saved number to load prepared spell
echo     - press SPACE to cast
echo     - Forward cone points along cast direction
echo     - Up cone stays vertical/spike-like
echo.
pause
endlocal
