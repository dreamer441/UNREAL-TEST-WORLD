@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "PROJECT_DIR=D:\TESTUNREALPROJECT"
set "HEADER=%PROJECT_DIR%\Plugins\AmadeusRuntime\Source\AmadeusRuntime\Private\AmadeusInteractionSubsystem.cpp"
set "UPROJECT=%PROJECT_DIR%\TESTUNREALPROJECT.uproject"

echo ============================================================
echo AMADEUS Runtime - Slate include compatibility fix
echo ============================================================
echo.

if not exist "%HEADER%" (
  echo ERROR: Could not find:
  echo %HEADER%
  pause
  exit /b 1
)

copy /y "%HEADER%" "%HEADER%.bak_before_slate_fix" >nul

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$p='%HEADER%';" ^
  "$s=[System.IO.File]::ReadAllText($p);" ^
  "$old='#include ""Widgets/Layout/SVerticalBox.h""';" ^
  "$new='#include ""Widgets/SBoxPanel.h""';" ^
  "if($s.Contains($old)){$s=$s.Replace($old,$new); [System.IO.File]::WriteAllText($p,$s,[System.Text.UTF8Encoding]::new($false)); Write-Host 'Patched SVerticalBox include.'} else {Write-Host 'Old include not found; file may already be patched.'}"

echo.
echo Cleaning only AmadeusRuntime generated build products...
if exist "%PROJECT_DIR%\Plugins\AmadeusRuntime\Binaries" rmdir /s /q "%PROJECT_DIR%\Plugins\AmadeusRuntime\Binaries"
if exist "%PROJECT_DIR%\Plugins\AmadeusRuntime\Intermediate" rmdir /s /q "%PROJECT_DIR%\Plugins\AmadeusRuntime\Intermediate"

echo.
echo Invalidating project build rules...
if exist "%PROJECT_DIR%\Intermediate\Build" rmdir /s /q "%PROJECT_DIR%\Intermediate\Build"

echo.
echo Opening Unreal project for bundled rebuild...
start "" "%UPROJECT%"

echo.
echo If Unreal asks to rebuild missing modules, choose YES.
echo If it fails again, send the newest:
echo %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
echo.
pause
endlocal
