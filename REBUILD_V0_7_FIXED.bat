@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo ProjectX / AMADEUS Gameplay v0.7 - fixed rebuild
echo ============================================================
echo.
echo Unreal Editor must be CLOSED before continuing.
echo.
pause

set "UPROJECT=%CD%\TESTUNREALPROJECT.uproject"
set "UE_ROOT=D:\UE_5.8"
set "UBT=%UE_ROOT%\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll"

if not exist "%UPROJECT%" (
  echo ERROR: Could not find %UPROJECT%
  pause
  exit /b 1
)

if not exist "%UBT%" (
  echo ERROR: Could not find UnrealBuildTool at:
  echo %UBT%
  pause
  exit /b 1
)

echo Cleaning project/plugin generated build data...
if exist "%CD%\Binaries" rmdir /s /q "%CD%\Binaries"
if exist "%CD%\Intermediate" rmdir /s /q "%CD%\Intermediate"

for %%P in (MaterialCore PhysicalBody ImpactSystem EarthFoundation EarthMagic EarthTestHarness SpellCreation) do (
  if exist "%CD%\Plugins\%%P\Binaries" rmdir /s /q "%CD%\Plugins\%%P\Binaries"
  if exist "%CD%\Plugins\%%P\Intermediate" rmdir /s /q "%CD%\Plugins\%%P\Intermediate"
)

echo.
echo Building project plugins using an Editor target type...
dotnet "%UBT%" Development Win64 -Project="%UPROJECT%" -TargetType=Editor -Progress -NoEngineChanges -NoHotReloadFromIDE
set "ERR=%ERRORLEVEL%"

echo.
if not "%ERR%"=="0" (
  echo BUILD FAILED with code %ERR%.
  echo Please send: %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
  pause
  exit /b %ERR%
)

echo BUILD SUCCEEDED.
echo Opening project...
start "" "%UPROJECT%"
exit /b 0
