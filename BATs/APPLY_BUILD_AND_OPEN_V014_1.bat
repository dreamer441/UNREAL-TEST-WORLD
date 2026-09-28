@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS Gameplay v0.14.1
echo   Rune Graph Redesign + Ready Slot Input Fix
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this ZIP into D:\TESTUNREALPROJECT\
  pause
  exit /b 1
)

if not exist "Plugins\SpellGraph\SpellGraph.uplugin" (
  echo ERROR: v0.14.0 Rune Canvas must already be installed.
  pause
  exit /b 1
)

echo Close Unreal Editor before continuing.
pause

echo [1/4] Applying graph redesign...
py -3 "%~dp0PATCH_V014_1_RUNE_GRAPH_REDESIGN.py"
if errorlevel 1 (
  echo.
  echo PATCH FAILED. Copy the error text and send it to ChatGPT.
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
echo TEST
echo ============================================================
echo.
echo READY SPELL:
echo   - Build/compile a Rune Canvas spell.
echo   - Click a ready slot above the preview to save it.
echo   - Leave TAB, press that number, verify the prepared spell loads.
echo.
echo GRAPH:
echo   - Graph nodes show SIGNS ONLY.
echo   - Click Earth.
echo   - Earth has a downward line and an empty child socket.
echo   - Click the empty socket, then choose Sphere from palette.
echo   - Earth now branches to Sphere and keeps another empty socket.
echo   - Sphere also gets its own outgoing socket.
echo   - Tier III values have NO outgoing socket.
echo.
pause
endlocal
