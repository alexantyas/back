import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from alembic import context
import os
import sys

# добавляем путь к app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# импорт настроек и моделей
from app.db import Base
from app.models import user, team, application, competition, match

# Alembic Config object
config = context.config

# Подключаем конфиг логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Указываем метаданные
target_metadata = Base.metadata

# Получаем SQLAlchemy URL из alembic.ini
def get_url():
    return config.get_main_option("sqlalchemy.url")

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    from sqlalchemy import create_engine

    connectable = create_engine(
        get_url(),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
