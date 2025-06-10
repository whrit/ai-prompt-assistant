#!/usr/bin/env python3
"""
Input dialog implementation for the AI Prompt Assistant.
This file handles the floating input window that appears when triggered.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt6.QtCore import Qt, QObject, QEvent, QTimer
from PyQt6.QtGui import QFont, QIcon


class InputDialog:
    """Custom input dialog that appears in the center of the screen."""
    
    def __init__(self, initial_text=""):
        """Initialize the input dialog.
        
        Args:
            initial_text (str): Optional text to pre-populate the input field with.
        """
        self.app = None
        self.dialog = None
        self.char_counter = None
        self.text_input = None
        self.initial_text = initial_text
        self.result = {"text": "", "submitted": False}
    
    def run(self):
        """Create and show the dialog, then return the result."""
        # Initialize QApplication in the main thread
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        
        # Reset result for this run
        self.result = {"text": "", "submitted": False}
        
        # Create a completely new dialog each time
        self.dialog = QDialog()
        self.setup_dialog()
        
        # Execute the dialog
        result = self.dialog.exec()
        
        # Return the result
        return self.result if self.result["submitted"] else None
    
    def setup_dialog(self):
        """Set up the input dialog UI."""
        self.dialog = QDialog()
        self.dialog.setWindowTitle("AI Prompt Assistant")
        self.dialog.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.dialog.setModal(True)
        self.dialog.finished.connect(self.on_dialog_closed)
        self.dialog.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Center the dialog on screen
        screen_geometry = self.app.primaryScreen().geometry()
        self.dialog.resize(500, 200)
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
        
        # Set initial text if provided
        if self.initial_text:
            self.text_input.setText(self.initial_text)
            # Position cursor at the end of the text
            cursor = self.text_input.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.text_input.setTextCursor(cursor)
            
        layout.addWidget(self.text_input)
        
        # Add character counter with improved styling
        self.char_counter = QLabel("0 characters")
        self.char_counter.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.char_counter.setStyleSheet("color: #666; font-style: italic;")
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
        
        # Add event filter for Enter key
        self.text_input.installEventFilter(EnterKeyFilter(self))
        
        # Set up focus handling - this is critical for the dialog to work properly
        # Connect to the dialog's show event to set focus after it's visible
        self.dialog.showEvent = lambda event: self._on_dialog_shown(event)
        
        # Also set up a timer to ensure focus is set after dialog is fully rendered
        QTimer.singleShot(10, self._setup_focus_timers)
    
    def _on_dialog_shown(self, event):
        """Handle dialog show event to set focus."""
        # Call the original showEvent handler
        QDialog.showEvent(self.dialog, event)
        # Set focus to the text input
        self.text_input.setFocus()
        # Ensure the window is active
        self.dialog.activateWindow()
    
    def _setup_focus_timers(self):
        """Set up multiple timers to ensure focus is set."""
        # Use multiple timers with increasing delays for maximum reliability
        QTimer.singleShot(50, self._force_focus)
        QTimer.singleShot(150, self._force_focus)
        QTimer.singleShot(300, self._force_focus)
        QTimer.singleShot(500, self._force_focus)
    
    def _force_focus(self):
        """Force focus to the text input field."""
        if self.dialog and self.text_input:
            self.text_input.setFocus()
            self.dialog.activateWindow()
    
    def update_char_count(self):
        """Update the character counter with more detailed information."""
        text = self.text_input.toPlainText()
        char_count = len(text)
        word_count = len(text.split()) if text.strip() else 0
        
        # Change color based on character count
        if char_count > 1000:
            self.char_counter.setStyleSheet("color: #c0392b; font-style: italic;") # Red for very long prompts
        elif char_count > 500:
            self.char_counter.setStyleSheet("color: #e67e22; font-style: italic;") # Orange for longer prompts
        else:
            self.char_counter.setStyleSheet("color: #666; font-style: italic;") # Default gray
            
        self.char_counter.setText(f"{char_count} characters | {word_count} words")
    
    def submit(self):
        """Submit the input text."""
        text = self.text_input.toPlainText().strip()
        if text:
            self.result = {"text": text, "submitted": True}
            self.dialog.accept()
    
    def on_dialog_closed(self, result):
        """Handle dialog close event."""
        # If the dialog was closed without submitting, ensure result is properly set
        if not self.result["submitted"]:
            self.result = {"text": "", "submitted": False}


class EnterKeyFilter(QObject):
    """Event filter to handle Enter key press."""
    
    def __init__(self, dialog):
        super().__init__()
        self.dialog = dialog
    
    def eventFilter(self, obj, event):
        """Filter events to catch Enter key press or Cmd+Enter."""
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Return:
            # Submit on plain Enter or Cmd+Enter
            if not event.modifiers() or event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                self.dialog.submit()
                return True
        return super().eventFilter(obj, event)
