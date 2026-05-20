# PyInstaller spec for MindSphere
# Build with: pyinstaller installer/MindSphere.spec

import sys
from pathlib import Path

ROOT = Path(SPECPATH).parent.resolve()

a = Analysis(
    [str(ROOT / 'installer' / 'launcher.py')],
    pathex=[str(ROOT / 'backend')],
    binaries=[],
    datas=[
        (str(ROOT / 'backend'), 'backend'),
        (str(ROOT / 'frontend'), 'frontend'),
    ],
    hiddenimports=[
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastapi',
        'pydantic',
        'google.generativeai',
        'google.ai.generativelanguage',
        'webview',
        'webview.platforms.cocoa',
        'config',
        'database',
        'gemini_service',
        'main',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MindSphere',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # No terminal window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='MindSphere',
)

app = BUNDLE(
    coll,
    name='MindSphere.app',
    icon='/Users/vedantkasat/Desktop/mindsphere/installer/assets/icon.icns',
    bundle_identifier='com.vedantkasat.mindsphere',
    info_plist={
        'CFBundleName': 'MindSphere',
        'CFBundleDisplayName': 'MindSphere',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSBackgroundOnly': False,
    },
)
