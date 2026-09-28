@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS Gameplay v0.14.2
echo   Radial Rune Canvas + Spell Modifier Ready-Slot Fix
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this ZIP into D:\TESTUNREALPROJECT\
  pause
  exit /b 1
)

if not exist "Plugins\SpellGraph\SpellGraph.uplugin" (
  echo ERROR: Rune Canvas V1 must already be installed.
  pause
  exit /b 1
)

echo Close Unreal Editor before continuing.
pause

echo [1/4] Applying v0.14.2...
py -3 "%~dp0PATCH_V014_2_RADIAL_CANVAS.py"
if errorlevel 1 (
  echo.
  echo PATCH FAILED. Copy the patch error and send it to ChatGPT.
  pause
  exit /b 1
)

echo [2/4] Clearing affected generated products...
if exist "Plugins\InnerRealm\Binaries" rmdir /s /q "Plugins\InnerRealm\Binaries"
if exist "Plugins\InnerRealm\Intermediate" rmdir /s /q "Plugins\InnerRealm\Intermediate"
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [3/4] Building TESTUNREALPROJECTEditor...
call "D:\UE_5.8\Engine\Build\BatchFiles\Build.bat" TESTUNREALPROJECTEditor Win64 Development -Project="%CD%\TESTUNREALPROJECT.uproject" -WaitMutex -NoHotReloadFromIDE
if errorlevel 1 (
  echo.
  echo ============================================================
  echo BUILD FAILED
  echo Send the FIRST meaningful compiler error or:
  echo   %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
  echo ============================================================
  pause
  exit /b 1
)

echo [4/4] BUILD SUCCEEDED. Opening Unreal...
start "" "%CD%\TESTUNREALPROJECT.uproject"

echo.
echo ============================================================
echo TEST 1 - SPELL MODIFIER READY SLOT
echo ============================================================
echo.
echo TAB -^> SPELL MODIFIER
echo Change/build the current spell.
echo Click one of the ready-spell number slots above the preview.
echo The slot should respond again.
echo.
echo ============================================================
echo TEST 2 - RADIAL RUNE CANVAS
echo ============================================================
echo.
echo TAB -^> RUNE CANVAS
echo 1. Click Earth.
echo 2. Click Cube.
echo    Graph should create ONE central [Earth + Cube] sign node.
echo 3. DOUBLE CLICK that node.
echo    First empty branch appears DOWN.
echo 4. Choose Speed.
echo    Speed appears on that branch and another empty branch remains.
echo 5. Add another modifier: next branch goes UP, then LEFT, RIGHT,
echo    then diagonal/in-between directions.
echo 6. DOUBLE CLICK Speed.
echo    Speed gets its own free radial branch, avoiding the incoming line.
echo 7. Attach Magnitude 3.
echo    Tier III value has no outgoing line.
echo.
pause
endlocal
