# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pje_automatico.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icon.ico', '.'), 
        ('logowide.png', '.'),  # Include logowide.png
        ('initial_tab.html', '.'),  # Include initial_tab.html
        ('logowide.gif', '.'),  # Include your GIF file
    ],
    hiddenimports=[
        'tkinter',  # Ensure tkinter is included
        'PIL._imagingtk',  # Include PIL's tkinter support
        'pystray._win32',  # Include pystray for Windows
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pje_automatico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Prevent console window from opening
)
