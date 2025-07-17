# macropad_script.spec
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],  # Добавьте путь к вашим файлам
    binaries=[],
    datas=[],  # Можете добавить дополнительные файлы, например ('macropad.log', '.')
    hiddenimports=[
        'win32gui',
        'win32con',
        'win32api',
        'win32process',
        'serial',
        'psutil',
        'pywintypes'  # Важно! Часто упускают этот модуль
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='MacroPadController',
    debug=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,  # Установите True, если нужна консоль для отладки
    icon='macropad_icon.ico',
    target_arch='x64'  # Явно укажите архитектуру, если нужно
)