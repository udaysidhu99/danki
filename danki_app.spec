# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['danki_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('dictionary/german_english_dict_20k.json', 'dictionary'),
        ('Danki Template Deck.apkg', '.'),
        ('githubstar_banner.png', '.'),
        ('icon.ico', '.'),
    ],
    hiddenimports=['edge_tts', 'asyncio'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='danki_app',
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
    icon=['icon.ico'],
)
