#!/usr/bin/env python3
"""
History dialog for the AI Prompt Assistant.
Allows users to view, reuse, and delete their past prompts.
"""

import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMessageBox, QMenu, QWidget, QSplitter, QTextEdit
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QFont, QColor
from src.settings_manager import SettingsManager


class HistoryDialog(QDialog):
    """Dialog for viewing and managing input history."""
    
    prompt_selected = pyqtSignal(str)
    
    def __init__(self, history_manager, parent=None):
        """Initialize the history dialog."""
        super().__init__(parent)
        self.history_manager = history_manager
        self.selected_entry = None
        
        # Initialize settings for localization
        self.settings = SettingsManager()
        self.localized_strings = self.settings.load_localization()
        
        self.setWindowTitle(self.get_string("settings.history.dialog_title", "Prompt History"))
        self.setMinimumSize(800, 500)
        self.setup_ui()
        self.load_history()
    
    def get_string(self, key_path, default=""):
        """Get a localized string."""
        return self.settings.get_string(key_path, default)
    
    def setup_ui(self):
        """Set up the UI components."""
        main_layout = QVBoxLayout(self)
        
        # Create splitter for table and preview
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Create table widget
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            self.get_string("settings.history.date_column", "Date"),
            self.get_string("settings.history.prompt_column", "Prompt"),
            self.get_string("settings.history.service_column", "AI Service")
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        splitter.addWidget(self.table)
        
        # Create preview area
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        preview_header = QHBoxLayout()
        preview_label = QLabel(self.get_string("settings.history.preview_label", "Preview:"))
        preview_label.setFont(QFont("", 0, QFont.Weight.Bold))
        preview_header.addWidget(preview_label)
        preview_header.addStretch()
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText(self.get_string("settings.history.no_history", "Select a prompt to preview"))
        
        preview_layout.addLayout(preview_header)
        preview_layout.addWidget(self.preview_text)
        
        splitter.addWidget(preview_widget)
        
        # Set initial sizes
        splitter.setSizes([300, 200])
        
        main_layout.addWidget(splitter)
        
        # Create buttons
        button_layout = QHBoxLayout()
        
        self.reuse_button = QPushButton(self.get_string("settings.history.reuse_button", "Reuse Prompt"))
        self.reuse_button.setEnabled(False)
        self.reuse_button.clicked.connect(self.reuse_prompt)
        
        self.delete_button = QPushButton(self.get_string("settings.history.delete_button", "Delete"))
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_prompt)
        
        self.clear_all_button = QPushButton(self.get_string("settings.history.clear_all_button", "Clear All"))
        self.clear_all_button.clicked.connect(self.clear_all_prompts)
        
        self.close_button = QPushButton(self.get_string("settings.history.close_button", "Close"))
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.reuse_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_all_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        main_layout.addLayout(button_layout)
    
    def load_history(self):
        """Load history entries into the table."""
        entries = self.history_manager.get_entries()
        
        self.table.setRowCount(len(entries))
        
        for i, entry in enumerate(entries):
            # Date column
            date_item = QTableWidgetItem(entry["datetime"])
            date_item.setData(Qt.ItemDataRole.UserRole, entry["id"])
            self.table.setItem(i, 0, date_item)
            
            # Prompt column - truncate if too long
            prompt_text = entry["input_text"]
            if len(prompt_text) > 50:
                display_text = prompt_text[:47] + "..."
            else:
                display_text = prompt_text
                
            prompt_item = QTableWidgetItem(display_text)
            prompt_item.setToolTip(prompt_text)
            self.table.setItem(i, 1, prompt_item)
            
            # AI Service column
            service_item = QTableWidgetItem(entry["ai_service"])
            self.table.setItem(i, 2, service_item)
    
    def on_selection_changed(self):
        """Handle selection change in the table."""
        selected_rows = self.table.selectedItems()
        
        if selected_rows:
            row = self.table.currentRow()
            entry_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            self.selected_entry = self.history_manager.get_entry(entry_id)
            
            if self.selected_entry:
                self.preview_text.setText(self.selected_entry["input_text"])
                self.reuse_button.setEnabled(True)
                self.delete_button.setEnabled(True)
        else:
            self.selected_entry = None
            self.preview_text.clear()
            self.reuse_button.setEnabled(False)
            self.delete_button.setEnabled(False)
    
    def show_context_menu(self, position):
        """Show context menu for the table."""
        if not self.table.selectedItems():
            return
            
        context_menu = QMenu(self)
        
        reuse_action = QAction(self.get_string("settings.history.reuse_button", "Reuse Prompt"), self)
        reuse_action.triggered.connect(self.reuse_prompt)
        
        delete_action = QAction(self.get_string("settings.history.delete_button", "Delete"), self)
        delete_action.triggered.connect(self.delete_prompt)
        
        context_menu.addAction(reuse_action)
        context_menu.addAction(delete_action)
        
        context_menu.exec(self.table.viewport().mapToGlobal(position))
    
    def reuse_prompt(self):
        """Reuse the selected prompt."""
        if self.selected_entry:
            self.prompt_selected.emit(self.selected_entry["input_text"])
            self.accept()
    
    def delete_prompt(self):
        """Delete the selected prompt."""
        if self.selected_entry:
            confirm = QMessageBox.question(
                self,
                self.get_string("settings.history.delete_button", "Confirm Delete"),
                self.get_string("settings.history.confirm_delete", "Are you sure you want to delete this prompt?"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm == QMessageBox.StandardButton.Yes:
                # Add delete_entry method to history_manager
                self.history_manager.delete_entry(self.selected_entry["id"])
                self.load_history()
                self.selected_entry = None
                self.preview_text.clear()
                self.reuse_button.setEnabled(False)
                self.delete_button.setEnabled(False)
    
    def clear_all_prompts(self):
        """Clear all prompts from history."""
        confirm = QMessageBox.question(
            self,
            self.get_string("settings.history.clear_all_button", "Confirm Clear All"),
            self.get_string("settings.history.confirm_clear_all", "Are you sure you want to delete ALL prompts from history? This cannot be undone."),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.history_manager.clear_history()
            self.load_history()
            self.selected_entry = None
            self.preview_text.clear()
            self.reuse_button.setEnabled(False)
            self.delete_button.setEnabled(False)


def main():
    """Run the history dialog as a standalone application (for testing)."""
    from history_manager import HistoryManager
    
    app = QApplication(sys.argv)
    history_manager = HistoryManager()
    
    # Add some test entries if none exist
    entries = history_manager.get_entries()
    if not entries:
        history_manager.add_entry("Test prompt 1", "Rephrased test prompt 1", "chatgpt")
        history_manager.add_entry("Test prompt 2", "Rephrased test prompt 2", "chatgpt")
        history_manager.add_entry("Test prompt 3", "Rephrased test prompt 3", "chatgpt")
    
    dialog = HistoryDialog(history_manager)
    dialog.exec()


if __name__ == "__main__":
    main()
