# migrations/env.py — NAVAM Alembic async migration environment
# PostgreSQL 16 + PostGIS 3.4 | SQLAlchemy 2.0 async | asyncpg driver
#
# Usage:
#   export DATABASE_URL="postgresql+asyncpg://navam:secret@localhost:5432/navam"
#   alembic upgrade head

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
import logging
from logging.config import fileConfig

# Load .env from project root or local directory
root_env = Path(__file__).resolve().parents[3] / ".env"
if root_env.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(root_env, override=True)
    except ImportError:
        pass
else:
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
    except ImportError:
        pass

# Add apps/api/src to sys.path
api_src = Path(__file__).resolve().parents[1] / "src"
if str(api_src) not in sys.path:
    sys.path.insert(0, str(api_src))

from sqlalchemy import pool, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
from alembic import context

# ---------------------------------------------------------------------------
# Alembic Config object (gives access to values in alembic.ini)
# ---------------------------------------------------------------------------
config = context.config

# Set up Python logging from alembic.ini [loggers] section
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

log = logging.getLogger("alembic.env")

# ---------------------------------------------------------------------------
# Resolve DATABASE_URL from environment (takes priority over alembic.ini)
# ---------------------------------------------------------------------------
_db_url = os.environ.get("DATABASE_URL")
if _db_url:
    # Ensure asyncpg driver is used; accept plain postgresql:// or asyncpg variant
    if _db_url.startswith("postgresql://") or _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        _db_url = _db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    if "sslmode=require" in _db_url:
        _db_url = _db_url.replace("sslmode=require", "ssl=require")
    if "channel_binding=require" in _db_url:
        _db_url = _db_url.replace("&channel_binding=require", "").replace("channel_binding=require", "")
    config.set_main_option("sqlalchemy.url", _db_url)

# ---------------------------------------------------------------------------
# Import application metadata so Alembic can autogenerate diffs
# ---------------------------------------------------------------------------
try:
    from navam_api.models import Base  # type: ignore[import]
    target_metadata = Base.metadata
    log.info("Loaded SQLAlchemy metadata from navam_api.models")
except ImportError:
    # Models package not yet available — run in manual SQL mode
    log.warning(
        "navam_api.models not found; autogenerate will be disabled. "
        "Use op.execute() migrations for schema changes."
    )
    target_metadata = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# PostGIS type registration helper
# ---------------------------------------------------------------------------
def _include_object(object, name, type_, reflected, compare_to):  # noqa: A002
    """
    Exclude PostGIS internal tables from autogenerate comparisons.
    Prevents alembic diff noise from geography_columns, geometry_columns, etc.
    """
    postgis_tables = {
        "geography_columns",
        "geometry_columns",
        "raster_columns",
        "raster_overviews",
        "spatial_ref_sys",
    }
    if type_ == "table" and name in postgis_tables:
        return False
    return True


# ---------------------------------------------------------------------------
# Offline migration (generates SQL script without a live DB connection)
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode — emit SQL to stdout/file without
    actually connecting to the database.  Useful for generating reviewed
    migration scripts for production DBA approval.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=_include_object,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


from sqlalchemy import create_engine

def run_migrations_online() -> None:
    """Run migrations in 'online' mode using synchronous psycopg2 connection."""
    url = config.get_main_option("sqlalchemy.url")
    if "+asyncpg" in url:
        url = url.replace("+asyncpg", "")
    if "ssl=require" in url:
        url = url.replace("ssl=require", "sslmode=require")
    if "channel_binding=require" in url:
        url = url.replace("&channel_binding=require", "").replace("channel_binding=require", "")

    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS navam;"))
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS audit;"))
        connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=_include_object,
            compare_type=True,
            compare_server_default=True,
            include_schemas=True,
            version_table_schema="navam",
        )
        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------------------------
# Dispatch: offline vs. online
# ---------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
