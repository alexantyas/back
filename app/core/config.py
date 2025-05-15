import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings  # ✅ заменено
from typing import List

# Загружаем переменные окружения
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Tournament System"
    DEBUG: bool = True

    # База данных
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:1s2a3n4e5k@localhost:5432/arena_db")

    # Безопасность
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 часа

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8080"]

    model_config = {
        "case_sensitive": True
    }

settings = Settings()
