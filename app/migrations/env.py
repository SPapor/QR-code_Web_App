import asyncio
from logging.config import fileConfig

import sqlalchemy as sa
from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

import auth.tables  # noqa: F401  (populate metadata)
import google_auth.tables  # noqa: F401
import qr_code.tables  # noqa: F401
import telegram_auth.tables  # noqa: F401
import user.tables  # noqa: F401
from core.database import metadata
from core.settings import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.DB_URI)

target_metadata = metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def compare_type(ctx, inspected_column, metadata_column, inspected_type, metadata_type) -> bool | None:
    # sqlite has no UUID type: it comes back as NUMERIC on reflection,
    # which is not a real difference — don't let autogenerate flag it
    if ctx.dialect.name == "sqlite" and isinstance(metadata_type, sa.UUID):
        return False
    return None


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # sqlite can't ALTER most things in place; batch mode recreates the table
        render_as_batch=connection.dialect.name == "sqlite",
        compare_type=compare_type,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
