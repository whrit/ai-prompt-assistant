#!/bin/bash

# Script to create a DMG installer for AI Prompt Assistant using create-dmg
echo "Creating DMG installer for AI Prompt Assistant..."

# Set variables
APP_NAME="AI Prompt Assistant"
DMG_NAME="${APP_NAME}.dmg"
SOURCE_DIR="dist/${APP_NAME}.app"

# Check if the app exists
if [ ! -d "${SOURCE_DIR}" ]; then
    echo "Error: ${SOURCE_DIR} does not exist. Run build_app.sh first."
    exit 1
fi

# Check if create-dmg is installed
if ! command -v create-dmg &> /dev/null; then
    echo "Error: create-dmg is not installed. Install it with: brew install create-dmg"
    exit 1
fi

# Remove any existing DMG files
rm -f "${DMG_NAME}"

# Create DMG using create-dmg with proper escaping
echo "Creating DMG using create-dmg..."
create-dmg \
    --volname "AI Prompt Assistant" \
    --volicon "resources/icons/menubar_icon.png" \
    --window-pos 200 120 \
    --window-size 800 400 \
    --icon-size 100 \
    --icon "${APP_NAME}.app" 200 190 \
    --hide-extension "${APP_NAME}.app" \
    --app-drop-link 600 185 \
    "${DMG_NAME}" \
    "${SOURCE_DIR}"

if [ $? -eq 0 ]; then
    echo "DMG installer created successfully: ${DMG_NAME}"
    echo "Installation instructions:"
    echo "1. Open the DMG file"
    echo "2. Drag the ${APP_NAME} icon to the Applications folder"
    echo "3. Launch the application from your Applications folder"
else
    echo "Error: Failed to create DMG installer"
    exit 1
fi
