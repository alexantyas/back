from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import engine
from app.db.base import Base
from app.routers import (
    users,
    teams,
    competitions,
    applications,
    matches,
    auth,
    additional_info,
    location,
    judges,
    
)
from app.core.config import settings

# Импорт всех моделей заставляет SQLAlchemy их зарегистрировать
from app import models  

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/docs",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite по умолчанию
        "http://localhost:8080",  # Vue CLI
        "http://localhost:8082",  # ваш случай!
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Автоматически создаём таблицы (если вы не используете Alembic)
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Подключаем роутеры (в том числе competitions.router с брэкет-эндпоинтами)
app.include_router(users.router)
app.include_router(teams.router)
app.include_router(competitions.router)
app.include_router(applications.router)
app.include_router(matches.router)
app.include_router(auth.router)
app.include_router(additional_info.router)
app.include_router(location.router)
app.include_router(judges.router)


