@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo  ProjectX Foundation V0.5 - physical body / motion rebuild
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

echo [2/2] Opening project. Accept Unreal's rebuild prompt.
start "" "TESTUNREALPROJECT.uproject"

echo.
echo V0.5 installed.
echo New architecture: MaterialCore - PhysicalBody - ImpactSystem - EarthFoundation.
echo Gravity is enabled for the test projectile and ImpactSystem now returns post-impact motion/impulse.
echo If Unreal reports a compile error, send:
echo %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
pause
