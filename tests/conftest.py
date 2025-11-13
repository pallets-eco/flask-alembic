from __future__ import annotations

import collections.abc as c
import gc
import os
from pathlib import Path

import pytest
from flask import Flask
from flask.ctx import AppContext
from flask_sqlalchemy_lite import SQLAlchemy

from flask_alembic import Alembic


@pytest.fixture
def app(request: pytest.FixtureRequest, tmp_path: Path) -> c.Iterator[Flask]:
    app = Flask(request.module.__name__, root_path=os.fspath(tmp_path))
    app.config["SQLALCHEMY_ENGINES"] = {
        "default": "sqlite://",
        "other": "sqlite://",
    }
    yield app
    gc.collect()


@pytest.fixture
def app_ctx(app: Flask) -> c.Iterator[AppContext]:
    with app.app_context() as ctx:
        yield ctx


@pytest.fixture
def db(app: Flask) -> c.Iterator[SQLAlchemy]:
    db = SQLAlchemy(app)
    yield db

    with app.app_context():
        for engine in db.engines.values():
            engine.dispose()


@pytest.fixture
def alembic(app: Flask, db: SQLAlchemy) -> Alembic:
    return Alembic(app)
