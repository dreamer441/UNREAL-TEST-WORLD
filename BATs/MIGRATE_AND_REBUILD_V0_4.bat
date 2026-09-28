@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo  ProjectX Foundation V0.4 - migrate and force rebuild
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Put this BAT beside TESTUNREALPROJECT.uproject.
  pause
  exit /b 1
)

echo [1/4] Removing superseded MaterialInteraction plugin...
if exist "Plugins\MaterialInteraction" rmdir /s /q "Plugins\MaterialInteraction"

echo [2/4] Removing obsolete deformation-era Earth source files...
del /q "Plugins\EarthFoundation\Source\EarthFoundation\Public\EarthDeformationComponent.h" 2>nul
del /q "Plugins\EarthFoundation\Source\EarthFoundation\Private\EarthDeformationComponent.cpp" 2>nul
del /q "Plugins\EarthFoundation\Source\EarthFoundation\Public\EarthDeformationTypes.h" 2>nul
del /q "Plugins\EarthFoundation\Source\EarthFoundation\Public\EarthImpactProvider.h" 2>nul
del /q "Plugins\EarthFoundation\Source\EarthFoundation\Public\EarthImpactResponseComponent.h" 2>nul
del /q "Plugins\EarthFoundation\Source\EarthFoundation\Private\EarthImpactResponseComponent.cpp" 2>nul

echo [3/4] Clearing generated plugin binaries/intermediates...
for %%P in (MaterialCore ImpactSystem EarthFoundation EarthTestHarness) do (
  if exist "Plugins\%%P\Binaries" rmdir /s /q "Plugins\%%P\Binaries"
  if exist "Plugins\%%P\Intermediate" rmdir /s /q "Plugins\%%P\Intermediate"
)

echo [4/4] Opening the project. Accept the Unreal rebuild prompt.
start "" "TESTUNREALPROJECT.uproject"

echo.
echo Migration complete. If compilation fails, send the first compiler error block.
pause
