#!/usr/bin/env python3
"""
Settings manager for the AI Prompt Assistant.
Handles loading, saving, and accessing application settings.
"""

import os
import json
import keyring
from pathlib import Path
import locale


class SettingsManager:
    """Manages application settings and preferences."""
    
    def __init__(self):
        """Initialize the settings manager."""
        self.settings = {}
        self.settings_file = os.path.expanduser(
            "~/Library/Application Support/AI Prompt Assistant/settings/preferences.json"
        )
        self.load_settings()
    
    def load_settings(self):
        """Load settings from the settings file."""
        # Create default settings
        self.settings = {
            "keyboard_shortcut": "⌃⌘D",
            "ai_service": "chatgpt",
            "language": "en",
            "launch_at_login": False,
            "check_updates_automatically": True,
            "history_limit": 100,
            "openai_api_key": ""
        }
        
        # Try to load API key from keyring
        try:
            api_key = keyring.get_password("ai_prompt_assistant", "openai_api_key")
            if api_key:
                self.settings["openai_api_key"] = api_key
        except Exception as e:
            print(f"Error loading API key from keyring: {e}")
        
        # Load settings from file if it exists
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to the settings file."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except IOError as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key, default=None):
        """Get a setting value."""
        # For API key, try to get from keyring first
        if key == "openai_api_key":
            try:
                api_key = keyring.get_password("ai_prompt_assistant", "openai_api_key")
                if api_key:
                    return api_key
            except Exception as e:
                print(f"Error getting API key from keyring: {e}")
                
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value."""
        self.settings[key] = value
        
        # Store API key in keyring for security
        if key == "openai_api_key" and value:
            try:
                keyring.set_password("ai_prompt_assistant", "openai_api_key", value)
                # Don't store the actual key in the settings file
                self.settings[key] = "*****"
            except Exception as e:
                print(f"Error storing API key in keyring: {e}")
                
        self.save_settings()
        return True
    
    def get_secure(self, key):
        """Get a secure setting value from the keychain."""
        return keyring.get_password("AI Prompt Assistant", key)
    
    def set_secure(self, key, value):
        """Set a secure setting value in the keychain."""
        keyring.set_password("AI Prompt Assistant", key, value)
    
    def clear_secure(self, key):
        """Clear a secure setting value from the keychain."""
        try:
            keyring.delete_password("AI Prompt Assistant", key)
        except keyring.errors.PasswordDeleteError:
            pass
    
    def get_available_languages(self):
        """Get a list of available languages."""
        languages = [
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Spanish"},
            {"code": "de", "name": "German"},
            {"code": "sv", "name": "Swedish"},
            {"code": "tr", "name": "Turkish"}
        ]
        return languages
    
    def get_current_language(self):
        """Get the current language code."""
        return self.get("language", "en")
    
    def set_language(self, lang_code):
        """Set the current language."""
        if lang_code in [lang["code"] for lang in self.get_available_languages()]:
            self.set("language", lang_code)
            return True
        return False
    
    def load_localization(self):
        """Load the localization file for the current language."""
        lang_code = self.get_current_language()
        # Get the correct path to the resources directory
        base_dir = os.path.dirname(os.path.dirname(__file__))
        localization_file = os.path.join(
            base_dir, "resources", "localization", f"{lang_code}.json"
        )
        
        try:
            with open(localization_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError, FileNotFoundError) as e:
            print(f"Error loading localization file: {e}")
            # Fall back to English if the selected language file can't be loaded
            if lang_code != "en":
                self.set_language("en")
                return self.load_localization()
            return {}
    
    def get_string(self, key_path, default=""):
        """Get a localized string by its key path (e.g., 'menubar.open_input')."""
        localization = self.load_localization()
        keys = key_path.split('.')
        
        # Navigate through the nested dictionary
        current = localization
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current if isinstance(current, str) else default
