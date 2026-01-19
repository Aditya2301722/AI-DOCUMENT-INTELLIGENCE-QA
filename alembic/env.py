

import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# -----------------------------
# Alembic Config
# -----------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -----------------------------
# ADD backend/ TO PYTHON PATH
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
sys.path.append(str(BACKEND_DIR))

# -----------------------------
# IMPORT MODELS (SYNC SAFE)
# -----------------------------
from app.models.base import Base
from app.models.customer import Customer
from app.models.session import Session
from app.models.message import Message

target_metadata = Base.metadata

# -----------------------------
# OFFLINE MIGRATIONS
# -----------------------------
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# -----------------------------
# ONLINE MIGRATIONS (SYNC ENGINE)
# -----------------------------
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

# -----------------------------
# ENTRY POINT
# -----------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
