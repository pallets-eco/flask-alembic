Flask-Alembic
=============

Flask-Alembic is a `Flask`_ extension that provides a configurable `Alembic`_ migration
environment around a `Flask-SQLAlchemy`_ database.

.. _Flask: https://palletsprojects.com/p/flask/
.. _Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/
.. _Alembic: https://alembic.sqlalchemy.org/en/latest/


Installation
------------

Install from `PyPI`_:

.. code-block:: text

    $ pip install Flask-Alembic

.. _PyPI: https://pypi.org/project/Flask-Alembic


Differences from Alembic
------------------------

-   Configuration is taken from ``Flask.config`` instead of
    ``alembic.ini`` and ``env.py``.
-   The migrations are stored directly in the migrations folder instead
    of the versions folder.
-   Provides the migration environment instead of ``env.py`` and exposes
    Alembic's internal API objects.
-   Differentiates between CLI commands and Python functions. The
    functions return revision objects and don't print to stdout.
-   Allows operating Alembic at any API level while the app is running,
    through the exposed objects and functions.
-   Does not (currently) support offline migrations. I don't plan to add
    this but am open to patches.
-   Does not (currently) support multiple databases. I plan on adding
    support for Flask-SQLAlchemy binds and external bases eventually, or
    am open to patches.
-   Adds a system for managing independent migration branches and makes
    it easier to work with named branches.


User Guide
----------

.. toctree::
    :maxdepth: 2

    use
    config
    branches


API Reference
-------------

.. toctree::
    :maxdepth: 2

    api


Additional Information
----------------------

.. toctree::
    :maxdepth: 1

    license

.. toctree::
    :maxdepth: 2

    changes
