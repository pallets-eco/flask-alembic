from __future__ import annotations

import collections.abc as c
import os
import shutil
from pathlib import Path

import pytest
import sqlalchemy as sa
from flask import Flask
from flask.ctx import AppContext
from flask.testing import FlaskCliRunner
from flask_sqlalchemy_lite import SQLAlchemy

from flask_alembic import Alembic


@pytest.fixture
def app(request: pytest.FixtureRequest, tmp_path: Path) -> Flask:
    app = Flask(request.module.__name__, root_path=os.fspath(tmp_path))
    app.config["SQLALCHEMY_ENGINES"] = {
        "default": "sqlite://",
        "other": "sqlite://",
    }
    return app


@pytest.fixture
def app_ctx(app: Flask) -> c.Iterator[AppContext]:
    with app.app_context() as ctx:
        yield ctx


@pytest.fixture
def db(app: Flask) -> c.Iterator[SQLAlchemy]:
    yield SQLAlchemy(app)


@pytest.fixture
def metadata() -> sa.MetaData:
    return sa.MetaData()


@pytest.fixture(autouse=True)
def todo_table(metadata: sa.MetaData) -> sa.Table:
    return sa.Table(
        "todo",
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("text", sa.String),
    )


@pytest.fixture
def alembic(
    app: Flask, db: SQLAlchemy, metadata: sa.MetaData, tmp_path: Path
) -> Alembic:
    shutil.copytree(Path(__file__).parent / "migrations", tmp_path / "migrations")
    return Alembic(app, metadatas=metadata)


@pytest.fixture
def runner(app: Flask) -> c.Iterator[FlaskCliRunner]:
    """Create a test CLI runner."""
    yield app.test_cli_runner()
