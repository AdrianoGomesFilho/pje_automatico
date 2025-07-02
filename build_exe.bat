@echo off
echo ========================================
echo       PJE Automatico Build Script
echo ========================================
echo.

echo Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install Python dependencies
    pause
    exit /b 1
)

echo.
echo Checking for existing build directories...
if exist "build\" (
    echo Cleaning previous build directory...
    rmdir /s /q "build"
)
if exist "dist\" (
    echo Cleaning previous dist directory...
    rmdir /s /q "dist"
)

echo.
echo Building executable with PyInstaller...
echo This may take several minutes...
pyinstaller pje_automatico.spec --clean --noconfirm
if %errorlevel% neq 0 (
    echo Error: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo           Build Successful!
echo ========================================
echo.
echo The standalone executable has been created:
echo Location: dist\PJE_Automatico.exe
echo.
echo This executable includes all dependencies and can be run on any Windows PC
echo without requiring Python installation or additional setup.
echo.
echo IMPORTANT NOTES:
echo - Make sure Google Chrome is installed on the target PC
echo - The executable will automatically download ChromeDriver when needed
echo - No additional Python packages need to be installed on the target PC
echo.
pause
