#!/bin/bash

# Build script for AI Prompt Assistant
echo "Building AI Prompt Assistant..."

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install py2app

# Build the application
echo "Building application with py2app..."
python setup.py py2app

echo "Build complete! The application is available in the dist directory."
echo "To create a DMG installer, you can use create-dmg:"
echo "create-dmg --volname \"AI Prompt Assistant\" --volicon \"resources/icons/menubar_icon.icns\" --window-pos 200 120 --window-size 800 400 --icon-size 100 --icon \"AI Prompt Assistant.app\" 200 190 --hide-extension \"AI Prompt Assistant.app\" --app-drop-link 600 185 \"AI Prompt Assistant.dmg\" \"dist/AI Prompt Assistant.app\""
