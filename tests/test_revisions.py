import pytest

from flask_alembic import Alembic


@pytest.mark.usefixtures("app_ctx")
def test_int_id(alembic: Alembic) -> None:
    """If the id is an int, first check if it is a revision before treating it
    as a relative count."""
    alembic.upgrade("1000")
    alembic.upgrade("1")
    alembic.downgrade("1000")
    alembic.downgrade("-1")
