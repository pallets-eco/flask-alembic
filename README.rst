Flask-Alembic
=============

This `Flask`_ extension provides a configurable `Alembic`_ migration environment around a `Flask-SQLAlchemy`_ database.

`Full documentation`_

Installation
------------

Install releases from `PyPI`_::

    pip install Flask-Alembic

Install the latest code from `BitBucket`_::

    pip install https://bitbucket.org/davidism/flask-alembic/get/default.tar.gz

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

Commands are included for Click (Flask 0.11, or Flask-CLI)::

    $ flask db revision "making changes"
    $ flask db upgrade

and Flask-Script::

    $ python manage.py db --help

Differences from Alembic core
-----------------------------

* Configuration is taken from ``Flask.config`` instead of ``alembic.ini``.
* The migrations are stored directly in the migrations folder instead of the versions folder.
* The extension provides the migration environment instead of ``env.py``.
* Does not (currently) support offline migrations or multiple databases.
* Adds a system for managing independent migration branches and makes it easier to work with named branches.

Differences from Flask-Migrate
------------------------------

`Flask-Migrate`_ is a simple wrapper around the existing Alembic commands.  It associates the Flask-SQLAlchemy database with Alembic, and wraps the Alembic commands with Flask-Script.  It still requires the standard Alembic file structure, does not integrate with Flask configuration, and does not expose the Alembic internals.

.. _Flask: https://palletsprojects.com/p/flask/
.. _Flask-SQLAlchemy: http://flask-sqlalchemy.pocoo.org/
.. _Alembic: https://alembic.zzzcomputing.com/en/latest/
.. _PyPI: https://pypi.python.org/pypi/Flask-Alembic
.. _BitBucket: https://bitbucket.org/davidism/flask-alembic
.. _Flask-Migrate: https://flask-migrate.readthedocs.io/en/latest/
.. _Full documentation: https://flask-alembic.readthedocs.io/
