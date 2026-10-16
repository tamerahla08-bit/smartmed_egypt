@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PY=
python --version >nul 2>nul && set PY=python
if not defined PY ( py --version >nul 2>nul && set PY=py )
if not defined PY (
  echo Python was not found. Install it from python.org and tick "Add Python to PATH".
  pause
  exit /b 1
)
start "" http://localhost:8000
%PY% run_web.py
if errorlevel 1 pause
