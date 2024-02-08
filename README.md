# Flask-Alembic

Flask-Alembic is a [Flask][] extension that provides a configurable [Alembic][]
migration environment around a [Flask-SQLAlchemy][] database.

[Flask]: https://flask.palletsprojects.com
[Alembic]: https://alembic.sqlalchemy.org
[Flask-SQLAlchemy]: https://flask-sqlalchemy.palletsprojects.com

## Installation

Install from [PyPI][]:

```text
$ pip install Flask-Alembic
```

[PyPI]: https://pypi.org/project/Flask-Alembic

## Basic Usage

You've created a Flask application and some models with Flask-SQLAlchemy. Now
start using Flask-Alembic:

```python
from flask_alembic import Alembic

# Intialize the extension
alembic = Alembic()
alembic.init_app(app)
```

Commands are added to the `flask` CLI:

```text
$ flask db --help
$ flask db revision "making changes"
$ flask db upgrade
```

You can also access Alembic's functionality from Python:

```python
with app.app_context():
    # Auto-generate a migration
    alembic.revision('making changes')

    # Upgrade the database
    alembic.upgrade()

    # Access the internals
    environment_context = alembic.env
```

## Differences from Alembic

- Configuration is taken from `Flask.config` instead of `alembic.ini` and
  `env.py`.
- The migrations are stored directly in the `migrations` folder instead of the
  `versions` folder.
- Provides the migration environment instead of `env.py` and exposes Alembic's
  internal API objects.
- Differentiates between CLI commands and Python functions. The functions return
  revision objects and don't print to stdout.
- Allows operating Alembic at any API level while the app is running, through
  the exposed objects and functions.
- Does not (currently) support offline migrations. I don't plan to add this but
  am open to patches.
- Does not (currently) support multiple databases. I plan on adding support for
  Flask-SQLAlchemy binds and external bases eventually, or am open to patches.
- Adds a system for managing independent migration branches and makes it easier
  to work with named branches.
