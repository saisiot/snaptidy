# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['snaptidy/snaptidy/cli.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('README.md', '.'),
        ('README-ko.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'snaptidy.snaptidy.cli',
        'snaptidy.snaptidy.flatten',
        'snaptidy.snaptidy.dedup',
        'snaptidy.snaptidy.organize',
        'snaptidy.snaptidy.utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt6', 'PySide6', 'tkinter', 'wx'],
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
    name='snaptidy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo.png',
) 