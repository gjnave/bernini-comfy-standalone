@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\install.ps1" %*
if errorlevel 1 (
  echo.
  echo Install failed. See the messages above.
  pause
  exit /b 1
)
echo.
echo Install complete. Run run.bat to start Bernini ComfyUI.
pause
