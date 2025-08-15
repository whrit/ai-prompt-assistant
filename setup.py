"""
Setup script for packaging AI Prompt Assistant with py2app.

This targets the rumps-based implementation (`src/app.py`) via `run_app.py`.
"""

from setuptools import setup

# Use the wrapper so imports resolve correctly and we target the rumps app
APP = ['run_app.py']

DATA_FILES = [
    ('resources/icons', ['resources/icons/menubar_icon.png']),
    ('resources/localization', [
        'resources/localization/en.json',
        'resources/localization/es.json',
        'resources/localization/de.json',
        'resources/localization/sv.json',
        'resources/localization/tr.json',
    ]),
]

OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,  # menubar app (no Dock icon)
        'CFBundleName': 'AI Prompt Assistant',
        'CFBundleDisplayName': 'AI Prompt Assistant',
        'CFBundleIdentifier': 'co.raspiska.aipromptassistant',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'NSHumanReadableCopyright': '© 2025 Raspiska Tech & Consultancy',
    },
    # Force-include modules used by the rumps + PyObjC stack and zlib.
    # Including zlib helps avoid environments where it might otherwise be missed.
    'includes': ['rumps', 'AppKit', 'Quartz', 'requests', 'keyring', 'zlib'],
    # Avoid pulling in Qt when building the rumps-based app
    'excludes': ['PyQt6', 'PySide6', 'PySide2', 'tkinter'],
}

setup(
    name='AI Prompt Assistant',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app>=0.28.6'],
    install_requires=[
        'rumps',
        'requests',
        'keyring',
        'pyobjc',
        'pyobjc-framework-Cocoa',
        'pyobjc-framework-Quartz',
    ],
)
