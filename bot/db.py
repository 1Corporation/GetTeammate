import aiosqlite
import os
from datetime import datetime
from typing import Optional

class Database:
    _conn: Optional[aiosqlite.Connection] = None

    @classmethod
    async def init(cls, db_path: str):
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        cls._conn = await aiosqlite.connect(db_path)
        # Return rows as dict-like
        cls._conn.row_factory = aiosqlite.Row
        await cls._create_tables()

    @classmethod
    async def _create_tables(cls):
        assert cls._conn is not None
        await cls._conn.executescript("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            full_name TEXT,
            photo_file_id TEXT,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'pending', -- pending, approved, rejected
            created_at TEXT NOT NULL
        );
        """)
        await cls._conn.commit()

    @classmethod
    async def get_conn(cls) -> aiosqlite.Connection:
        if cls._conn is None:
            raise RuntimeError("Database not initialized")
        return cls._conn

    @classmethod
    async def close(cls):
        if cls._conn:
            await cls._conn.close()
            cls._conn = None
