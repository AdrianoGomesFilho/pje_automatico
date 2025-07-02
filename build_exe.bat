@echo off
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Building executable with PyInstaller...
pyinstaller pje_automatico.spec --clean --noconfirm

echo.
echo Build complete!
echo The executable can be found in the 'dist' folder as 'PJE_Automatico.exe'
echo.
pause
