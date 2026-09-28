@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS Gameplay v0.14.0
echo   Rune Canvas V1 / Semantic Spell Graph
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this ZIP into D:\TESTUNREALPROJECT\
  pause
  exit /b 1
)

if not exist "Plugins\WorldCodex\WorldCodex.uplugin" (
  echo ERROR: v0.13.5 Codex Grammar must already be installed.
  pause
  exit /b 1
)

if not exist "Plugins\SpellMotion\SpellMotion.uplugin" (
  echo ERROR: v0.13.5 Motion Direction must already be installed.
  pause
  exit /b 1
)

echo Close Unreal Editor before continuing.
pause

echo [1/5] Applying Rune Canvas integration...
py -3 "%~dp0PATCH_V014_0_RUNE_CANVAS.py"
if errorlevel 1 (
  echo.
  echo PATCH FAILED.
  echo Copy the patch error and send it to ChatGPT.
  pause
  exit /b 1
)

echo [2/5] Clearing affected generated products...
for %%D in (SpellGraph WorldCodex InnerRealm SpellPreview SpellCreation SpellPattern SpellMotion SpellLoadout LiveSpellCasting SpellExecution EarthMagic) do (
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
echo RUNE CANVAS V1 TEST
echo ============================================================
echo.
echo 1. TAB
echo 2. Choose RUNE CANVAS
echo 3. Click [E] Earth
echo 4. Select Earth in the graph
echo 5. Click Sphere
echo.
echo The graph should now become VALID and the existing 3D preview should
echo show the compiled Earth Sphere.
echo.
echo Try:
echo   Earth
echo     Sphere
echo       Sphere Radius
echo         Magnitude 4
echo     Speed
echo       Magnitude 3
echo     Amount
echo       Magnitude 2
echo     Circle
echo       Circle Radius
echo         Magnitude 3
echo       Instance Orientation
echo         Outward Orientation
echo     Motion Direction
echo       Outward
echo.
echo Then return to SPELL MODIFIER: the current values should reflect the
echo successfully compiled graph because both interfaces feed the same
echo FSpellDefinition foundation.
echo.
echo V1 NOTES:
echo   - Click-to-place, not free drag/drop yet.
echo   - One Tier-I root only.
echo   - Logic/world-reference Signs stay in CODEX until later compiler patches.
echo   - Stacking / multiple roots is next.
echo.
pause
endlocal
