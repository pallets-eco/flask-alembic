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

    with app.app_context():
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

.. _Flask: https://palletsprojects.com/p/flask/
.. _Flask-SQLAlchemy: http://flask-sqlalchemy.pocoo.org/
.. _Alembic: https://alembic.zzzcomputing.com/en/latest/
.. _PyPI: https://pypi.python.org/pypi/Flask-Alembic
.. _BitBucket: https://bitbucket.org/davidism/flask-alembic
.. _Full documentation: https://flask-alembic.readthedocs.io/
