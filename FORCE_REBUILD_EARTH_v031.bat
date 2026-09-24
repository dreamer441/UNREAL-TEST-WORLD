@echo off
setlocal
cd /d "%~dp0"

echo =====================================================
echo AMADEUS Earth / MaterialInteraction - FORCE REBUILD
echo =====================================================
echo.

REM Do not delete build outputs while Unreal is running.
tasklist /FI "IMAGENAME eq UnrealEditor.exe" 2>NUL | find /I "UnrealEditor.exe" >NUL
if not errorlevel 1 (
  echo ERROR: Unreal Editor is still running.
  echo Close Unreal completely, then run this file again.
  echo.
  pause
  exit /b 1
)

for %%P in (MaterialInteraction EarthFoundation EarthTestHarness) do (
  if exist "Plugins\%%P\Binaries" (
    echo Removing Plugins\%%P\Binaries ...
    rmdir /S /Q "Plugins\%%P\Binaries"
  )
  if exist "Plugins\%%P\Intermediate" (
    echo Removing Plugins\%%P\Intermediate ...
    rmdir /S /Q "Plugins\%%P\Intermediate"
  )
)

REM Project-level generated outputs may contain stale module manifests.
if exist "Binaries" (
  echo Removing project Binaries ...
  rmdir /S /Q "Binaries"
)
if exist "Intermediate\Build" (
  echo Removing project Intermediate\Build ...
  rmdir /S /Q "Intermediate\Build"
)

echo.
echo Clean complete.
echo Unreal must now rebuild the C++ modules from the source you copied.
echo.

if exist "TESTUNREALPROJECT.uproject" (
  echo Opening TESTUNREALPROJECT.uproject ...
  start "" "TESTUNREALPROJECT.uproject"
) else (
  echo ERROR: TESTUNREALPROJECT.uproject was not found next to this BAT file.
  echo Put this BAT directly in D:\TESTUNREALPROJECT\ and run it there.
  pause
  exit /b 2
)

endlocal
