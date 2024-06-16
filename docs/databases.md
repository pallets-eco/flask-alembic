from sqlalchemy.orm import DeclarativeBase

# Database Scenarios

You can use Flask-Alembic with Flask-SQLAlchemy, Flask-SQLAlchemy-Lite, or plain
SQLAlchemy. Alembic's single and multiple database templates are supported.

## Flask-SQLAlchemy

The default engine (`db.engine`) and metadata (`db.metadata`) will automatically
be used. If multiple binds are configured, they (`db.engines`) will be used if
multiple metadatas are configured in Flask-Alembic. Additional metadata
(`db.metadatas`) will not be used automatically however, as it's not possible to
know which are external and should not be migrated.

## Flask-SQLAlchemy-Lite

The default engine (`db.engine`) will automatically be used. Since
Flask-SQLAlchemy-Lite does not manage the models, tables, or metadata itself,
the metadata you define must be passed to `Alembic`.

```python
from flask_alembic import Alembic
from sqlalchemy.orm import DeclarativeBase

class Model(DeclarativeBase):
    pass

alembic = Alembic(metadatas=Model.metadata)
```

## Plain SQLAlchemy

If you are not using either extension, but defining SQLAlchemy engines and
models/metadata manually, you can pass them to `Alembic`. You can also do this
when using either extension to control exactly what is used for migrations.

```python
from flask_alembic import Alembic
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

engine = create_engine("sqlite:///default.sqlite")

class Model(DeclarativeBase):
    pass

alembic = Alembic(metadatas=Model.metadata, engines=engine)
```

## Multiple Databases

If you need to manage migrations across multiple databases, you can specify
multiple metadata and engines to run migrations on. Flask-Alembic will use
Alembic's suggested `multidb` template for generating and running migrations.

The `metadatas` argument can be a dict mapping string names to a single
metadata or list of metadatas. When using Flask-SQLAlchemy(-Lite), `db.engines`
is automatically used, so the keys there should match up with the keys in
`metadatas`. Otherwise, the `engines` argument can be a dict mapping the same
string names to engines.

```python
from flask import Flask
from flask_alembic import Alembic
from flask_sqlalchemy_lite import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class DefaultBase(DeclarativeBase):
    pass

class AuthBase(DeclarativeBase):
    pass

db = SQLAlchemy()
alembic = Alembic(
    metadatas={
        "default": DefaultBase.metadata,
        "auth": AuthBase.metadata,
    },
)
app = Flask(__name__)
app.config["SQLALCHEMY_ENGINES"] = {
    "default": "sqlite:///default.sqlite",
    "auth": "postgresql:///app-auth",
}
db.init_app(app)
alembic.init_app(app)
```

When `alembic.init_app` is called, it creates the migrations directory and
script template if it does not exist. It will choose the `generic` (single
database) template if only one name is configured, or the `multidb` template if
more are configured. Due to the way Alembic works, the two templates are not
compatible. If you switch to single or multiple databases later after generating
migrations, you'll need to replace the `script.py.mako` file and modify the
existing migrations. A good strategy in that scenario may be to delete existing
migrations and start from scratch.

## Multiple Metadatas

It's possible to split your models/tables for a database across multiple
metadatas. In that case, you can pass a list of metadatas instead of a single
metadata. If you're only managing a single database, you can pass the list
directly to `metadatas`, otherwise any value in the dict can be a list.


```python
from flask_alembic import Alembic
from sqlalchemy.orm import DeclarativeBase

class DefaultBase(DeclarativeBase):
    pass

class AuthBase(DeclarativeBase):
    pass

alembic = Alembic(metadatas=[DefaultBase.metadata, AuthBase.metadata])
```
