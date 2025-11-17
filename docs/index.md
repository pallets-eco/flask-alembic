# Flask-Alembic

Flask-Alembic is a [Flask][] extension that provides a configurable [Alembic][]
database migration environment. Supports [Flask-SQLAlchemy],
[Flask-SQLAlchemy-Lite], or plain [SQLAlchemy]. Supports Alembic's single and
multiple database templates.

[Flask]: https://flask.palletsprojects.com
[Alembic]: https://alembic.sqlalchemy.org
[SQLAlchemy]: https://www.sqlalchemy.org
[Flask-SQLAlchemy]: https://flask-sqlalchemy.palletsprojects.com
[Flask-SQLAlchemy-Lite]: https://flask-sqlalchemy-lite.readthedocs.io

## Installation

Install from [PyPI][] using an installer such as pip:

```
$ pip install Flask-Alembic
```

[PyPI]: https://pypi.org/project/Flask-Alembic

## Source

The project is hosted on GitHub: <https://github.com/pallets-eco/flask-alembic>.

## Differences from Alembic

- Configuration is taken from `Flask.config` instead of `alembic.ini` and
  `env.py`.
- Engines and model/table metadata are taken from Flask-SQLAlchemy(-Lite) if
  available, or can be configured manually.
- The migrations are stored directly in the `migrations` folder instead of the
  `versions` folder.
- Provides the migration environment instead of `env.py` and exposes Alembic's
  internal API objects.
- Differentiates between CLI commands and Python functions. The functions return
  revision objects and don't print to stdout.
- Allows operating Alembic at any API level while the app is running, through
  the exposed objects and functions.
- Adds a system for managing independent migration branches and makes it easier
  to work with named branches.
- Does not (currently) support offline migrations. I don't plan to work on this
  but am open to patches.
- Does not (currently) support async engines. I don't plan to work on this but
  am open to patches.

```{toctree}
:hidden:

use
config
databases
branches
api
license
changes
```
