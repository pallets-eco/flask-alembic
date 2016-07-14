"""
flask_alembic
-------------

.. autoclass:: flask_alembic.Alembic
    :members:
    :member-order: bysource

.. automodule:: flask_alembic.cli
    :members:
"""

from flask_alembic.extension import Alembic
from flask_alembic.cli.click import cli as alembic_click
from flask_alembic.cli.script import manager as alembic_script
