from __future__ import annotations

import pytest
import sqlalchemy as sa
from flask.testing import FlaskCliRunner

from flask_alembic import Alembic


@pytest.mark.usefixtures("app_ctx")
def test_needs_no_changes(alembic: Alembic) -> None:
    alembic.upgrade()
    assert not alembic.needs_revision()


@pytest.mark.usefixtures("app_ctx")
def test_needs_changes(alembic: Alembic, metadata: sa.MetaData) -> None:
    alembic.upgrade()
    sa.Table(
        "new_table",
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
    )
    assert alembic.needs_revision()


@pytest.mark.usefixtures("app_ctx")
def test_check_no_changes(alembic: Alembic, runner: FlaskCliRunner) -> None:
    alembic.upgrade()
    result = runner.invoke(args=["db", "check"])
    assert result.exit_code == 0
    assert "No changes detected" in result.output


@pytest.mark.usefixtures("app_ctx")
def test_check_changes(
    alembic: Alembic, runner: FlaskCliRunner, metadata: sa.MetaData
) -> None:
    alembic.upgrade()
    sa.Table(
        "new_table",
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
    )
    result = runner.invoke(args=["db", "check"])
    assert result.exit_code == 1
    assert "Changes detected" in result.output
