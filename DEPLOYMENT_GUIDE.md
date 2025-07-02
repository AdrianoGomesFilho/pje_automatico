# PJE Automático - Deployment Guide

## Creating the Standalone Executable

Follow these steps to create a standalone executable that can run on any Windows PC without requiring Python installation or additional configuration.

### Prerequisites

1. **Python 3.8 or higher** installed on the build machine
2. **Google Chrome** installed (for testing)
3. **Internet connection** (for downloading dependencies)

### Build Process

1. **Run the build script:**
   ```cmd
   build_exe.bat
   ```

2. **Wait for completion:**
   - The script will install all dependencies
   - PyInstaller will create the executable
   - This process may take 5-10 minutes

3. **Find the executable:**
   - Location: `dist\PJE_Automatico.exe`
   - Size: Approximately 200-300 MB (includes all dependencies)

### What's Included in the Executable

The standalone executable includes:
- ✅ Python runtime environment
- ✅ All required Python packages
- ✅ Selenium WebDriver components
- ✅ Automatic ChromeDriver management
- ✅ Application icons and assets
- ✅ All tribunal handlers
- ✅ Cryptography libraries
- ✅ GUI frameworks (tkinter, pystray)
- ✅ Notification systems

### Deployment to Target PC

#### Requirements on Target PC:
- **Windows 10/11** (64-bit recommended)
- **Google Chrome browser** (latest version)
- **Internet connection** (for initial ChromeDriver download)

#### Installation Steps:
1. Copy `PJE_Automatico.exe` to the target PC
2. Place it in any folder (e.g., `C:\PJE_Automatico\`)
3. Double-click to run - no installation required!

#### First Run:
- The application will automatically download ChromeDriver if needed
- This happens only once and requires internet connection
- Subsequent runs work offline (except for PJE website access)

### Features of the Standalone Version

#### Self-Contained:
- No Python installation required
- No pip install commands needed
- No dependency management
- No configuration files to setup

#### Automatic Driver Management:
- ChromeDriver is downloaded automatically
- Always uses compatible version with installed Chrome
- Handles driver updates transparently

#### Portable:
- Single executable file
- Can be run from USB drive
- No registry modifications
- No system-wide installations

### Troubleshooting

#### Common Issues:

1. **"Failed to execute script" error:**
   - Ensure Google Chrome is installed
   - Check internet connection for first run
   - Run as administrator if needed

2. **Antivirus blocking:**
   - Some antivirus may flag the executable
   - Add to antivirus whitelist
   - This is common with PyInstaller executables

3. **Chrome version issues:**
   - Update Google Chrome to latest version
   - Delete downloaded ChromeDriver cache
   - Restart the application

#### Debug Mode:
To enable console output for debugging:
- Edit `pje_automatico.spec`
- Change `console=False` to `console=True`
- Rebuild the executable

### Distribution

#### File Sharing:
- The executable can be shared via:
  - Email (if size permits)
  - Cloud storage (Google Drive, OneDrive)
  - Network file sharing
  - USB drives

#### Version Updates:
- Replace old executable with new version
- User settings and data are preserved
- No uninstall/reinstall required

### Security Considerations

- The executable is digitally unsigned
- Windows may show "Unknown publisher" warning
- Users can click "More info" → "Run anyway"
- Consider code signing for production distribution

### Performance Notes

- **Startup time:** 10-15 seconds (first run may be longer)
- **Memory usage:** 150-300 MB RAM
- **Disk space:** 200-300 MB
- **Network:** Minimal (only for PJE access and updates)

---

## Build Configuration Details

The build is configured for maximum compatibility:

- **One-file distribution:** Everything in single .exe
- **UPX compression:** Reduces file size
- **Windows GUI mode:** No console window
- **Embedded resources:** Icons and assets included
- **Hidden imports:** All required modules explicitly listed

This ensures the executable runs reliably across different Windows systems without requiring any additional setup or configuration.
