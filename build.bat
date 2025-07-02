@echo off
echo ================================================
echo PJE Automatico - Quick Build Script
echo ================================================
echo.

REM Change to script directory
cd /d "%~dp0"

echo Building executable...
echo.

REM Run the Python build script
python build.py

echo.
echo ================================================
echo Build process completed!
echo ================================================

pause
