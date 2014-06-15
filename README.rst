Flask-Alembic
=============

This Flask extension provides a configurable Alembic migration environment around a Flask-SQLAlchemy database.

Installation
------------

Install releases from PyPI::

    pip install Flask-Alembic

Install latest code from BitBucket::

    pip install https://bitbucket.org/davidism/flask-alembic

Basic Usage
-----------

You've create a Flask application and some models with Flask-SQLAlchemy.  Now start using Flask-Alembic::

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

FAQ
----

How does Flask-Alembic differ from Alembic core?
    Alembic uses alembic.ini for configuration, and env.py for setting up a migration environment.  Flask-Alembic takes advantage of Flask's configuration to remove alembic.ini.  It removes env.py and provides the migration environment directly, which allows access to all the Alembic internals within the Flask application.

How does Flask-Alembic differ from Flask-Migrate?
    Flask-Migrate is a simple wrapper around the existing Alembic commands.  It associates the Flask-SQLAlchemy database with Alembic, and wraps the Alembic commands with Flask-Script.  It still requires the standard Alembic file structure, does not integrate with Flask configuration, and does not expose the Alembic internals.

TODO
----

*   See if `db.session` can be used rather than establishing new connections.
*   Support multiple databases though Flask-SQLAlchemy's binds.
*   Provide commands with Click, the new Flask CLI.
