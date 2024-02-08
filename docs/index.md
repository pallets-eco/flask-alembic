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

```{toctree}
:hidden:

use
config
branches
api
license
changes
```
