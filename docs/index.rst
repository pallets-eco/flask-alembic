Flask-Alembic
=============

Flask-Alembic is a `Flask`_ extension that provides a configurable
`Alembic`_ migration environment around a `Flask-SQLAlchemy`_ database.


Installation
------------

Install with pip:

.. code-block:: text

    $ pip install Flask-Alembic

.. _Flask: https://palletsprojects.com/p/flask/
.. _Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/
.. _Alembic: https://alembic.sqlalchemy.org/en/latest/


Configuration
-------------

Configuration for Alembic and its migrations is pulled from the
following Flask config keys.

-   ``ALEMBIC`` is a dictionary containing general configuration, mostly
    used by :class:`~alembic.config.Config` and
    :class:`~alembic.script.ScriptDirectory`. See Alembic's docs on
    `config <alembic-config_>`_.
-   ``ALEMBIC_CONTEXT`` is a dictionary containing options passed to
    :class:`~alembic.runtime.environment.EnvironmentContext` and
    :class:`~alembic.runtime.migration.MigrationContext`. See Alembic's
    docs on `runtime <alembic-runtime_>`_.

The only required configuration is ``ALEMBIC["script_location"]``, which
is the location of the migrations directory. If it is not an absolute
path, it will be relative to the instance folder. This defaults to
``migrations`` relative to the application root.

.. _alembic-config: https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file
.. _alembic-runtime: https://alembic.sqlalchemy.org/en/latest/api/runtime.html#runtime-objects


Basic Usage
-----------

First, set up your Flask app (or app factory) and the Flask-SQLAlchemy
extension and models.

This extension follows the common pattern of Flask extension setup.
Either immediately pass an app to :class:`~flask_alembic.Alembic`, or
call :meth:`~flask_alembic.Alembic.init_app` later.

.. code-block:: python

    from flask_alembic import Alembic

    alembic = Alembic()
    alembic.init_app(app)  # call in the app factory if you're using that pattern

When an app is registered, :meth:`~flask_alembic.Alembic.mkdir` is
called to set up the migrations directory if it does not already exist.
To prevent this, call ``init_app`` with ``run_mkdir=False``.

The ``alembic`` instance provides an interface between the current app
and Alembic. It exposes similar commands to the command line available
from Alembic, but Flask-Alembic's methods return data rather than
produce output. You can use this interface to do what the command line
commands do, from inside your app.

.. code-block:: python

    # generate a new revision
    # same as flask db revision 'made changes'
    alembic.revision('made changes')

    # run all available upgrades
    # same as ./manage.py db upgrade
    alembic.upgrade()

You can also get at the Alembic internals that enable these commands.
See the `Alembic API docs <alembic-api_>`_ for more information.

.. code-block:: python

    # locate a revision by name
    alembic.script.get_revision("head")
    # could compare this to the 'head' revision above to see if upgrades are needed
    alembic.context.get_current_revision()
    # probably don't want to do this outside a revision, but it'll work
    alembic.op.drop_column("my_table", "my_column")
    # see that the column you just dropped will be added back next revision
    alembic.compare_metadata()

The functions require an app context. If you're calling them outside a
view, set up a context manually.

.. code-block:: python

    with app.app_context():
        alembic.upgrade()

.. _alembic-api: https://alembic.sqlalchemy.org/en/latest/api/index.html


Independent Named Branches
--------------------------

Alembic supports `named branches`_, but its syntax is hard to remember
and verbose. Flask-Alembic makes it easier by providing a central
configuration for branch names and revision directories and simplifying
the syntax to the ``revision`` command.

Alembic allows configuration of multiple version locations.
``version_locations`` is a list of directories to search for migration
scripts. Flask-Alembic extends this to allow tuples as well as strings
in the list. If a tuple is added, it specifies a ``(branch, directory)``
pair. The ``script_location`` is automatically given the label
``default`` and added to the ``version_locations``.

.. code-block:: python

    ALEMBIC = {
        "version_locations": [
            # not a branch, just another search location
            "other_migrations",
            # posts branch migrations will be placed here
            ("posts", "/path/to/posts_extension/migrations"),
            # relative paths are relative to the application root
            ("users", "users/migrations"),
        ]
    }

The ``revision`` command takes a ``--branch`` option (defaults to
``default``). This takes the place of specifying ``--parent``,
``--label``, and ``--path``. This will automatically start the branch
from the base revision, label the revision correctly, and place the
revisions in the correct location.

.. code-block:: text

    $ flask db revision --branch users 'create user model'
    # equivalent to (if branch is new)
    # alembic revision --autogenerate --head base --branch-label users --version-path users/migrations -m 'create user model'
    # or (if branch exists)
    # alembic revision --autogenerate --head users@head -m 'create user model'

.. _named branches: https://alembic.sqlalchemy.org/en/latest/branches.html#working-with-multiple-bases


Command Line
------------

Currently, `Click`_ and `Flask-Script`_ are supported. The commands are
the same for either one. Flask-Script was deprecated in 2017, the
preferred interface is Click.

If you are using Flask >= 0.11, the preferred interface is Click. If you
are using Flask 0.10, you can use backported integration via
`Flask-CLI`_. Flask-Alembic will automatically add the command to the
CLI if it detects that Click is available.

.. code-block:: text

    $ flask db --help

If you have set up a :class:`flask_script.Manager` for your project
using Flask-Script, you can add Alembic commands like this:

.. code-block:: python

    from flask_alembic import alembic_script
    app_manager.add_command("db", alembic_manager)

.. code-block:: text

    $ python manage.py db

.. _Click: https://palletsprojects.com/p/click/
.. _Flask-Script: https://flask-script.readthedocs.io/en/latest/
.. _Flask-CLI: https://flask-cli.readthedocs.io/en/latest/


Differences from Alembic
------------------------

Flask-Alembic is opinionated and was designed to enable specific
workflows. If you're looking for a more direct wrapper around Alembic,
you may be interested in `Flask-Migrate`_ instead.

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

.. _Flask-Migrate: https://flask-migrate.readthedocs.io/en/latest/


API Reference
-------------

.. automodule:: flask_alembic
