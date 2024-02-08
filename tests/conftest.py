import os
from pathlib import Path

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_alembic import Alembic


@pytest.fixture
def app(request: pytest.FixtureRequest, tmp_path: Path) -> Flask:
    app = Flask(request.module.__name__, root_path=os.fspath(tmp_path))
    app.config.update(
        SQLALCHEMY_DATABASE_URI="sqlite://",
        SQLALCHEMY_RECORD_QUERIES=False,
    )
    return app


@pytest.fixture
def db(app: Flask, request: pytest.FixtureRequest) -> SQLAlchemy:
    return SQLAlchemy(app)


@pytest.fixture
def alembic(app: Flask, db: SQLAlchemy) -> Alembic:
    return Alembic(app)
