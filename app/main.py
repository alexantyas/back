from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from app.routers import users, teams, competitions, applications, matches, auth
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app import models  # 👈 импорт всех моделей (ВАЖНО!)
from app.routers import additional_info, location

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/docs",
    redoc_url=None
)

# === CORS ===
# Используем ALLOWED_ORIGINS из .env или вручную подставляем fallback


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Подключение роутеров ===
app.include_router(users.router)
app.include_router(teams.router)
app.include_router(competitions.router)
app.include_router(applications.router)
app.include_router(matches.router)
app.include_router(auth.router)
app.include_router(additional_info.router)
app.include_router(location.router)
