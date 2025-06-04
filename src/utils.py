#!/usr/bin/env python3
"""
Utility functions for the AI Prompt Assistant.
"""

import os
import sys
import subprocess
from pathlib import Path


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    return os.path.join(base_path, relative_path)


def set_launch_at_login(enable=True):
    """Configure the app to launch at login."""
    app_path = get_app_path()
    
    if sys.platform != 'darwin':
        print("Launch at login is only supported on macOS")
        return False
    
    try:
        if enable:
            # Add to login items
            cmd = [
                'osascript',
                '-e', 
                f'tell application "System Events" to make login item at end with properties {{path:"{app_path}", hidden:false}}'
            ]
        else:
            # Remove from login items
            cmd = [
                'osascript',
                '-e',
                f'tell application "System Events" to delete login item "{os.path.basename(app_path)}"'
            ]
        
        subprocess.run(cmd, check=True)
        return True
    except subprocess.SubprocessError as e:
        print(f"Failed to set launch at login: {e}")
        return False


def get_app_path():
    """Get the path to the application bundle."""
    if getattr(sys, 'frozen', False):
        # Running as bundled app
        return os.path.abspath(sys.executable)
    else:
        # Running in development
        return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def copy_to_clipboard(text):
    """Copy text to clipboard."""
    if sys.platform == 'darwin':
        try:
            process = subprocess.Popen(
                'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Failed to copy to clipboard: {e}")
            return False
    else:
        print("Clipboard functionality is only supported on macOS")
        return False


def show_notification(title, message):
    """Show a system notification."""
    if sys.platform == 'darwin':
        try:
            cmd = [
                'osascript',
                '-e',
                f'display notification "{message}" with title "{title}"'
            ]
            subprocess.run(cmd, check=True)
            return True
        except subprocess.SubprocessError as e:
            print(f"Failed to show notification: {e}")
            return False
    else:
        print("Notification functionality is only supported on macOS")
        return False
