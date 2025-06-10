#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QFont

class AboutDialog(QDialog):
    """Dialog showing information about the application."""
    
    def __init__(self, settings, parent=None):
        """Initialize the about dialog.
        
        Args:
            settings: The settings manager instance
            parent: The parent widget
        """
        super().__init__(parent)
        self.settings = settings
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle(self.settings.get_string("about.title", "About AI Prompt Assistant"))
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # App name and version
        app_name_label = QLabel(self.settings.get_string("app.name", "AI Prompt Assistant"))
        app_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        app_name_label.setFont(font)
        
        version = self.settings.get_string("app.version", "1.0.0")
        version_label = QLabel(f"v{version}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Description
        description = self.settings.get_string(
            "about.description", 
            "A menubar application that helps you create better AI prompts."
        )
        description_label = QLabel(description)
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Copyright
        current_year = "2025"  # This should be dynamically generated in a real app
        copyright_text = f"© {current_year} " + self.settings.get_string("about.copyright", "AI Prompt Assistant Team")
        copyright_label = QLabel(copyright_text)
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Credits
        credits_label = QLabel(self.settings.get_string("about.credits", "Created by me using Windsurf (https://windsurf.com/)") )
        credits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Close button
        button_layout = QHBoxLayout()
        close_button = QPushButton(self.settings.get_string("about.close", "Close"))
        close_button.clicked.connect(self.accept)
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        button_layout.addWidget(close_button)
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Add widgets to layout
        layout.addWidget(app_name_label)
        layout.addWidget(version_label)
        layout.addWidget(description_label)
        layout.addWidget(copyright_label)
        layout.addWidget(credits_label)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
