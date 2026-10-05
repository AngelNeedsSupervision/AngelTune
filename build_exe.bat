@echo off
setlocal
title Build AngelTune
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher "py" was not found.
  echo Install Python for Windows first, then run this file again.
  pause
  exit /b 1
)

echo Installing/updating PyInstaller...
py -m pip install --upgrade pyinstaller
if errorlevel 1 (
  echo.
  echo PyInstaller installation failed.
  pause
  exit /b 1
)

echo.
echo Building AngelTune EXE...
py -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --add-data "assets;assets" ^
  --icon "assets\angeltune_icon.ico" ^
  --name AngelTune AngelTune.pyw

if errorlevel 1 (
  echo.
  echo Build failed.
  pause
  exit /b 1
)

echo.
echo Done.
echo EXE: dist\AngelTune.exe
pause
