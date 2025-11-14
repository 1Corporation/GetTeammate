from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ProfileCreate(BaseModel):
    user_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None
    photo_file_id: str
    description: str

class ProfileDB(ProfileCreate):
    id: int
    status: str = Field(default="pending")
    created_at: datetime
