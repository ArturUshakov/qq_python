# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = [
    'tqdm',
]

# Сбор данных для tqdm (если используется)
tmp_ret = collect_all('tqdm')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# Анализ скрипта
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'multiprocessing',  # Если не используется, исключите
        'pyimod02_importers',  # Используется только в PyInstaller, можно исключить
        'cryptography',  # Если не используется шифрование, можно исключить
        'OpenSSL',  # Если не используется SSL, можно исключить
        'tqdm.contrib.discord',  # Если не используется интеграция с Discord
        'tqdm.contrib.slack',  # Если не используется интеграция с Slack
        'tqdm.keras',  # Если не используется Keras
        'dask',  # Если не используется Dask
        'matplotlib',  # Если не используется Matplotlib
        'IPython',  # Если не используется IPython
        'tensorflow',  # Если не используется TensorFlow
        'socks',  # Если не используется прокси через SOCKS
        'simplejson',  # Если не используется SimpleJSON
        'rich',  # Если не используется Rich
        'pandas',  # Если не используется Pandas
        'numpy',  # Если не используется NumPy
    ],
    noarchive=True,
    optimize=2,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='qq',
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
)
