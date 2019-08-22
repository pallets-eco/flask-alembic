"""
flask_alembic
-------------

.. autoclass:: flask_alembic.Alembic
    :members:
    :member-order: bysource

.. automodule:: flask_alembic.cli
    :members:
"""
from .extension import Alembic

try:
    from .cli.click import cli as alembic_click
except ImportError:
    alembic_click = None

try:
    from .cli.script import manager as alembic_script
except ImportError:
    alembic_script = None
