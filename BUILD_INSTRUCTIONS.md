# PJE Automático - Executable Build Instructions

This guide will help you create a standalone executable (.exe) file that can be run on any Windows computer without requiring Python installation.

## Prerequisites

1. **Python 3.7+** must be installed on the build machine
2. **Google Chrome** must be installed (required by the application)

## Building the Executable

### Option 1: Automatic Build (Recommended)
1. Open Command Prompt or PowerShell as Administrator
2. Navigate to the project folder: `cd path\to\pje_automatico`
3. Run the build script: `build_exe.bat`
4. Wait for the build process to complete
5. The executable will be created in the `dist` folder as `PJE_Automatico.exe`

### Option 2: Manual Build
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Build the executable:
   ```bash
   pyinstaller pje_automatico.spec --clean --noconfirm
   ```

3. The executable will be in the `dist` folder

## Distribution

The created `PJE_Automatico.exe` file is completely standalone and can be:
- Copied to any Windows computer
- Run without installing Python or any dependencies
- Distributed via USB drive, email, or network share

## File Size

The executable will be approximately 150-200 MB due to:
- Embedded Python interpreter
- All required libraries (Selenium, Tkinter, PIL, etc.)
- Chrome WebDriver dependencies

## Requirements for End Users

**The target computer only needs:**
1. **Windows 7/10/11** (64-bit recommended)
2. **Google Chrome browser** installed
3. **Internet connection** for PJE and Astrea access

**No other installations required!**

## Troubleshooting

### Build Issues
- **"Module not found" errors**: Make sure all dependencies in `requirements.txt` are installed
- **Permission errors**: Run Command Prompt as Administrator
- **Antivirus blocking**: Temporarily disable antivirus during build

### Runtime Issues
- **"Chrome not found"**: Install Google Chrome on the target computer
- **Firewall blocking**: Allow the application through Windows Firewall
- **Missing Visual C++ redistributables**: Install Microsoft Visual C++ Redistributable

## Technical Details

- **Build tool**: PyInstaller
- **Bundle type**: One-file executable
- **Console**: Hidden (GUI application)
- **Icon**: Custom icon.ico included
- **UPX compression**: Enabled for smaller file size

## Security Note

Some antivirus software may flag PyInstaller executables as suspicious. This is a false positive common with Python executables. The application is safe and the source code is open for inspection.
