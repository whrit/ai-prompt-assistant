#!/usr/bin/env python3
"""
Input dialog implementation for the AI Prompt Assistant.
This file handles the floating input window that appears when triggered.
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                            QTextEdit, QPushButton, QLabel)
from PyQt6.QtCore import Qt, QSize, QObject, QEvent
from PyQt6.QtGui import QFont, QIcon


class InputDialog:
    """Custom input dialog that appears in the center of the screen."""
    
    def __init__(self, settings):
        """Initialize the input dialog with settings."""
        self.settings = settings
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.dialog = None
        self.text_input = None
        self.result = {"text": "", "submitted": False}
    
    def run(self):
        """Create and show the dialog, then return the result."""
        self.create_dialog()
        self.dialog.exec()
        return self.result if self.result["submitted"] else None
    
    def create_dialog(self):
        """Create the input dialog UI."""
        self.dialog = QDialog()
        self.dialog.setWindowTitle("AI Prompt Assistant")
        self.dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.dialog.setMinimumSize(600, 300)
        
        # Center the dialog on screen
        screen_geometry = self.app.primaryScreen().geometry()
        x = (screen_geometry.width() - self.dialog.width()) // 2
        y = (screen_geometry.height() - self.dialog.height()) // 2
        self.dialog.move(x, y)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add header
        header_layout = QHBoxLayout()
        title_label = QLabel("Enter your prompt")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Close button
        close_button = QPushButton("×")
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.dialog.close)
        header_layout.addWidget(close_button)
        
        layout.addLayout(header_layout)
        
        # Add text input
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Type your prompt here...")
        self.text_input.setFont(QFont("Arial", 12))
        layout.addWidget(self.text_input)
        
        # Add character counter
        self.char_counter = QLabel("0 characters")
        self.char_counter.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.char_counter)
        
        # Connect text changed signal
        self.text_input.textChanged.connect(self.update_char_count)
        
        # Add buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        submit_button = QPushButton("Ask")
        submit_button.setFixedSize(100, 40)
        submit_button.clicked.connect(self.submit)
        button_layout.addWidget(submit_button)
        
        layout.addLayout(button_layout)
        
        # Set layout
        self.dialog.setLayout(layout)
        
        # Set focus to text input
        self.text_input.setFocus()
        
        # Connect enter key to submit
        self.text_input.installEventFilter(EnterKeyFilter(self))
    
    def update_char_count(self):
        """Update the character counter."""
        count = len(self.text_input.toPlainText())
        self.char_counter.setText(f"{count} characters")
    
    def submit(self):
        """Submit the input text."""
        text = self.text_input.toPlainText().strip()
        if text:
            self.result = {"text": text, "submitted": True}
            self.dialog.accept()


class EnterKeyFilter(QObject):
    """Event filter to handle Enter key press."""
    
    def __init__(self, dialog):
        super().__init__()
        self.dialog = dialog
    
    def eventFilter(self, obj, event):
        """Filter events to catch Enter key press."""
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Return and not event.modifiers():
            self.dialog.submit()
            return True
        return super().eventFilter(obj, event)
