# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['launcher_mock.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('frontend_dist_mock', 'frontend/dist'),
        ('mock_server.py', '.'),
    ],
    hiddenimports=[
        'flask',
        'flask_cors',
        'jinja2',
        'markupsafe',
        'werkzeug',
        'click',
        'itsdangerous',
        'blinker',
        'math',
        'random',
        'datetime',
        'urllib',
        'urllib.request',
        'mock_server'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.packages)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='KeithleyController_MOCK',
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
    icon=None
)