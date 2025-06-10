#!/bin/bash

# Script to create a DMG installer for AI Prompt Assistant
echo "Creating DMG installer for AI Prompt Assistant..."

# Set variables
APP_NAME="AI Prompt Assistant"
DMG_NAME="${APP_NAME}.dmg"
VOLUME_NAME="${APP_NAME} Installer"
SOURCE_DIR="dist/${APP_NAME}.app"
DMG_TEMP="${APP_NAME}-temp.dmg"
DMG_FINAL="${DMG_NAME}"

# Check if the app exists
if [ ! -d "${SOURCE_DIR}" ]; then
    echo "Error: ${SOURCE_DIR} does not exist. Run build_app.sh first."
    exit 1
fi

# Remove any existing DMG files
rm -f "${DMG_TEMP}" "${DMG_FINAL}"

# Create a temporary DMG
echo "Creating temporary DMG..."
hdiutil create -srcfolder "${SOURCE_DIR}" -volname "${VOLUME_NAME}" -fs HFS+ \
      -fsargs "-c c=64,a=16,e=16" -format UDRW -size 100m "${DMG_TEMP}"

# Mount the temporary DMG
echo "Mounting temporary DMG..."
DEVICE=$(hdiutil attach -readwrite -noverify -noautoopen "${DMG_TEMP}" | \
         egrep '^/dev/' | sed 1q | awk '{print $1}')

# Wait for the mount to complete
sleep 2

# Get the volume path
VOLUME_PATH="/Volumes/${VOLUME_NAME}"

# Create a link to the Applications folder
echo "Creating link to Applications folder..."
ln -s /Applications "${VOLUME_PATH}/Applications"

# Unmount the temporary DMG
echo "Unmounting temporary DMG..."
hdiutil detach "${DEVICE}"

# Convert the temporary DMG to the final DMG
echo "Creating final DMG..."
hdiutil convert "${DMG_TEMP}" -format UDZO -imagekey zlib-level=9 -o "${DMG_FINAL}"

# Remove the temporary DMG
rm -f "${DMG_TEMP}"

echo "DMG installer created: ${DMG_FINAL}"
echo "Installation instructions:"
echo "1. Open the DMG file"
echo "2. Drag the ${APP_NAME} icon to the Applications folder"
echo "3. Launch the application from your Applications folder"
