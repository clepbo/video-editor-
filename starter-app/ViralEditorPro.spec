# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for ViralEditorPro - optimized for size and compatibility

block_cipher = None

a = Analysis(
    ['viral_editor_pro.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Add any data files if needed
    ],
    hiddenimports=[
        'customtkinter',
        'faster_whisper',
        'sentence_transformers',
        'sklearn',
        'sklearn.metrics.pairwise',
        'sklearn.utils._typedefs',
        'ultralytics',
        'cv2',
        'PIL',
        'numpy',
        'scipy',
        'scipy.special',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'notebook',
        'jupyter',
    ],
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
    name='ViralEditorPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed, no console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
