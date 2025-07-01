# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Common analysis for both CLI and GUI
common_analysis = Analysis(
    [],
    pathex=[],
    binaries=[],
    datas=[
        ('logo.png', '.'),
        ('README.md', '.'),
        ('README-ko.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'core.cli',
        'core.gui',
        'core.flatten',
        'core.dedup',
        'core.organize',
        'core.utils',
        'gui.widgets.folder_selector',
        'gui.widgets.progress_widget',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
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

pyz = PYZ(common_analysis.pure, common_analysis.zipped_data, cipher=block_cipher)

# CLI executable
cli_exe = EXE(
    pyz,
    common_analysis.scripts,
    [],
    exclude_binaries=True,
    name='snaptidy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo.png',
)

# GUI executable
gui_exe = EXE(
    pyz,
    [],
    common_analysis.binaries,
    common_analysis.zipfiles,
    common_analysis.datas,
    [],
    name='snaptidy-gui',
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
