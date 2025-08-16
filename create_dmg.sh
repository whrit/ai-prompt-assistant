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

# Calculate the app size and determine appropriate DMG size
echo "Calculating app size..."
APP_SIZE_KB=$(du -sk "${SOURCE_DIR}" | cut -f1)
APP_SIZE_MB=$((APP_SIZE_KB / 1024))
# Add 50MB buffer for DMG overhead and Applications link
DMG_SIZE_MB=$((APP_SIZE_MB + 50))

echo "App size: ${APP_SIZE_MB}MB"
echo "DMG size will be: ${DMG_SIZE_MB}MB"

# Remove any existing DMG files
rm -f "${DMG_TEMP}" "${DMG_FINAL}"

# Create a temporary DMG with calculated size
echo "Creating temporary DMG..."
hdiutil create -srcfolder "${SOURCE_DIR}" -volname "${VOLUME_NAME}" -fs HFS+ \
      -fsargs "-c c=64,a=16,e=16" -format UDRW -size ${DMG_SIZE_MB}m "${DMG_TEMP}"

if [ $? -ne 0 ]; then
    echo "Error: Failed to create temporary DMG"
    exit 1
fi

# Mount the temporary DMG
echo "Mounting temporary DMG..."
DEVICE=$(hdiutil attach -readwrite -noverify -noautoopen "${DMG_TEMP}" | \
         egrep '^/dev/' | sed 1q | awk '{print $1}')

if [ -z "${DEVICE}" ]; then
    echo "Error: Failed to mount temporary DMG"
    rm -f "${DMG_TEMP}"
    exit 1
fi

echo "Mounted DMG on device: ${DEVICE}"

# Wait for the mount to complete
sleep 3

# Get the volume path
VOLUME_PATH="/Volumes/${VOLUME_NAME}"

# Verify the volume is accessible
if [ ! -d "${VOLUME_PATH}" ]; then
    echo "Error: Volume path ${VOLUME_PATH} is not accessible"
    hdiutil detach "${DEVICE}" 2>/dev/null
    rm -f "${DMG_TEMP}"
    exit 1
fi

# Create a link to the Applications folder
echo "Creating link to Applications folder..."
ln -s /Applications "${VOLUME_PATH}/Applications"

if [ $? -ne 0 ]; then
    echo "Error: Failed to create Applications link"
    hdiutil detach "${DEVICE}" 2>/dev/null
    rm -f "${DMG_TEMP}"
    exit 1
fi

# Unmount the temporary DMG
echo "Unmounting temporary DMG..."
hdiutil detach "${DEVICE}"

if [ $? -ne 0 ]; then
    echo "Error: Failed to unmount temporary DMG"
    exit 1
fi

# Convert the temporary DMG to the final DMG
echo "Creating final DMG..."
hdiutil convert "${DMG_TEMP}" -format UDZO -imagekey zlib-level=9 -o "${DMG_FINAL}"

if [ $? -ne 0 ]; then
    echo "Error: Failed to create final DMG"
    rm -f "${DMG_TEMP}"
    exit 1
fi

# Remove the temporary DMG
rm -f "${DMG_TEMP}"

echo "DMG installer created: ${DMG_FINAL}"
echo "Installation instructions:"
echo "1. Open the DMG file"
echo "2. Drag the ${APP_NAME} icon to the Applications folder"
echo "3. Launch the application from your Applications folder"
