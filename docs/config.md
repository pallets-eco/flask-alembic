# Configuration

Configuration for Alembic and its migrations uses the following Flask config
keys.

```{currentmodule} flask_alembic
```

```{data} ALEMBIC
A dictionary containing general configuration, mostly used by
{class}`~alembic.config.Config` and {class}`~alembic.script.ScriptDirectory`.
See Alembic's docs on [config][alembic-config].

If a value is a dict, the key will be equivalent to a section name in
``alembic.ini``, and the value will be the items in the section. This allows
using Alembic's [post_write_hooks], for example.

```{versionchanged} 3.1
Treat dict values as sections.
```

```{data} ALEMBIC_CONTEXT
A dictionary containing options passed to {class}`.MigrationContext` by
{attr}`.EnvironmentContext.configure`. See Alembic's docs on
[runtime][alembic-runtime].
```

`ALEMBIC["script_location"]` is the location of the `migrations` directory. If
it is not an absolute path, it will be relative to the application root. It
defaults to `migrations` relative to the application root.

`ALEMBIC_CONTEXT["compare_type"]` defaults to `True` in Alembic.
`ALEMBIC_CONTEXT["compare_server_default"]` defaults to `True`, it would
otherwise default to `False` in Alembic.

[alembic-config]: https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file
[alembic-runtime]: https://alembic.sqlalchemy.org/en/latest/api/runtime.html#runtime-objects
[post_write_hooks]: https://alembic.sqlalchemy.org/en/latest/autogenerate.html#applying-post-processing-and-python-code-formatters-to-generated-revisions

## Post Processing Revisions

It's possible to tell Alembic to run one or more commands on a generated
migration file. See [Alembic's docs][post_write_hooks] for full details.
Here are some useful examples.

### black

Run the [black] formatter.

[black]: https://black.readthedocs.io

```python
ALEMBIC = {
    "post_write_hooks": {
        "hooks": "black",
        "pre-commit.type": "console_scripts",
        "pre-commit.entrypoint": "black",
    }
}
```

### ruff

Run the [ruff] formatter.

[ruff]: https://docs.astral.sh/ruff/formatter/

```python
ALEMBIC = {
    "post_write_hooks": {
        "hooks": "ruff",
        "pre-commit.type": "console_scripts",
        "pre-commit.entrypoint": "ruff",
        "pre-commit.options": "format REVISION_SCRIPT_FILENAME",
    }
}
```

### pre-commit

Run all configured [pre-commit] hooks.

[pre-commit]: https://pre-commit.com

```python
ALEMBIC = {
    "post_write_hooks": {
        "hooks": "pre-commit",
        "pre-commit.type": "console_scripts",
        "pre-commit.entrypoint": "pre-commit",
        "pre-commit.options": "run --files REVISION_SCRIPT_FILENAME",
    }
}
```

### git add

Add the file to git so that you don't forget when committing. This can be run
after other hooks so that all the changes are staged.

```python
ALEMBIC = {
    "post_write_hooks": {
        "hooks": "pre-commit, git",
        "pre-commit.type": "console_scripts",
        "pre-commit.entrypoint": "pre-commit",
        "pre-commit.options": "run --files REVISION_SCRIPT_FILENAME",
        "git.type": "exec",
        "git.executable": "git",
        "git.options": "add REVISION_SCRIPT_FILENAME",
    }
}
```
