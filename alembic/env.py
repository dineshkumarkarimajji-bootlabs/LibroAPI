import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from model import Base  # Import your SQLAlchemy Base here

# Alembic Config object
config = context.config

# Use DATABASE_URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Dinesh2003@localhost:5433/karimajjidineshkumar")

# Target metadata for 'autogenerate'
target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        {"sqlalchemy.url": DATABASE_URL},  # Pass URL here
        prefix='sqlalchemy.',
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
