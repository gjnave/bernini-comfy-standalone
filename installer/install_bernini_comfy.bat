@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

set "REPO_URL=https://github.com/gjnave/bernini-comfy-standalone.git"
set "APP_DIR=%~dp0bernini-comfy-standalone"

echo Bernini ComfyUI standalone installer
echo.

where git >nul 2>&1
if errorlevel 1 (
  echo ERROR: Git is required.
  echo Install Git for Windows, then run this installer again:
  echo https://git-scm.com/download/win
  pause
  exit /b 1
)

where py >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python Launcher for Windows is required.
  echo Install Python 3.10 from python.org and make sure "py" is available.
  pause
  exit /b 1
)

if exist "%APP_DIR%\.git" (
  echo Updating existing repo...
  git -C "%APP_DIR%" pull --ff-only
) else (
  echo Cloning Bernini standalone repo...
  git clone "%REPO_URL%" "%APP_DIR%"
)

if errorlevel 1 (
  echo.
  echo ERROR: Could not clone or update the repo.
  pause
  exit /b 1
)

cd /d "%APP_DIR%"
call install.bat
