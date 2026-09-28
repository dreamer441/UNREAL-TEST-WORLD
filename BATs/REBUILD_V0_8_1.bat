@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo  ProjectX / AMADEUS Gameplay v0.8.1 - Inner Realm floor fix
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Put this BAT beside TESTUNREALPROJECT.uproject.
  pause
  exit /b 1
)

echo Unreal Editor must be CLOSED before continuing.
echo.
pause

echo [1/2] Clearing generated InnerRealm build data...
if exist "Plugins\InnerRealm\Binaries" rmdir /s /q "Plugins\InnerRealm\Binaries"
if exist "Plugins\InnerRealm\Intermediate" rmdir /s /q "Plugins\InnerRealm\Intermediate"
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [2/2] Opening project...
echo If Unreal asks to rebuild missing modules, choose YES.
start "" "TESTUNREALPROJECT.uproject"

echo.
echo Patch behavior:
echo - Player pawn is frozen during meditation.
echo - Player transform is restored on exit.
echo - Inner Realm camera stays in the player's XY streaming region.
echo.
pause
