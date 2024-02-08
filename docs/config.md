# Configuration

Configuration for Alembic and its migrations uses the following Flask config
keys.

```{module} flask_alembic.config
```

```{data} ALEMBIC
A dictionary containing general configuration, mostly used by
{class}`~alembic.config.Config` and {class}`~alembic.script.ScriptDirectory`.
See Alembic's docs on [config][alembic-config].
```

```{data} ALEMBIC_CONTEXT
A dictionary containing options passed to {class}`.MigrationContext` by
{attr}`.EnvironmentContext.configure`. See Alembic's docs on
[runtime][alembic-runtime].
```

`ALEMBIC["script_location"]` is the location of the `migrations` directory. If
it is not an absolute path, it will be relative to the application root. It
defaults to `migrations` relative to the application root.

`ALEMBIC_CONTEXt["compare_type"]` defaults to `True` in Alembic.
`ALEMBIC_CONTEXT["compare_server_default"]` defaults to `True`, it would
otherwise default to `False` in Alembic.

[alembic-config]: https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file
[alembic-runtime]: https://alembic.sqlalchemy.org/en/latest/api/runtime.html#runtime-objects
