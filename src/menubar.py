#!/usr/bin/env python3
"""
Menubar implementation for the AI Prompt Assistant.
This file handles the menubar icon, menu items, and their actions.
"""

import os
import rumps
import webbrowser
import threading
from src.settings_manager import SettingsManager
from src.history_manager import HistoryManager
from src.input_dialog import InputDialog
from src.settings_dialog import SettingsDialog
from src.history_dialog import HistoryDialog
from src.keyboard_shortcut import KeyboardShortcutHandler
from src.about_dialog import AboutDialog
from src.version_checker import VersionChecker


class MenuBarApp(rumps.App):
    """Main menubar application class."""
    
    def __init__(self):
        """Initialize the menubar app."""
        # Initialize settings
        self.settings = SettingsManager()
        
        # Initialize history manager
        self.history_manager = HistoryManager()
        
        # Initialize input dialog to None - will create a new one each time
        self.input_dialog = None
        
        # Flag for keyboard shortcut trigger
        self._shortcut_triggered = False
        
        # Initialize shortcut handler
        self.shortcut_handler = None
        
        # We need to initialize the shortcut handler in a separate thread
        # because it needs to run in the main thread of a Cocoa application
        self.init_shortcut_handler_thread = threading.Thread(target=self.init_shortcut_handler)
        self.init_shortcut_handler_thread.daemon = True
        
        # Initialize the app with title and icon
        self.localized_strings = {}
        self.load_localization()
        
        super(MenuBarApp, self).__init__(
            self.get_string("app.name", "AI Prompt"),
            icon=os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                             "resources", "icons", "menubar_icon.png")
        )
        
        # Create menu items
        self.menu = [
            rumps.MenuItem(self.get_string("menubar.open_input", "Open Input"), callback=self.open_input),
            rumps.MenuItem(self.get_string("menubar.history", "History"), callback=self.open_history),
            None,  # Separator
            rumps.MenuItem(self.get_string("menubar.settings", "Settings"), callback=self.open_settings),
            rumps.MenuItem(self.get_string("menubar.check_updates", "Check for Updates"), callback=self.check_updates),
            rumps.MenuItem(self.get_string("menubar.about", "About"), callback=self.open_about),
            None,  # Separator
            rumps.MenuItem(self.get_string("menubar.accessibility", "Accessibility Settings"), callback=self.open_accessibility_settings)
            # rumps automatically adds a Quit menu item, so we don't need to add our own
        ]
        
        # Register global keyboard shortcut
        self.register_keyboard_shortcut()
        
        # Start the shortcut handler thread
        self.init_shortcut_handler_thread.start()
        
        # Set up a timer to check for shortcut triggers
        self.shortcut_timer = rumps.Timer(self.check_shortcut_trigger, 1)
        self.shortcut_timer.start()
    
    def init_shortcut_handler(self):
        """Initialize the keyboard shortcut handler in a separate thread."""
        try:
            # Initialize the keyboard shortcut handler
            self.shortcut_handler = KeyboardShortcutHandler()
            # Register the keyboard shortcut
            self.register_keyboard_shortcut()
            
            # Check if we need to show the accessibility alert
            if self.shortcut_handler.needs_accessibility_permissions():
                self.show_accessibility_alert()
        except Exception as e:
            print(f"Error initializing keyboard shortcut handler: {e}")
    
    def show_accessibility_alert(self):
        """Show an alert if the application is not trusted for accessibility."""
        alert = rumps.alert(
            self.get_string("notifications.accessibility_required", "Accessibility Permission Required"),
            self.get_string("notifications.accessibility_message", "To use keyboard shortcuts, AI Prompt Assistant needs accessibility permissions. Would you like to open System Preferences to grant permission?"),
            [self.get_string("notifications.open_settings", "Open Settings"), self.get_string("notifications.cancel", "Cancel")]
        )
        
        # If the user clicked "Open Settings", open the accessibility preferences
        if alert == 0:  # First button (Open Settings)
            self.open_accessibility_settings()
    
    def open_accessibility_settings(self, sender=None):
        """Open the System Preferences Accessibility panel."""
        if self.shortcut_handler:
            self.shortcut_handler.open_accessibility_preferences()
    
    def register_keyboard_shortcut(self):
        """Register the global keyboard shortcut."""
        shortcut = self.settings.get("keyboard_shortcut", "⌃⌘D")
        print(f"Keyboard shortcut registered as: {shortcut}")
        
        # If the shortcut handler is initialized, register the shortcut
        if self.shortcut_handler:
            try:
                # Use a simple wrapper function that just shows a notification
                # We'll use a flag to indicate that the input dialog should be opened
                # when the user clicks the notification
                def shortcut_callback():
                    try:
                        # Set the flag to indicate shortcut was triggered
                        self._shortcut_triggered = True
                        # Show a notification that will open the input dialog when clicked
                        rumps.notification(
                            "AI Prompt Assistant",
                            "Keyboard Shortcut Detected",
                            "Click to open input dialog",
                            sound=True
                        )
                        # We'll handle opening the dialog when the notification is clicked
                    except Exception as e:
                        print(f"Error in shortcut callback: {e}")
                
                self.shortcut_handler.register_shortcut(shortcut, shortcut_callback)
            except Exception as e:
                print(f"Error registering keyboard shortcut: {e}")
    
    def load_localization(self):
        """Load localized strings based on current language setting."""
        self.localized_strings = self.settings.load_localization()
    
    def get_string(self, key_path, default=""):
        """Get a localized string."""
        return self.settings.get_string(key_path, default)
    
    def change_language(self, lang_code):
        """Change the application language."""
        if self.settings.set_language(lang_code):
            self.load_localization()
            # Update menu items with new language
            self.menu["Open Input"].title = self.get_string("menubar.open_input", "Open Input")
            self.menu["History"].title = self.get_string("menubar.history", "History")
            self.menu["Settings"].title = self.get_string("menubar.settings", "Settings")
            self.menu["Check for Updates"].title = self.get_string("menubar.check_updates", "Check for Updates")
            # The Quit item is automatically added by rumps
            return True
        return False
    
    def update_keyboard_shortcut(self, shortcut):
        """Update the keyboard shortcut."""
        # Save the new shortcut to settings
        self.settings.set("keyboard_shortcut", shortcut)
        
        # Unregister the old shortcut and register the new one
        if self.shortcut_handler:
            self.shortcut_handler.unregister_shortcut()
            self.shortcut_handler.register_shortcut(shortcut, self.open_input)
    
    @rumps.clicked("Open Input")
    def open_input(self, sender=None, initial_text=""):
        """Open the input dialog.
        
        Args:
            sender: The sender of the event (used by rumps)
            initial_text: Optional text to pre-populate the input field with
        """
        # Create a new input dialog each time, with optional initial text
        input_dialog = InputDialog(initial_text=initial_text)
        result = input_dialog.run()
        
        if result and result.get("text"):
            self.process_input(result["text"])
    
    def check_shortcut_trigger(self, timer):
        """Check if a keyboard shortcut was triggered and handle it."""
        # If the shortcut was triggered, open the input dialog
        if self._shortcut_triggered:
            # Reset the flag
            self._shortcut_triggered = False
            # Open the input dialog
            self.open_input()
    
    def process_input(self, text):
        """Process the user input text."""
        print(f"Processing input: {text}")
        
        # Add "how to" prefix if it doesn't already start with it
        if not text.lower().startswith("how to"):
            prefixed_text = f"how to {text}"
        else:
            prefixed_text = text
            
        # Initialize API client if not already done
        if not hasattr(self, 'api_client'):
            from src.api_client import ApiClient
            self.api_client = ApiClient(self.settings)
        
        # Check if API key is available
        api_key = self.settings.get("openai_api_key", "")
        if not api_key:
            # No API key, show notification to the user
            rumps.notification(
                title=self.get_string("api.missing_key.title", "API Key Missing"),
                subtitle=self.get_string("app.name", "AI Prompt Assistant"),
                message=self.get_string("api.missing_key.message", "No OpenAI API key found. Please add your API key in Settings.")
            )
        
        # Send to API for rephrasing
        try:
            rephrased_text = self.api_client.rephrase_prompt(prefixed_text)
            print(f"Rephrased text: {rephrased_text}")
            
            # The API client already adds the entry to history
            ai_service = self.settings.get("ai_service", "chatgpt")
            
            # Get the URL for the AI service with the rephrased text
            url = self.api_client.get_ai_service_url(ai_service, rephrased_text)
            
            # Open the browser with the rephrased text
            webbrowser.open(url)
            
            # Show success notification if rephrasing was successful and different from original
            if rephrased_text != prefixed_text and api_key:
                rumps.notification(
                    title=self.get_string("api.success.title", "Prompt Rephrased"),
                    subtitle=self.get_string("app.name", "AI Prompt Assistant"),
                    message=self.get_string("api.success.message", "Your prompt was successfully rephrased and sent to the browser.")
                )
            
        except Exception as e:
            # If API call fails, fall back to original behavior
            print(f"API error: {e}")
            self.history_manager.add_entry(text, text, self.settings.get("ai_service", "chatgpt"))
            
            # Show error notification
            rumps.notification(
                title=self.get_string("api.error.title", "API Error"),
                subtitle=self.get_string("app.name", "AI Prompt Assistant"),
                message=f"{self.get_string('api.error.message', 'Error rephrasing prompt:')} {str(e)}"
            )
            
            # Fall back to direct browser opening with original text
            ai_service = self.settings.get("ai_service", "chatgpt")
            url = f"https://chat.openai.com/?prompt={text}"
            if ai_service == "chatgpt":
                webbrowser.open(url)
        
        # No need to restart the keyboard shortcut listener anymore
        # since we're using a reusable dialog that just hides/shows
    
    @rumps.clicked("Settings")
    def open_settings(self, _):
        """Open the settings dialog."""
        dialog = SettingsDialog(self.settings)
        result = dialog.exec()
        
        if result == 1:  # QDialog.Accepted
            result_data = dialog.get_result()
            if not result_data:
                return
                
            # Process language change
            if "language" in result_data:
                lang_code = result_data["language"]
                if self.change_language(lang_code):
                    rumps.notification(
                        title=self.get_string("settings.language.changed", "Language Changed"),
                        subtitle=self.get_string("app.name", "AI Prompt Assistant"),
                        message=self.get_string("settings.language.restart_recommended", "Language changed. Some elements may require restart.")
                    )
            
            # Process keyboard shortcut change
            if "keyboard_shortcut" in result_data:
                self.update_keyboard_shortcut(result_data["keyboard_shortcut"])
                
            # Process AI service change
            if "ai_service" in result_data:
                self.settings.set("ai_service", result_data["ai_service"])
                
            # Process API key change
            if "openai_api_key" in result_data:
                self.settings.set("openai_api_key", result_data["openai_api_key"])
                
            # Process launch at login change
            if "launch_at_login" in result_data:
                self.settings.set("launch_at_login", result_data["launch_at_login"])
    
    @rumps.clicked("History")
    def open_history(self, _):
        """Open the history dialog."""
        dialog = HistoryDialog(self.history_manager)
        
        # Connect the prompt_selected signal to our handler
        dialog.prompt_selected.connect(self.reuse_prompt_from_history)
        
        # Show the dialog
        dialog.exec()
    
    def reuse_prompt_from_history(self, prompt_text):
        """Reuse a prompt from history."""
        if prompt_text:
            # Use the existing open_input method with the selected prompt as initial text
            self.open_input(initial_text=prompt_text)
    
    @rumps.clicked("Check for Updates")
    def check_updates(self, _):
        """Check for application updates."""
        checker = VersionChecker()
        update_info = checker.check_for_updates()
        
        if update_info and update_info.get("available"):
            rumps.notification(
                title=update_info.get("title", self.get_string("notifications.update_available", "Update Available")),
                subtitle=self.get_string("app.name", "AI Prompt Assistant"),
                message=update_info.get("text", "A new version is available.")
            )
        else:
            rumps.notification(
                title=self.get_string("notifications.no_updates", "No Updates"),
                subtitle=self.get_string("app.name", "AI Prompt Assistant"),
                message=self.get_string("notifications.no_updates_message", "You're using the latest version.")
            )

    def open_about(self, _):
        """Open the about dialog."""
        about_dialog = AboutDialog(self.settings)
        about_dialog.exec()
