from __future__ import annotations

import collections.abc as c
import os
import typing as t
from pathlib import Path

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from flask_alembic import Alembic


@pytest.fixture
def db(app: Flask) -> c.Iterator[SQLAlchemy]:
    app.config["SQLALCHEMY_BINDS"] = {
        None: "sqlite://",
        "other": "sqlite://",
    }
    db = SQLAlchemy(app)
    yield db

    with app.app_context():
        for engine in db.engines.values():
            engine.dispose()


@pytest.fixture
def Book(db: SQLAlchemy) -> type[t.Any]:
    class Book(db.Model):  # type: ignore[name-defined, misc]
        id = db.Column(db.Integer, primary_key=True)

    return Book


@pytest.fixture
def User(db: SQLAlchemy) -> type[t.Any]:
    class User(db.Model):  # type: ignore[name-defined, misc]
        __bind_key__ = "other"
        id = db.Column(db.Integer, primary_key=True)

    return User


@pytest.mark.usefixtures("app_ctx", "db")
def test_uses_binds(app: Flask) -> None:
    """Engines and metadata from Flask-SQLAlchemy are used if none are passed."""
    alembic = Alembic(app)
    assert alembic.migration_context


@pytest.mark.usefixtures("app_ctx", "User")
def test_missing_engine(app: Flask, db: SQLAlchemy) -> None:
    """There must be an engine matching each metadata name."""
    alembic = Alembic(
        app, metadatas={"default": db.metadata, "missing": db.metadatas["other"]}
    )

    with pytest.raises(RuntimeError, match="Missing engine config"):
        assert alembic.migration_context


@pytest.mark.usefixtures("app_ctx")
def test_override_engines(tmp_path: Path, app: Flask, db: SQLAlchemy) -> None:
    """A passed engine overrides one from Flask-SQLAlchemy."""
    db_path = os.fspath(tmp_path / "default.sqlite")
    engine = create_engine(f"sqlite:///{db_path}")
    alembic = Alembic(app, engines=engine)
    assert alembic.migration_context.connection is not None
    assert alembic.migration_context.connection.engine.url.database == db_path
    alembic.migration_context.connection.close()
    engine.dispose()
