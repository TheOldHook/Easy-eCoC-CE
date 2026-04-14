# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

# Platform-specific icon configuration
icon_file = None
if sys.platform == 'win32':
    icon_file = 'img/Icon.ico'
elif sys.platform == 'darwin':
    icon_file = 'img/Icon.icns' if os.path.exists('img/Icon.icns') else None

a = Analysis(
    ['ecoc-gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('img/Icon.png', 'img'),
        ('img/Icon.ico', 'img'),
    ],
    hiddenimports=[
        'ecoc_service',
        'samarbeidsportalen',
        'pubkeygen',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Easy-eCoC',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI app (no console window)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)
