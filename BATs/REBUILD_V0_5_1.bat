@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo  ProjectX Foundation V0.5.1 - UHT units fix / force rebuild
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Put this BAT beside TESTUNREALPROJECT.uproject.
  pause
  exit /b 1
)

echo [1/2] Clearing generated plugin binaries/intermediates...
for %%P in (MaterialCore PhysicalBody ImpactSystem EarthFoundation EarthTestHarness) do (
  if exist "Plugins\%%P\Binaries" rmdir /s /q "Plugins\%%P\Binaries"
  if exist "Plugins\%%P\Intermediate" rmdir /s /q "Plugins\%%P\Intermediate"
)

if exist "Binaries" rmdir /s /q "Binaries"
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [2/2] Opening project. Accept Unreal's rebuild prompt.
start "" "TESTUNREALPROJECT.uproject"

echo.
echo V0.5.1 patch installed.
echo Fix: removed unsupported UHT Units metadata for density and volume.
echo If Unreal reports another compile error, send:
echo %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
pause
