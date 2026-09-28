@echo off
setlocal
set "SRC=%LOCALAPPDATA%\UnrealBuildTool\Log.txt"
set "DST=%~dp0V0_7_BUILD_LOG.txt"
echo ===============================================
echo ProjectX / AMADEUS Gameplay v0.7 log collector
echo ===============================================
echo.
if not exist "%SRC%" (
  echo Could not find:
  echo %SRC%
  echo.
  pause
  exit /b 1
)
copy /Y "%SRC%" "%DST%" >nul
if errorlevel 1 (
  echo Failed to copy the build log.
  pause
  exit /b 1
)
echo Created:
echo %DST%
echo.
echo Upload V0_7_BUILD_LOG.txt to ChatGPT.
pause
