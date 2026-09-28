@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS Gameplay v0.13.5
echo   Codex Grammar + Motion Direction
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this ZIP into D:\TESTUNREALPROJECT\
  pause
  exit /b 1
)

if not exist "Plugins\WorldCodex\WorldCodex.uplugin" (
  echo ERROR: v0.13.4.1 World Codex must already be installed.
  pause
  exit /b 1
)

echo Close Unreal Editor before continuing.
pause

echo [1/5] Applying v0.13.5 source patch...
py -3 "%~dp0PATCH_V013_5_CODEX_GRAMMAR_MOTION.py"
if errorlevel 1 (
  echo.
  echo PATCH FAILED. Copy the error text and send it to ChatGPT.
  pause
  exit /b 1
)

echo [2/5] Clearing affected generated products...
for %%D in (WorldCodex SpellCreation SpellMotion SpellPattern SpellExecution SpellPreview InnerRealm LiveSpellCasting SpellLoadout EarthMagic) do (
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
echo ============================================================
echo.
echo CODEX:
echo   - Entries show TIER I / II / III
echo   - VALUES category contains Magnitude 0 through 5
echo   - In Air is replaced by Airborne with precise state meaning
echo   - Motion Direction and direction values are documented
echo.
echo SPELL MODIFIER:
echo   - New DIRECTION / TRAVEL controls appear
echo.
echo BEST MOTION TEST:
echo   Earth / Cone
echo   Amount = 8
echo   Arrangement = Circle
echo   Speed greater than 0
echo.
echo   Orientation = Up + Direction = Outward
echo       objects FACE Up, but MOVE radially outward
echo.
echo   Orientation = Outward + Direction = Forward
echo       objects FACE outward, but MOVE together forward
echo.
echo   Direction = Inward
echo       all instances MOVE toward pattern center
echo.
echo   Direction = Tangent
echo       circle instances LAUNCH along their local tangent direction
echo.
echo NOTE:
echo   Outward/Inward/Tangent on a single centered object fall back to Forward.
echo.
pause
endlocal
