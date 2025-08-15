#!/bin/bash

# Build script for AI Prompt Assistant
echo "Building AI Prompt Assistant..."

set -euo pipefail

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Detect and activate an existing virtual environment
if [ -d ".venv" ]; then
  echo "Activating Python venv (.venv)"
  source .venv/bin/activate
elif [ -d "venv" ]; then
  echo "Activating Python venv (venv)"
  source venv/bin/activate
else
  echo "No venv found; creating .venv"
  python3 -m venv .venv
  source .venv/bin/activate
fi

python -c "import sys, zlib; print('Using Python:', sys.executable); print('zlib has __file__:', hasattr(zlib, '__file__'))"

# Install dependencies (prefer wheel builds; avoid legacy installer)
echo "Installing dependencies..."
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
pip install 'py2app>=0.28.6'

# Build the application
echo "Building application with py2app..."
python -m pip install --use-pep517 . 1>/dev/null 2>/dev/null || true
python setup.py py2app

echo "Build complete! The application is available in the dist directory."
echo "To create a DMG installer, you can use create-dmg:"
echo "create-dmg --volname \"AI Prompt Assistant\" --volicon \"resources/icons/menubar_icon.icns\" --window-pos 200 120 --window-size 800 400 --icon-size 100 --icon \"AI Prompt Assistant.app\" 200 190 --hide-extension \"AI Prompt Assistant.app\" --app-drop-link 600 185 \"AI Prompt Assistant.dmg\" \"dist/AI Prompt Assistant.app\""
