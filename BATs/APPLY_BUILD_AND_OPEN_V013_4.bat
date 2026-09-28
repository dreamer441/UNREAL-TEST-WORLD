@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AMADEUS Gameplay v0.13.4
echo   World Codex + Sign Vocabulary + TAB Navigation
echo ============================================================
echo.

if not exist "TESTUNREALPROJECT.uproject" (
  echo ERROR: Extract this ZIP into D:\TESTUNREALPROJECT\
  pause
  exit /b 1
)

if not exist "Plugins\SpellPattern\SpellPattern.uplugin" (
  echo ERROR: v0.13.3 must be installed and working first.
  pause
  exit /b 1
)

echo Close Unreal Editor before continuing.
pause

echo [1/6] Applying v0.13.4 source patch...
py -3 "%~dp0PATCH_V013_4_WORLD_CODEX.py"
if errorlevel 1 (
  echo.
  echo PATCH FAILED. Copy the error text and send it to ChatGPT.
  pause
  exit /b 1
)

echo [2/6] Clearing affected generated products...
for %%D in (WorldCodex InnerRealm SpellPreview) do (
  if exist "Plugins\%%D\Binaries" rmdir /s /q "Plugins\%%D\Binaries"
  if exist "Plugins\%%D\Intermediate" rmdir /s /q "Plugins\%%D\Intermediate"
)

if exist "Intermediate\Build" rmdir /s /q "Intermediate\Build"

echo [3/6] Building TESTUNREALPROJECTEditor with UE 5.8...
if not exist "D:\UE_5.8\Engine\Build\BatchFiles\Build.bat" (
  echo ERROR: D:\UE_5.8\Engine\Build\BatchFiles\Build.bat not found.
  pause
  exit /b 1
)

call "D:\UE_5.8\Engine\Build\BatchFiles\Build.bat" TESTUNREALPROJECTEditor Win64 Development -Project="%CD%\TESTUNREALPROJECT.uproject" -WaitMutex -NoHotReloadFromIDE
if errorlevel 1 (
  echo.
  echo ============================================================
  echo BUILD FAILED
  echo Send the newest:
  echo   %%LOCALAPPDATA%%\UnrealBuildTool\Log.txt
  echo ============================================================
  pause
  exit /b 1
)

echo [4/6] BUILD SUCCEEDED.
echo [5/6] Opening Unreal...
start "" "%CD%\TESTUNREALPROJECT.uproject"
echo [6/6] Ready.

echo.
echo TEST CHECKLIST:
echo   TAB opens the same Meditation Realm.
echo   Top buttons: SPELL MODIFIER / CODEX / CANVAS-LATER.
echo   SPELL MODIFIER preserves the current editor and 3D preview.
echo   CODEX replaces the editor/preview with the Codex browser.
echo   Selecting entries updates Sign, ID, description, capabilities and relations.
echo   CANVAS-LATER shows the reserved v0.14 page.
echo   Returning to SPELL MODIFIER restores the current spell editor.
echo.
echo IMPORTANT:
echo   This patch does not change spell execution or Earth physics.
echo.
pause
endlocal
