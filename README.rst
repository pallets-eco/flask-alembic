Flask-Alembic
=============

This `Flask`_ extension provides a configurable `Alembic`_ migration environment around a `Flask-SQLAlchemy`_ database.

Installation
------------

Install releases from `PyPI`_::

    pip install Flask-Alembic

Install latest code from `BitBucket`_::

    pip install https://bitbucket.org/davidism/flask-alembic

Basic Usage
-----------

You've created a Flask application and some models with Flask-SQLAlchemy.  Now start using Flask-Alembic::

    from flask_alembic import Alembic

    # Intialize the extension
    alembic = Alembic()
    alembic.init_app(app)

    # Auto-generate a migration
    alembic.revision('making changes')

    # Upgrade the database
    alembic.upgrade()

    # Access the internals
    environment_context = alembic.env

Differences from Alembic core
-----------------------------

*   Configuration is taken from Flask instead of alembic.ini.
*   The migrations are stored directly in the migrations folder instead of the versions folder.
*   The extension provides the migration environment instead of env.py.
*   Does not (currently) support offline migrations.

Differences from Flask-Migrate
------------------------------

`Flask-Migrate`_ is a simple wrapper around the existing Alembic commands.  It associates the Flask-SQLAlchemy database with Alembic, and wraps the Alembic commands with Flask-Script.  It still requires the standard Alembic file structure, does not integrate with Flask configuration, and does not expose the Alembic internals.

TODO
----

*   See if ``db.session`` can be used rather than establishing new connections.
*   Support multiple databases though Flask-SQLAlchemy's binds.
*   Support offline migrations.

.. _Flask: http://flask.pocoo.org/
.. _Flask-SQLAlchemy: https://pythonhosted.org/Flask-SQLAlchemy/
.. _Alembic: https://alembic.readthedocs.org/en/latest/
.. _PyPI: https://pypi.python.org/pypi/Flask-Alembic
.. _BitBucket: https://bitbucket.org/davidism/flask-alembic
.. _Flask-Migrate: https://flask-migrate.readthedocs.org/en/latest/
