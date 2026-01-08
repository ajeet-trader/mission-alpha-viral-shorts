"""
SQLite Database Provider

Simple file-based database for local development.
"""

import sqlite3
import json
from typing import Dict, List, Optional
from pathlib import Path
from app.core.interfaces import IDatabaseProvider
from app.core.logger import log_step, log_success
import logging

logger = logging.getLogger(__name__)


class SQLiteProvider(IDatabaseProvider):
    """SQLite database provider."""
    
    def __init__(self, config):
        self.config = config
        db_path = Path(config.sqlite.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
        log_success(f"SQLite connected: {db_path}")
    
    def _init_tables(self):
        """Create tables if not exist."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS content (
                id TEXT PRIMARY KEY,
                type TEXT,
                title TEXT,
                body TEXT,
                source TEXT,
                score REAL,
                created_at TEXT
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id TEXT PRIMARY KEY,
                content_title TEXT,
                script_hook TEXT,
                audio_path TEXT,
                video_path TEXT,
                duration REAL,
                resolution TEXT,
                created_at TEXT
            )
        """)
        
        self.conn.commit()
    
    async def insert(self, table: str, data: Dict) -> str:
        """Insert record."""
        log_step(f"💾 Inserting into {table}")
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        cursor = self.conn.execute(sql, list(data.values()))
        self.conn.commit()
        
        return data.get('id', str(cursor.lastrowid))
    
    async def query(self, table: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Query records."""
        log_step(f"🔍 Querying {table}")
        
        sql = f"SELECT * FROM {table}"
        params = []
        
        if filters:
            conditions = [f"{k} = ?" for k in filters.keys()]
            sql += " WHERE " + " AND ".join(conditions)
            params = list(filters.values())
        
        cursor = self.conn.execute(sql, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    async def update(self, table: str, id: str, data: Dict) -> bool:
        """Update record."""
        log_step(f"📝 Updating {table}/{id}")
        
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE id = ?"
        
        cursor = self.conn.execute(sql, list(data.values()) + [id])
        self.conn.commit()
        
        return cursor.rowcount > 0
