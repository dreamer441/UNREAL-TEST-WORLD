@echo off
setlocal
cd /d "%~dp0"

echo ==============================================================
echo AMADEUS Runtime - UE 5.8 TickableWorldSubsystem include fix
echo ==============================================================
echo.

set "HEADER=%~dp0Plugins\AmadeusRuntime\Source\AmadeusRuntime\Public\AmadeusInteractionSubsystem.h"
set "UPROJECT=%~dp0TESTUNREALPROJECT.uproject"

if not exist "%HEADER%" (
  echo ERROR: Could not find:
  echo %HEADER%
  echo.
  echo Extract this patch into D:\TESTUNREALPROJECT\ and run it there.
  pause
  exit /b 1
)

if not exist "%UPROJECT%" (
  echo ERROR: Could not find TESTUNREALPROJECT.uproject beside this script.
  pause
  exit /b 1
)

echo [1/4] Backing up AmadeusInteractionSubsystem.h ...
copy /y "%HEADER%" "%HEADER%.pre_include_fix.bak" >nul

echo [2/4] Replacing obsolete/missing UE include ...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$p='%HEADER%'; $s=[IO.File]::ReadAllText($p); $old='#include \"Subsystems/TickableWorldSubsystem.h\"'; $new='#include \"Subsystems/WorldSubsystem.h\"'; if(-not $s.Contains($old)){ Write-Host 'Expected include was not found. No file changes made.' -ForegroundColor Yellow; exit 2 }; [IO.File]::WriteAllText($p,$s.Replace($old,$new)); Write-Host 'Patched:' $p"
if errorlevel 1 (
  echo.
  echo PATCH FAILED. Original header remains available as .pre_include_fix.bak
  pause
  exit /b 1
)

echo [3/4] Clearing AmadeusRuntime generated build products ...
if exist "%~dp0Plugins\AmadeusRuntime\Binaries" rmdir /s /q "%~dp0Plugins\AmadeusRuntime\Binaries"
if exist "%~dp0Plugins\AmadeusRuntime\Intermediate" rmdir /s /q "%~dp0Plugins\AmadeusRuntime\Intermediate"
if exist "%~dp0Intermediate\Build\BuildRules" rmdir /s /q "%~dp0Intermediate\Build\BuildRules"

echo [4/4] Opening project for Unreal's bundled rebuild ...
start "" "%UPROJECT%"

echo.
echo If Unreal asks to rebuild missing modules, choose YES.
echo If it fails again, upload %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt.
echo.
pause
endlocal
