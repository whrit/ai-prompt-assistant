#!/usr/bin/env python3
"""
Main entry point for the AI Prompt Assistant application.
This file initializes the menubar app and connects all components.
"""

import sys
import os
from src.menubar import MenuBarApp


def main():
    """Initialize and run the application."""
    # Ensure application directories exist
    setup_app_directories()
    
    # Start the menubar application
    app = MenuBarApp()
    app.run()


def setup_app_directories():
    """Create necessary application directories if they don't exist."""
    app_data_dir = os.path.expanduser("~/Library/Application Support/AI Prompt Assistant")
    
    # Create main app data directory
    if not os.path.exists(app_data_dir):
        os.makedirs(app_data_dir)
    
    # Create subdirectories
    for subdir in ["history", "settings", "logs"]:
        path = os.path.join(app_data_dir, subdir)
        if not os.path.exists(path):
            os.makedirs(path)


if __name__ == "__main__":
    main()
