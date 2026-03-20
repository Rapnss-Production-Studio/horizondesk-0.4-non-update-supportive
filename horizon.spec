# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Horizon Desk
# Run with: pyinstaller horizon.spec

import os

# Root of the project (where this spec lives)
ROOT = os.path.abspath(SPECPATH)

block_cipher = None

a = Analysis(
    # Entry point
    [os.path.join(ROOT, 'sample-gui', 'main_gui.py')],

    pathex=[
        ROOT,                                   # project root (for core/, tools/, ai/)
        os.path.join(ROOT, 'sample-gui'),       # for local imports in main_gui.py
    ],

    binaries=[],

    datas=[
        # React production build — served as the webview UI
        (os.path.join(ROOT, 'sample-gui', 'dist'), 'sample-gui/dist'),

        # App icon
        (os.path.join(ROOT, 'sample-gui', 'public', 'logo.ico'), 'sample-gui/public'),

        # Environment variables (API keys etc.)
        (os.path.join(ROOT, '.env'), '.'),

        # Plugins folder — copied as-is so users can install/edit plugins
        (os.path.join(ROOT, 'plugins'), 'plugins'),

        # Assets (wallpapers, media, etc.)
        (os.path.join(ROOT, 'assets'), 'assets'),
    ],

    # Hidden imports that PyInstaller's static analysis may miss
    hiddenimports=[
        # Core framework modules
        'core',
        'core.agent',
        'core.input_manager',
        'core.memory',
        'core.llm',
        'core.plugin_manager',
        'core.skill_manager',
        'core.capabilities',
        'core.cortex',
        'core.swarm',
        'core.synapse',
        'core.horizon_online',
        'core.overlay',
        'core.voice',
        'core.vision_monitor',
        'core.gateway_logic',
        'core.knowledge_base',
        'core.tools',

        # Tools
        'tools',
        'tools.filesystem',
        'tools.desktop',
        'tools.system',
        'tools.web',
        'tools.advanced_tools',
        'tools.interaction',
        'tools.research',
        'tools.vision',
        'tools.voice_tools',
        'tools.playwright_tool',
        'tools.telegram_tool',
        'tools.video_tools',
        'tools.sgi_tools',
        'tools.horizon_online_tools',

        # Root main.py — contains get_initialized_agent, lazily imported in main_gui.py
        # PyInstaller's static analysis misses lazy/deferred imports inside functions
        'main',

        # Third-party libraries likely missed by auto-analysis
        'webview',
        'webview.platforms.winforms',
        'groq',
        'firebase_admin',
        'firebase_admin.credentials',
        'firebase_admin.firestore',
        'dotenv',
        'requests',
        'PIL',
        'PIL.Image',
        'pywinauto',
        'pyautogui',
        'colorama',
        'pynput',
        'pynput.keyboard',
        'pynput.mouse',
        'networkx',
        'yaml',
        'pyperclip',
        'psutil',
        'win32api',
        'win32con',
        'win32gui',
        'pywintypes',
    ],

    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude development tools, test files, source dirs not needed at runtime
        'pytest',
        'setuptools',
        'pip',
        'venv',
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
    [],
    exclude_binaries=True,
    name='HorizonDesk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                     # compress with UPX if available
    console=False,                # no console window (silent launch)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(ROOT, 'sample-gui', 'public', 'logo.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HorizonDesk',           # output folder: dist/HorizonDesk/
)
