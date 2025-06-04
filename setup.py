"""
Setup script for packaging AI Prompt Assistant with py2app.
"""

from setuptools import setup

APP = ['src/main.py']
DATA_FILES = [
    ('resources/icons', ['resources/icons/menubar_icon.png']),
    ('resources/localization', ['resources/localization/en.json'])
]
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,  # This makes it a menubar app without dock icon
        'CFBundleName': 'AI Prompt Assistant',
        'CFBundleDisplayName': 'AI Prompt Assistant',
        'CFBundleIdentifier': 'co.raspiska.aipromptassistant',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'NSHumanReadableCopyright': '© 2025 Raspiska Tech & Consultancy',
    },
    'packages': ['rumps', 'PyQt6'],
    'includes': ['keyring', 'requests'],
}

setup(
    name='AI Prompt Assistant',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'rumps',
        'PyQt6',
        'requests',
        'keyring'
    ],
)
