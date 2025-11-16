from __future__ import annotations

import collections.abc as c
import os
import shutil
from pathlib import Path

import pytest
from app import Model
from flask import Flask
from flask.ctx import AppContext
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
def alembic(app: Flask, db: SQLAlchemy, tmp_path: Path) -> Alembic:
    shutil.copytree(Path(__file__).parent / "migrations", tmp_path / "migrations")
    return Alembic(app, metadatas=Model.metadata)
