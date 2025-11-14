from __future__ import annotations

import pytest
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

from flask_alembic import Alembic


class Model(DeclarativeBase):
    pass


class Other(DeclarativeBase):
    pass


@pytest.mark.usefixtures("app_ctx")
def test_metadata_required(app: Flask) -> None:
    """Passing a metadata is required with plain SQLAlchemy."""
    alembic = Alembic(app)

    with pytest.raises(RuntimeError, match="pass 'metadatas' when"):
        assert alembic.migration_context


@pytest.mark.usefixtures("app_ctx")
def test_engine_required(app: Flask) -> None:
    """Passing an engine is required with plain SQLAlchemy."""
    alembic = Alembic(app, metadatas=Model.metadata)

    with pytest.raises(RuntimeError, match="engines configured"):
        assert alembic.migration_context


@pytest.mark.usefixtures("app_ctx")
def test_valid_config(app: Flask) -> None:
    """A valid config that creates two migration contexts."""
    engine = create_engine("sqlite://")
    other_engine = create_engine("sqlite://")
    alembic = Alembic(
        app,
        metadatas={"default": Model.metadata, "other": Other.metadata},
        engines={"default": engine, "other": other_engine},
    )
    assert len(alembic.migration_contexts) == 2


@pytest.mark.usefixtures("app_ctx")
def test_missing_engine(app: Flask) -> None:
    """A valid config that creates two migration contexts."""
    engine = create_engine("sqlite://")
    alembic = Alembic(
        app,
        metadatas={"default": Model.metadata, "other": Other.metadata},
        engines=engine,
    )

    with pytest.raises(RuntimeError, match="Missing engine config"):
        assert alembic.migration_context
