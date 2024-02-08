from pathlib import Path

from click.testing import Result
from flask import Flask

from flask_alembic import Alembic


def test_default_config(app: Flask, alembic: Alembic) -> None:
    assert app.extensions["alembic"] == alembic
    assert app.config["ALEMBIC"] == {
        "script_location": "migrations",
        "version_locations": [],
    }
    assert app.config["ALEMBIC_CONTEXT"] == {
        "compare_server_default": True,
    }


def test_run_mkdir(app: Flask, alembic: Alembic) -> None:
    assert (Path(app.root_path) / "migrations").is_dir()


def test_no_run_mkdir(app: Flask) -> None:
    Alembic(app, run_mkdir=False)
    assert not (Path(app.root_path) / "migrations").exists()


def test_cli(app: Flask, alembic: Alembic) -> None:
    runner = app.test_cli_runner()
    result = runner.invoke(args=["db", "--help"])
    assert result.exit_code == 0


def test_no_cli(app: Flask) -> None:
    Alembic(app, command_name="")
    runner = app.test_cli_runner()
    result: Result = runner.invoke(args=["db", "--help"])
    assert result.exit_code == 2
