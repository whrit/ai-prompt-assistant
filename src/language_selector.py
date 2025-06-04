#!/usr/bin/env python3
"""
Language selector dialog for the AI Prompt Assistant.
"""

import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QComboBox, QPushButton)
from PyQt6.QtCore import Qt


class LanguageSelector(QDialog):
    """Dialog for selecting the application language."""
    
    def __init__(self, settings):
        """Initialize the language selector dialog."""
        super().__init__()
        self.settings = settings
        self.result_lang_code = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle(self.settings.get_string("settings.language.select_language", "Select Language"))
        self.setFixedSize(300, 150)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        # Center the dialog on screen
        screen_geometry = self.screen().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_label = QLabel(self.settings.get_string("settings.language.select_language", "Select Language:"))
        self.lang_combo = QComboBox()
        
        # Add available languages
        current_lang = self.settings.get_current_language()
        for lang in self.settings.get_available_languages():
            self.lang_combo.addItem(lang["name"], lang["code"])
            if lang["code"] == current_lang:
                self.lang_combo.setCurrentText(lang["name"])
        
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton(self.settings.get_string("settings.apply", "Apply"))
        self.cancel_button = QPushButton(self.settings.get_string("settings.cancel", "Cancel"))
        
        self.apply_button.clicked.connect(self.apply_language)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)
        
        # Add all layouts to main layout
        layout.addLayout(lang_layout)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def apply_language(self):
        """Apply the selected language."""
        selected_index = self.lang_combo.currentIndex()
        if selected_index >= 0:
            self.result_lang_code = self.lang_combo.itemData(selected_index)
            self.accept()
    
    def get_result(self):
        """Get the result of the dialog."""
        return {"language": self.result_lang_code} if self.result_lang_code else None
