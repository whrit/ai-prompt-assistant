#!/usr/bin/env python3
"""
Settings dialog for the AI Prompt Assistant.
"""

import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QComboBox, QPushButton, QLineEdit,
                            QTabWidget, QWidget, QCheckBox, QGroupBox,
                            QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt
import requests


class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""
    
    def __init__(self, settings):
        """Initialize the settings dialog."""
        super().__init__()
        self.settings = settings
        self.result_data = {}
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle(self.settings.get_string("settings.title", "Settings"))
        self.setFixedSize(500, 400)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        # Center the dialog on screen
        screen_geometry = self.screen().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
        # Create main layout
        main_layout = QVBoxLayout()
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self.general_tab = self.create_general_tab()
        self.ai_tab = self.create_ai_tab()
        self.language_tab = self.create_language_tab()
        
        # Add tabs to widget
        self.tabs.addTab(self.general_tab, self.settings.get_string("settings.tabs.general", "General"))
        self.tabs.addTab(self.ai_tab, self.settings.get_string("settings.tabs.ai", "AI Selection"))
        self.tabs.addTab(self.language_tab, self.settings.get_string("settings.tabs.language", "Language"))
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton(self.settings.get_string("settings.save", "Save"))
        self.cancel_button = QPushButton(self.settings.get_string("settings.cancel", "Cancel"))
        
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        # Add components to main layout
        main_layout.addWidget(self.tabs)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def create_general_tab(self):
        """Create the general settings tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Keyboard shortcut
        shortcut_group = QGroupBox(self.settings.get_string("settings.general.keyboard_shortcut", "Keyboard Shortcut"))
        shortcut_layout = QFormLayout()
        self.shortcut_edit = QLineEdit(self.settings.get("keyboard_shortcut", "⌃⌘D"))
        shortcut_layout.addRow(self.settings.get_string("settings.general.current_shortcut", "Current Shortcut:"), self.shortcut_edit)
        shortcut_group.setLayout(shortcut_layout)
        
        # Launch at login
        startup_group = QGroupBox(self.settings.get_string("settings.general.startup", "Startup"))
        startup_layout = QVBoxLayout()
        self.launch_checkbox = QCheckBox(self.settings.get_string("settings.general.launch_at_login", "Launch at Login"))
        self.launch_checkbox.setChecked(self.settings.get("launch_at_login", False))
        startup_layout.addWidget(self.launch_checkbox)
        startup_group.setLayout(startup_layout)
        
        # Add groups to layout
        layout.addWidget(shortcut_group)
        layout.addWidget(startup_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_ai_tab(self):
        """Create the AI settings tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # AI Service selection
        service_group = QGroupBox(self.settings.get_string("settings.ai.select_service", "Select AI Service"))
        service_layout = QVBoxLayout()
        
        self.ai_combo = QComboBox()
        self.ai_combo.addItem("ChatGPT", "chatgpt")
        self.ai_combo.addItem("Google Bard", "bard")
        self.ai_combo.addItem("Claude", "claude")
        
        # Set current AI service
        current_ai = self.settings.get("ai_service", "chatgpt")
        for i in range(self.ai_combo.count()):
            if self.ai_combo.itemData(i) == current_ai:
                self.ai_combo.setCurrentIndex(i)
                break
        
        service_layout.addWidget(self.ai_combo)
        service_group.setLayout(service_layout)
        
        # API Key
        api_group = QGroupBox(self.settings.get_string("settings.ai.api_key", "API Key"))
        api_layout = QFormLayout()
        
        # API Key input with test button in a horizontal layout
        key_layout = QHBoxLayout()
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        api_key = self.settings.get("openai_api_key", "")
        self.api_key_edit.setText(api_key)
        
        self.test_api_key_button = QPushButton(self.settings.get_string("settings.ai.test_api_key", "Test Key"))
        self.test_api_key_button.clicked.connect(self.test_api_key)
        
        key_layout.addWidget(self.api_key_edit)
        key_layout.addWidget(self.test_api_key_button)
        
        api_layout.addRow(self.settings.get_string("settings.ai.openai_api_key", "OpenAI API Key:"), key_layout)
        api_group.setLayout(api_layout)
        
        # Add groups to layout
        layout.addWidget(service_group)
        layout.addWidget(api_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_language_tab(self):
        """Create the language settings tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Language selection
        lang_group = QGroupBox(self.settings.get_string("settings.language.select_language", "Select Language"))
        lang_layout = QVBoxLayout()
        
        self.lang_combo = QComboBox()
        
        # Add available languages
        current_lang = self.settings.get_current_language()
        for lang in self.settings.get_available_languages():
            self.lang_combo.addItem(lang["name"], lang["code"])
            if lang["code"] == current_lang:
                self.lang_combo.setCurrentText(lang["name"])
        
        lang_layout.addWidget(self.lang_combo)
        lang_group.setLayout(lang_layout)
        
        # Add groups to layout
        layout.addWidget(lang_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def save_settings(self):
        """Save all settings."""
        # Save language
        selected_lang_index = self.lang_combo.currentIndex()
        if selected_lang_index >= 0:
            lang_code = self.lang_combo.itemData(selected_lang_index)
            self.result_data["language"] = lang_code
        
        # Save AI service
        selected_ai_index = self.ai_combo.currentIndex()
        if selected_ai_index >= 0:
            ai_service = self.ai_combo.itemData(selected_ai_index)
            self.result_data["ai_service"] = ai_service
        
        # Save API key
        api_key = self.api_key_edit.text().strip()
        if api_key:
            self.result_data["openai_api_key"] = api_key
        
        # Save keyboard shortcut
        shortcut = self.shortcut_edit.text().strip()
        if shortcut:
            self.result_data["keyboard_shortcut"] = shortcut
        
        # Save launch at login
        self.result_data["launch_at_login"] = self.launch_checkbox.isChecked()
        
        self.accept()
    
    def test_api_key(self):
        """Test if the API key is valid."""
        api_key = self.api_key_edit.text().strip()
        
        if not api_key:
            QMessageBox.warning(
                self,
                self.settings.get_string("settings.ai.api_key_error", "API Key Error"),
                self.settings.get_string("settings.ai.api_key_empty", "Please enter an API key to test.")
            )
            return
        
        # Show a message that we're testing
        self.test_api_key_button.setEnabled(False)
        self.test_api_key_button.setText(self.settings.get_string("settings.ai.testing", "Testing..."))
        
        # Test the API key with a simple request
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            # Make a simple models list request to verify the key
            response = requests.get(
                "https://api.openai.com/v1/models",
                headers=headers,
                timeout=10
            )
            
            response.raise_for_status()
            
            # If we get here, the key is valid
            QMessageBox.information(
                self,
                self.settings.get_string("settings.ai.api_key_valid", "API Key Valid"),
                self.settings.get_string("settings.ai.api_key_success", "The API key is valid and working correctly.")
            )
            
        except Exception as e:
            # Show error message
            QMessageBox.critical(
                self,
                self.settings.get_string("settings.ai.api_key_error", "API Key Error"),
                f"{self.settings.get_string('settings.ai.api_key_invalid', 'The API key appears to be invalid:')} {str(e)}"
            )
        
        # Reset button
        self.test_api_key_button.setEnabled(True)
        self.test_api_key_button.setText(self.settings.get_string("settings.ai.test_api_key", "Test Key"))
    
    def get_result(self):
        """Get the result of the dialog."""
        return self.result_data if self.result_data else None
