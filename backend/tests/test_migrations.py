from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text

from app import migrate
from app.database import Base, engine

INVESTOR_COLUMNS = {c.name for c in Base.metadata.tables["Investors"].columns}


def test_models_match_migrations():
    """Fails when a model changes without a new migration (the conftest DB came from migrations).

    Column types are not compared: SQLite reflects UUID as NUMERIC. Tables, columns, nullability
    and constraints are.
    """
    with engine.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn, opts={"compare_type": False}), Base.metadata)
    assert diff == []


def test_migrated_schema_has_both_tables_and_version(tmp_path, monkeypatch):
    fresh = create_engine(f"sqlite:///{tmp_path}/fresh.db")
    monkeypatch.setattr(migrate, "engine", fresh)
    migrate.run()
    insp = inspect(fresh)
    assert {"Investors", "Firms", "alembic_version"} <= set(insp.get_table_names())
    assert {c["name"] for c in insp.get_columns("Investors")} == INVESTOR_COLUMNS
    with fresh.connect() as conn:
        assert conn.execute(text("select version_num from alembic_version")).scalar() == migrate.BASELINE


def test_database_created_before_alembic_is_stamped_not_recreated(tmp_path, monkeypatch):
    legacy = create_engine(f"sqlite:///{tmp_path}/legacy.db")
    Base.metadata.create_all(legacy)  # how the app used to build the schema
    with legacy.begin() as conn:
        conn.execute(text(
            'insert into "Firms" (cognito_sub, name, email) values (:i, :n, :e)'
        ), {"i": "0" * 32, "n": "Old Firm", "e": "old@example.com"})

    monkeypatch.setattr(migrate, "engine", legacy)
    migrate.run()  # must not try to CREATE TABLE again
    migrate.run()  # and is safe to repeat

    with legacy.connect() as conn:
        assert conn.execute(text("select version_num from alembic_version")).scalar() == migrate.BASELINE
        assert conn.execute(text('select name from "Firms"')).scalar() == "Old Firm"


def test_partial_schema_is_refused(tmp_path, monkeypatch):
    partial = create_engine(f"sqlite:///{tmp_path}/partial.db")
    Base.metadata.tables["Firms"].create(partial)
    monkeypatch.setattr(migrate, "engine", partial)
    try:
        migrate.run()
    except RuntimeError as e:
        assert "part of the schema" in str(e)
    else:
        raise AssertionError("expected RuntimeError")
