"""Bring the database schema up to date: `python -m app.migrate`.

Databases created before Alembic (by Base.metadata.create_all) already have the tables but
no alembic_version row. Those are stamped at the baseline revision instead of re-creating
the tables, then upgraded normally.
"""
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.database import engine

BASELINE = "0001"
TABLES = {"Investors", "Firms"}
_ALEMBIC_INI = Path(__file__).resolve().parent.parent / "alembic.ini"


def run() -> None:
    cfg = Config(str(_ALEMBIC_INI))
    with engine.begin() as connection:
        cfg.attributes["connection"] = connection
        existing = set(inspect(connection).get_table_names())
        if "alembic_version" not in existing:
            present = TABLES & existing
            if present == TABLES:
                command.stamp(cfg, BASELINE)
            elif present:
                raise RuntimeError(
                    f"Database has only part of the schema ({sorted(present)}); "
                    "fix it by hand before running migrations."
                )
        command.upgrade(cfg, "head")


if __name__ == "__main__":
    run()
