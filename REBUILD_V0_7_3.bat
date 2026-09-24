@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo  ProjectX / AMADEUS Gameplay v0.7.3 - EarthMagic link fix
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

echo [1/3] Clearing generated project build data...
if exist "Binaries" rmdir /s /q "Binaries"
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [2/3] Clearing generated plugin binaries/intermediates...
for %%P in (MaterialCore PhysicalBody ImpactSystem EarthFoundation EarthMagic EarthTestHarness SpellCreation) do (
  if exist "Plugins\%%P\Binaries" rmdir /s /q "Plugins\%%P\Binaries"
  if exist "Plugins\%%P\Intermediate" rmdir /s /q "Plugins\%%P\Intermediate"
)

echo [3/3] Opening project...
echo Unreal will rebuild using its bundled toolchain.
echo If asked to rebuild missing modules, choose YES.
start "" "TESTUNREALPROJECT.uproject"

echo.
echo If Unreal still reports a compiler error, send:
echo %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
pause
