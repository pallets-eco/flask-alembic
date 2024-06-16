# Using Flask-Alembic

## Initialize the Application

```{currentmodule} flask_alembic
```

First, set up your Flask application (or application factory) and the
Flask-SQLAlchemy(-Lite) extension and models.

This extension follows the common pattern of Flask extension setup. Either
immediately pass an app to {class}`.Alembic`, or call {meth}`~.Alembic.init_app`
later.

```python
from flask_alembic import Alembic

alembic = Alembic()
alembic.init_app(app)  # call in the app factory if you're using that pattern
```

When using Flask-SQLAlchemy, `db.engines` and `db.metadata` are used
automatically.

When using Flask-SQLAlchemy-Lite, `db.engines` is used automatically, but you
must pass the metadata you defined.

```python
from flask_alembic import Alembic
from sqlalchemy.orm import DeclarativeBase

class Model(DeclarativeBase):
    pass

alembic = Alembic(metadatas=Model.metadata)
```

You can use Flask-Alembic with Flask-SQLAlchemy, Flask-SQLAlchemy-Lite, or plain
SQLAlchemy, and there is support for migrating multiple databases. See
{doc}`databases` for details.

When an app is registered, the migrations directory is created if it does not
exist.

## Using Alembic from the Command Line

Flask-Alembic automatically adds a `db` group of commands to the `flask` CLI.
From there you can generate revisions, apply upgrades, etc. The basic commands
are `revision` to create a new revision, and `upgrade` to apply available
revisions.

```text
$ flask db --help
$ flask db revision "made changes"
$ flask db upgrade
```

## Using Alembic from Python

The `alembic` instance provides an interface between the current app and
Alembic. It exposes similar commands to the command line available from Alembic,
but Flask-Alembic's methods return data rather than produce output. You can use
this interface to do what the command line commands do, from inside your app.

```python
# generate a new revision
# same as `flask db revision "made changes"`
alembic.revision("made changes")

# run all available upgrades
# same as `flask db upgrade`
alembic.upgrade()
```

You can also get at the Alembic internals that enable these commands. See the
[Alembic API docs][alembic-api] for more information.

[alembic-api]: https://alembic.sqlalchemy.org/en/latest/api/index.html

```python
# locate a revision by name
alembic.script.get_revision("head")

# could compare this to the "head" revision above to see if upgrades are needed
alembic.context.get_current_revision()

# probably don't want to do this outside a revision, but it'll work
alembic.op.drop_column("my_table", "my_column")

# see that the column you just dropped will be added back next revision
alembic.compare_metadata()
```

The functions require an app context. If you're calling them outside a view, set
up a context manually.

```python
with app.app_context():
    alembic.upgrade()
```
