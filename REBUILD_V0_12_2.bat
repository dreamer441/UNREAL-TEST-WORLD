@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS v0.12.2 - density grid + speed rings
echo ============================================================
echo.
if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this patch into the project root alongside TESTUNREALPROJECT.uproject.
  pause
  exit /b 1
)
if not exist "Plugins\SpellPreview\Source\SpellPreview\Private\SpellPreviewSubsystem.cpp" (
  echo ERROR: SpellPreview patch file was not merged correctly.
  pause
  exit /b 1
)

echo Close Unreal Editor and any running game instances before continuing.
pause

echo [1/3] Clearing SpellPreview generated build products...
if exist "Plugins\SpellPreview\Binaries" rmdir /s /q "Plugins\SpellPreview\Binaries"
if exist "Plugins\SpellPreview\Intermediate" rmdir /s /q "Plugins\SpellPreview\Intermediate"

echo [2/3] Clearing generated project build rules...
if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [3/3] Opening project for Unreal's bundled rebuild...
echo If prompted to rebuild missing modules, select YES.
start "" "TESTUNREALPROJECT.uproject"

echo.
echo Visual check:
echo   - low density = sparse construction grid
 echo   - high density = visibly denser construction grid
 echo   - speed 0 = no rings
 echo   - low/medium/high speed = 1/2/3 ring bands
 echo.
echo If build fails, upload: %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
pause
