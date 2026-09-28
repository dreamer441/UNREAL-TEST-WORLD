@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS Gameplay v0.13.2.1
echo   Slate Visibility Compile Fix
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this ZIP into D:\TESTUNREALPROJECT\
  pause
  exit /b 1
)

echo Close Unreal Editor before continuing.
pause

echo [1/4] Fixing MULTIPLE OBJECTS Slate visibility...
py -3 "%~dp0PATCH_V013_2_1_SLATE_VISIBILITY.py"
if errorlevel 1 (
  echo.
  echo PATCH FAILED.
  pause
  exit /b 1
)

echo [2/4] Clearing InnerRealm generated products...
if exist "Plugins\InnerRealm\Binaries" rmdir /s /q "Plugins\InnerRealm\Binaries"
if exist "Plugins\InnerRealm\Intermediate" rmdir /s /q "Plugins\InnerRealm\Intermediate"
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [3/4] Building TESTUNREALPROJECTEditor...
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

echo [4/4] BUILD SUCCEEDED. Opening Unreal...
start "" "%CD%\TESTUNREALPROJECT.uproject"

echo.
echo Test:
echo   Amount 1  = pattern options hidden
echo   Amount 2+ = Line/Circle appears
echo   Line      = Axis + Spacing appears
echo   Circle    = Radius appears
echo.
pause
endlocal
