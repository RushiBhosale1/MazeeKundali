"""
db/migrations/env.py
Alembic migration environment — supports async SQLAlchemy engine.
"""
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Load .env file so DATABASE_URL_SYNC is available
import os
from pathlib import Path
_env_file = Path(__file__).parent.parent.parent / ".env"
if _env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_file)

# Import all models so Alembic can detect them
from db.models import Base  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url():
    """Get DB URL from environment, defaulting to sync URL for migrations."""
    import os
    return os.environ.get(
        "DATABASE_URL_SYNC",
        "postgresql://kundali_user:kundali_pass@localhost:5432/kundali_db",
    )


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    from sqlalchemy.ext.asyncio import create_async_engine
    url = get_url()
    # Convert to asyncpg driver
    url = url.replace("postgresql://", "postgresql+asyncpg://")
    # asyncpg does not support channel_binding or sslmode — strip them
    url = url.replace("&channel_binding=require", "").replace("?channel_binding=require", "")
    url = url.replace("sslmode=require", "ssl=require")
    engine = create_async_engine(url, poolclass=pool.NullPool)
    async with engine.connect() as conn:
        await conn.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
