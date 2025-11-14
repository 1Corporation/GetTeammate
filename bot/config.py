from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    BOT_TOKEN: str = ""
    ADMINS: List[int] = []
    DATABASE_URL: str = "./database.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
