@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python 3 was not found. Install Python 3 and make sure the Python launcher is enabled.
  pause
  exit /b 1
)
py -3 install.py
if errorlevel 1 pause
