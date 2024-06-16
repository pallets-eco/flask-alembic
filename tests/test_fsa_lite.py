from __future__ import annotations

import os
from pathlib import Path

import pytest
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

from flask_alembic import Alembic

try:
    from flask_sqlalchemy_lite import SQLAlchemy
except ImportError:
    pytest.skip("flask_sqlalchemy_lite not available", allow_module_level=True)


@pytest.fixture
def app(app: Flask) -> Flask:
    app.config["SQLALCHEMY_ENGINES"] = {
        "default": "sqlite://",
        "other": "sqlite://",
    }
    return app


@pytest.fixture
def db(app: Flask) -> SQLAlchemy:
    return SQLAlchemy(app)


class Model(DeclarativeBase):
    pass


class Other(DeclarativeBase):
    pass


@pytest.mark.usefixtures("app_ctx")
def test_metadata_required(app: Flask) -> None:
    """Passing a metadata is required with Flask-SQLAlchemy-Lite."""
    alembic = Alembic(app)

    with pytest.raises(RuntimeError, match="pass 'metadatas' when"):
        assert alembic.migration_context


@pytest.mark.usefixtures("app_ctx", "db")
def test_uses_engines(app: Flask) -> None:
    """Engines from Flask-SQLAlchemy-Lite are used if none are passed."""
    alembic = Alembic(app, metadatas=Model.metadata)
    assert alembic.migration_context


@pytest.mark.usefixtures("app_ctx")
def test_engine_required(app: Flask) -> None:
    """Flask-SQLAlchemy-Lite must configure an engine."""
    del app.config["SQLALCHEMY_ENGINES"]
    SQLAlchemy(app, require_default_engine=False)
    alembic = Alembic(app, metadatas=Model.metadata)

    with pytest.raises(RuntimeError, match="engines configured"):
        assert alembic.migration_context


@pytest.mark.usefixtures("app_ctx", "db")
def test_missing_engine(app: Flask) -> None:
    """There must be an engine matching each metadata name."""
    alembic = Alembic(
        app, metadatas={"default": Model.metadata, "missing": Other.metadata}
    )

    with pytest.raises(RuntimeError, match="Missing engine config"):
        assert alembic.migration_context


@pytest.mark.usefixtures("app_ctx", "db")
def test_override_engines(tmp_path: Path, app: Flask) -> None:
    """A passed engine overrides one from Flask-SQLAlchemy-Lite."""
    db_path = os.fspath(tmp_path / "default.sqlite")
    engine = create_engine(f"sqlite:///{db_path}")
    alembic = Alembic(app, metadatas=Model.metadata, engines=engine)
    assert alembic.migration_context.connection is not None
    assert alembic.migration_context.connection.engine.url.database == db_path
