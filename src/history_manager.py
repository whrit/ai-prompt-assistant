#!/usr/bin/env python3
"""
History manager for the AI Prompt Assistant.
Handles storing and retrieving input history.
"""

import os
import sqlite3
import time
from datetime import datetime


class HistoryManager:
    """Manages input history using SQLite database."""
    
    def __init__(self):
        """Initialize the history manager."""
        self.db_path = os.path.expanduser(
            "~/Library/Application Support/AI Prompt Assistant/history/input_history.db"
        )
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure the database and tables exist."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Connect to database and create table if it doesn't exist
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS input_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_text TEXT NOT NULL,
                rephrased_text TEXT,
                ai_service TEXT NOT NULL,
                timestamp INTEGER NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_entry(self, input_text, rephrased_text=None, ai_service="chatgpt"):
        """Add a new entry to the history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = int(time.time())
        
        cursor.execute(
            "INSERT INTO input_history (input_text, rephrased_text, ai_service, timestamp) VALUES (?, ?, ?, ?)",
            (input_text, rephrased_text, ai_service, timestamp)
        )
        
        conn.commit()
        entry_id = cursor.lastrowid
        conn.close()
        
        return entry_id
    
    def get_entries(self, limit=50, offset=0):
        """Get entries from the history."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM input_history ORDER BY timestamp DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        
        entries = []
        for row in cursor.fetchall():
            entries.append({
                "id": row["id"],
                "input_text": row["input_text"],
                "rephrased_text": row["rephrased_text"],
                "ai_service": row["ai_service"],
                "timestamp": row["timestamp"],
                "datetime": datetime.fromtimestamp(row["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            })
        
        conn.close()
        return entries
    
    def get_entry(self, entry_id):
        """Get a specific entry by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM input_history WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        
        if row:
            entry = {
                "id": row["id"],
                "input_text": row["input_text"],
                "rephrased_text": row["rephrased_text"],
                "ai_service": row["ai_service"],
                "timestamp": row["timestamp"],
                "datetime": datetime.fromtimestamp(row["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            entry = None
        
        conn.close()
        return entry
    
    def delete_entry(self, entry_id):
        """Delete a specific entry by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM input_history WHERE id = ?", (entry_id,))
        
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        
        return deleted
    
    def clear_history(self):
        """Clear all history entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM input_history")
        
        conn.commit()
        conn.close()
