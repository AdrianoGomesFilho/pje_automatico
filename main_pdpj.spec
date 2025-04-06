# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(
    ['main_pdpj.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('logowide.gif', '.'),  # Include logowide.gif
        ('initial_tab.html', '.'),  # Include initial_tab.html
        ('icon.ico', '.')  # Include icon.ico
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PJE automatico',  # Set the name of the executable
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Disable console
    icon='icon.ico',  # Set the icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PJE automatico',  # Set the name of the collected output
)