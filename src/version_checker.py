#!/usr/bin/env python3
"""
Version checker for the AI Prompt Assistant.
Checks for updates and notifies the user.
"""

import requests
from src import __version__


class VersionChecker:
    """Checks for application updates."""
    
    def __init__(self):
        """Initialize the version checker."""
        self.current_version = __version__
        self.api_url = "https://api.example.com/version"  # Replace with actual API URL
    
    def check_for_updates(self):
        """Check if updates are available."""
        try:
            response = requests.get(self.api_url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            latest_version = data.get("version")
            
            if self._is_newer_version(latest_version):
                return {
                    "available": True,
                    "version": latest_version,
                    "title": data.get("title", "Update Available"),
                    "text": data.get("text", f"Version {latest_version} is now available.")
                }
            else:
                return {"available": False}
                
        except requests.exceptions.RequestException as e:
            print(f"Update check failed: {e}")
            return {"available": False, "error": str(e)}
    
    def _is_newer_version(self, version_str):
        """Compare versions to determine if the new version is newer."""
        if not version_str:
            return False
            
        # Convert version strings to tuples of integers
        current = tuple(map(int, self.current_version.split('.')))
        latest = tuple(map(int, version_str.split('.')))
        
        # Compare versions
        return latest > current
