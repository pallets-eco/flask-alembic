Flask-Alembic
=============

This `Flask`_ extension provides a configurable `Alembic`_ migration
environment around a `Flask-SQLAlchemy`_ database.

.. _Flask: https://palletsprojects.com/p/flask/
.. _Flask-SQLAlchemy: http://flask-sqlalchemy.pocoo.org/
.. _Alembic: https://alembic.zzzcomputing.com/en/latest/


Installation
------------

Install and update using `pip`_:

.. code-block:: text

    $ pip install Flask-Alembic

.. _pip: https://pip.pypa.io/en/stable/quickstart/


Basic Usage
-----------

You've created a Flask application and some models with
Flask-SQLAlchemy. Now start using Flask-Alembic:

.. code-block:: python

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

Commands are added to the ``flask`` CLI:

.. code-block:: text

    $ flask db --help
    $ flask db revision "making changes"
    $ flask db upgrade


Links
-----

-   Documentation: https://flask-alembic.readthedocs.io/
-   Releases: https://pypi.org/project/Flask-Alembic/
-   Code: https://github.com/davidism/flask-alembic
