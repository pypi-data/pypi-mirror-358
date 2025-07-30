import sqlite3
import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

@dataclass
class Case:
    case_id: int
    user_id: int
    moderator_id: int
    action: str
    reason: str
    timestamp: str
    duration: Optional[str] = None

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Cases table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cases (
                    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    moderator_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    duration TEXT
                )
            ''')

            # Warnings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS warnings (
                    warning_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    moderator_id INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    active BOOLEAN DEFAULT 1
                )
            ''')

            # Guild settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS guild_settings (
                    guild_id INTEGER PRIMARY KEY,
                    prefix TEXT DEFAULT '!',
                    log_channel_id INTEGER,
                    enabled_commands TEXT
                )
            ''')

            conn.commit()

    def add_case(self, user_id: int, moderator_id: int, action: str, reason: str, duration: str = None) -> int:
        """Add a moderation case"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO cases (user_id, moderator_id, action, reason, duration)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, moderator_id, action, reason, duration))
            conn.commit()
            return cursor.lastrowid

    def get_cases(self, user_id: int = None, limit: int = 10) -> List[Case]:
        """Get moderation cases"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if user_id:
                cursor.execute('''
                    SELECT * FROM cases WHERE user_id = ? 
                    ORDER BY timestamp DESC LIMIT ?
                ''', (user_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM cases ORDER BY timestamp DESC LIMIT ?
                ''', (limit,))

            rows = cursor.fetchall()
            return [Case(*row) for row in rows]

    def add_warning(self, user_id: int, moderator_id: int, reason: str) -> int:
        """Add a warning"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO warnings (user_id, moderator_id, reason)
                VALUES (?, ?, ?)
            ''', (user_id, moderator_id, reason))
            conn.commit()
            return cursor.lastrowid

    def get_warnings(self, user_id: int) -> List[Dict[str, Any]]:
        """Get active warnings for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM warnings WHERE user_id = ? AND active = 1
                ORDER BY timestamp DESC
            ''', (user_id,))

            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def remove_warning(self, warning_id: int) -> bool:
        """Remove a warning"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE warnings SET active = 0 WHERE warning_id = ?
            ''', (warning_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_user_stats(self, user_id: int) -> Dict[str, int]:
        """Get user moderation statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT action, COUNT(*) as count FROM cases 
                WHERE user_id = ? GROUP BY action
            ''', (user_id,))

            return dict(cursor.fetchall())