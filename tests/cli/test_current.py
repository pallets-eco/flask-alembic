from __future__ import annotations

import pytest
from flask.testing import FlaskCliRunner

from flask_alembic import Alembic


@pytest.mark.usefixtures("app_ctx")
def test_needs_upgrade_at_head(alembic: Alembic) -> None:
    alembic.upgrade()
    assert not alembic.needs_upgrade()


@pytest.mark.usefixtures("app_ctx")
def test_needs_upgrade_not_at_head(alembic: Alembic) -> None:
    alembic.upgrade(1)
    assert alembic.needs_upgrade()


@pytest.mark.usefixtures("app_ctx")
def test_check_heads_at_head(alembic: Alembic, runner: FlaskCliRunner) -> None:
    alembic.upgrade()
    result = runner.invoke(args=["db", "current", "--check-heads"])
    assert result.exit_code == 0


@pytest.mark.usefixtures("app_ctx")
def test_check_heads_not_at_head(alembic: Alembic, runner: FlaskCliRunner) -> None:
    alembic.upgrade(1)
    result = runner.invoke(args=["db", "current", "--check-heads"])
    assert result.exit_code == 1
    assert "Database is not on all head revisions" in result.output
