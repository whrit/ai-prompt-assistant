#!/usr/bin/env python3
"""
Wrapper script to run the AI Prompt Assistant application.
This ensures the proper Python path is set up.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import and run the app
from src.app import run


if __name__ == "__main__":
    run()
