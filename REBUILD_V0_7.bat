@echo off
setlocal
cd /d "%~dp0"

echo =============================================
echo ProjectX / AMADEUS Foundation v0.7 rebuild
echo =============================================
echo.
echo Unreal Editor must be CLOSED before continuing.
echo.
pause

rem Remove obsolete v0.6 projectile files if they still exist in the real project.
del /q "Plugins\EarthTestHarness\Source\EarthTestHarness\Public\EarthTestProjectile.h" 2>nul
del /q "Plugins\EarthTestHarness\Source\EarthTestHarness\Private\EarthTestProjectile.cpp" 2>nul
del /q "Plugins\SpellCreation\Source\SpellCreation\Public\ProjectileSpellDefinition.h" 2>nul

rem Force changed runtime plugins to rebuild from current source.
for %%P in (SpellCreation EarthMagic EarthTestHarness) do (
  if exist "Plugins\%%P\Binaries" rmdir /s /q "Plugins\%%P\Binaries"
  if exist "Plugins\%%P\Intermediate" rmdir /s /q "Plugins\%%P\Intermediate"
)

rem Project generated metadata can cache module/plugin state.
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

set UBT=D:\UE_5.8\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe
if not exist "%UBT%" set UBT=D:\UE_5.8\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll

if exist "D:\UE_5.8\Engine\Build\BatchFiles\Build.bat" (
  echo Building TESTUNREALPROJECTEditor...
  call "D:\UE_5.8\Engine\Build\BatchFiles\Build.bat" TESTUNREALPROJECTEditor Win64 Development -Project="%CD%\TESTUNREALPROJECT.uproject" -WaitMutex -FromMsBuild
  if errorlevel 1 goto :buildfail
) else (
  echo Unreal Build.bat not found. Open TESTUNREALPROJECT.uproject and accept the rebuild prompt.
)

echo.
echo Build finished. Opening project...
start "" "%CD%\TESTUNREALPROJECT.uproject"
exit /b 0

:buildfail
echo.
echo BUILD FAILED.
echo Please send the compiler error or %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt.
pause
exit /b 1
