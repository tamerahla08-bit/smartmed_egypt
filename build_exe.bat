@echo off
cd /d "%~dp0"
pip install pyinstaller
pyinstaller --noconsole --onedir --name SmartMedEgypt --add-data "hospitals.db;." main.py
echo.
echo Done. Open the dist\SmartMedEgypt folder and run SmartMedEgypt.exe
pause
