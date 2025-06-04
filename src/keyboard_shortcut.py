#!/usr/bin/env python3
"""
Keyboard shortcut handler for the AI Prompt Assistant.
This module handles global keyboard shortcut registration using pynput.
"""

import threading
import subprocess
import sys
import os
from pynput import keyboard


class KeyboardShortcutHandler:
    """Handles global keyboard shortcut registration and monitoring using pynput."""
    
    def __init__(self):
        """Initialize the keyboard shortcut handler."""
        self.callback = None
        self.shortcut_keys = []
        self.shortcut_modifiers = []
        self.listener = None
        self.currently_pressed = set()
        self.shortcut_str = ""
        self.is_trusted = True  # Assume trusted until proven otherwise
        self.permission_error = None
    
    def parse_shortcut(self, shortcut_str):
        """Parse a shortcut string like '⌘' into keys and modifiers."""
        self.shortcut_str = shortcut_str
        keys = []
        modifiers = []
        
        # Map symbols to modifier keys
        symbol_to_modifier = {
            '⌘': keyboard.Key.cmd,
            '⇧': keyboard.Key.shift,
            '⌥': keyboard.Key.alt,
            '⌃': keyboard.Key.ctrl
        }
        
        # Process each character in the shortcut string
        for char in shortcut_str:
            # Check if it's a modifier symbol
            if char in symbol_to_modifier:
                modifiers.append(symbol_to_modifier[char])
            # Otherwise, it's a regular key
            else:
                # Convert character to pynput key
                keys.append(keyboard.KeyCode.from_char(char.lower()))
        
        return keys, modifiers
    
    def register_shortcut(self, shortcut_str, callback):
        """Register a global keyboard shortcut."""
        try:
            # Parse the shortcut string
            self.shortcut_keys, self.shortcut_modifiers = self.parse_shortcut(shortcut_str)
            self.callback = callback
            
            # Start the keyboard listener if not already running
            if self.listener is None or not self.listener.running:
                self.start_listener()
            
            print(f"Keyboard shortcut registered: {shortcut_str}")
            return True
        except Exception as e:
            error_str = str(e).lower()
            if "trust" in error_str or "permission" in error_str or "accessibility" in error_str:
                self.is_trusted = False
                self.permission_error = str(e)
                print(f"Accessibility permission error: {e}")
            else:
                print(f"Error registering keyboard shortcut: {e}")
            return False
    
    def needs_accessibility_permissions(self):
        """Check if the application needs to request accessibility permissions."""
        return not self.is_trusted and self.permission_error is not None
    
    def open_accessibility_preferences(self):
        """Open the System Preferences Accessibility panel."""
        try:
            subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"])
            return True
        except Exception as e:
            print(f"Error opening accessibility preferences: {e}")
            return False
    
    def start_listener(self):
        """Start the keyboard listener in a separate thread."""
        try:
            # Create and start the keyboard listener
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.daemon = True
            self.listener.start()
        except Exception as e:
            print(f"Error starting keyboard listener: {e}")
    
    def _on_press(self, key):
        """Handle key press events."""
        try:
            # Add the key to currently pressed keys
            self.currently_pressed.add(key)
            
            # Check if our shortcut is pressed
            if self._check_shortcut():
                if self.callback:
                    # Execute the callback in the main thread
                    threading.Thread(target=self.callback).start()
                    return False  # Stop propagation of this key press
        except Exception as e:
            print(f"Error in key press handler: {e}")
        
        return True  # Continue processing this key press
    
    def _on_release(self, key):
        """Handle key release events."""
        try:
            # Remove the key from currently pressed keys
            if key in self.currently_pressed:
                self.currently_pressed.remove(key)
        except Exception as e:
            print(f"Error in key release handler: {e}")
        
        return True  # Continue listening
    
    def _check_shortcut(self):
        """Check if the current key combination matches our shortcut."""
        # Check if all modifiers are pressed
        for modifier in self.shortcut_modifiers:
            if modifier not in self.currently_pressed:
                return False
        
        # Check if all keys are pressed
        for key in self.shortcut_keys:
            if key not in self.currently_pressed:
                return False
        
        return True
    
    def unregister_shortcut(self):
        """Unregister the current shortcut."""
        if self.listener and self.listener.running:
            self.listener.stop()
            self.listener = None
        
        self.shortcut_keys = []
        self.shortcut_modifiers = []
        self.callback = None
        self.currently_pressed.clear()
    
    def restart_listener(self):
        """Restart the keyboard listener if it was previously registered."""
        try:
            # First, ensure any existing listener is properly stopped
            if self.listener:
                try:
                    if self.listener.running:
                        self.listener.stop()
                except Exception as e:
                    print(f"Error stopping existing listener: {e}")
                self.listener = None
            
            # Only restart if we have both callback and shortcut keys
            if self.callback and self.shortcut_keys:
                # Create a fresh listener
                self.start_listener()
                print("Keyboard shortcut listener successfully restarted")
                return True
            else:
                print("Cannot restart listener: missing callback or shortcut keys")
        except Exception as e:
            print(f"Error in restart_listener: {e}")
        
        return False


# Example usage:
# handler = KeyboardShortcutHandler.alloc().init()
# handler.register_shortcut("⌘ZX", lambda: print("Shortcut pressed!"))
