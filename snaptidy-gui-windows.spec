# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('logo.png', '.'),
        ('README.md', '.'),
        ('README-ko.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'snaptidy.snaptidy.cli',
        'snaptidy.snaptidy.flatten',
        'snaptidy.snaptidy.dedup',
        'snaptidy.snaptidy.organize',
        'snaptidy.snaptidy.utils',
        'gui.widgets.folder_selector',
        'gui.widgets.progress_widget',
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
    name='snaptidy-gui.exe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo.png',
)
