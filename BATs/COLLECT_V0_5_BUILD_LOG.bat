@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo ProjectX V0.5 - collect Unreal build log
echo ============================================================
echo.

set "SRC=%LOCALAPPDATA%\UnrealBuildTool\Log.txt"
set "DST=%~dp0V0_5_BUILD_LOG.txt"

if not exist "%SRC%" (
  echo ERROR: UnrealBuildTool log was not found at:
  echo %SRC%
  echo.
  echo Try opening TESTUNREALPROJECT.uproject once, let the compile fail,
  echo then run this file again.
  pause
  exit /b 1
)

copy /y "%SRC%" "%DST%" >nul
if errorlevel 1 (
  echo ERROR: Could not copy the log.
  pause
  exit /b 1
)

echo SUCCESS.
echo Created:
echo %DST%
echo.
echo Upload V0_5_BUILD_LOG.txt to ChatGPT.
explorer /select,"%DST%"
pause
