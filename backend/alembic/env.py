from alembic import context

import app.models  # noqa: F401  (registers the tables on Base.metadata)
from app.database import Base, DATABASE_URL, engine

target_metadata = Base.metadata

# SQLite cannot ALTER most things in place; batch mode recreates the table instead.
_batch = engine.dialect.name == "sqlite"


def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=_batch,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # A connection handed in by app.migrate (or tests) is reused; otherwise open our own.
    connection = context.config.attributes.get("connection")
    if connection is not None:
        _run(connection)
        return
    with engine.connect() as connection:
        _run(connection)


def _run(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=_batch,
        # SQLite reflects UUID columns as NUMERIC, so type comparison is Postgres-only
        compare_type=not _batch,
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
