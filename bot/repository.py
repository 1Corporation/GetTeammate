from typing import List, Optional
from datetime import datetime
from bot.db import Database
from bot.models import ProfileCreate, ProfileDB
import aiosqlite

class ProfilesRepository:
    """Repository for profiles. Singleton-like usage via class methods."""

    @staticmethod
    async def create(profile: ProfileCreate) -> int:
        conn = await Database.get_conn()
        cur = await conn.execute(
            "INSERT INTO profiles (user_id, username, full_name, photo_file_id, description, status, created_at) VALUES (?, ?, ?, ?, ?, 'pending', ?)",
            (profile.user_id, profile.username, profile.full_name, profile.photo_file_id, profile.description, datetime.utcnow().isoformat()),
        )
        await conn.commit()
        return cur.lastrowid

    @staticmethod
    async def get_by_id(profile_id: int) -> Optional[ProfileDB]:
        conn = await Database.get_conn()
        cur = await conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
        row = await cur.fetchone()
        if row:
            return ProfilesRepository._row_to_profile(row)
        return None

    @staticmethod
    async def list_pending() -> List[ProfileDB]:
        conn = await Database.get_conn()
        cur = await conn.execute("SELECT * FROM profiles WHERE status = 'pending' ORDER BY created_at ASC")
        rows = await cur.fetchall()
        return [ProfilesRepository._row_to_profile(r) for r in rows]

    @staticmethod
    async def list_approved(limit: int = 50, offset: int = 0) -> List[ProfileDB]:
        conn = await Database.get_conn()
        cur = await conn.execute("SELECT * FROM profiles WHERE status = 'approved' ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset))
        rows = await cur.fetchall()
        return [ProfilesRepository._row_to_profile(r) for r in rows]

    @staticmethod
    async def set_status(profile_id: int, status: str):
        conn = await Database.get_conn()
        await conn.execute("UPDATE profiles SET status = ? WHERE id = ?", (status, profile_id))
        await conn.commit()

    @staticmethod
    def _row_to_profile(row: aiosqlite.Row) -> ProfileDB:
        return ProfileDB(
            id=row["id"],
            user_id=row["user_id"],
            username=row["username"],
            full_name=row["full_name"],
            photo_file_id=row["photo_file_id"],
            description=row["description"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
