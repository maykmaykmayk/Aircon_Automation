@echo off
setlocal

REM Build Aircon Calculator executable for Windows
pyinstaller --onefile --console --name aircon-calculator main.py

echo.
echo Build complete. Check the dist folder for aircon-calculator.exe

