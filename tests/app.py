from __future__ import annotations

import shutil
import typing as t
from itertools import count

import sqlalchemy as sa
from flask import Flask
from flask_sqlalchemy_lite import SQLAlchemy
from sqlalchemy import orm

from flask_alembic import Alembic


class Model(orm.DeclarativeBase):
    pass


db = SQLAlchemy()
alembic = Alembic(metadatas=Model.metadata)


def create_app(test_config: dict[str, t.Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_ENGINES"] = {"default": "sqlite://"}

    if test_config:
        app.config |= test_config

    db.init_app(app)
    alembic.init_app(app)
    return app


def make_migrations():
    inc = count()
    alembic.rev_id = lambda: str(1_000 + next(inc))

    shutil.rmtree(alembic.config.get_main_option("script_location"))
    alembic.mkdir()

    sa.Table(
        "todo",
        Model.metadata,
        sa.Column("id", sa.Integer, primary_key=True),
    )
    alembic.revision("init")
    alembic.upgrade()

    sa.Table(
        "todo",
        Model.metadata,
        sa.Column("text", sa.String),
        extend_existing=True,
    )
    alembic.revision("add text column")


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        make_migrations()
