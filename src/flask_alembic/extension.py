from __future__ import annotations

import dataclasses
import logging
import os
import shutil
import sys
import typing as t
from contextlib import ExitStack
from datetime import datetime
from datetime import timezone
from weakref import WeakKeyDictionary

import sqlalchemy as sa
from alembic import autogenerate
from alembic import util
from alembic.config import Config
from alembic.operations import MigrationScript
from alembic.operations import Operations
from alembic.runtime.environment import EnvironmentContext
from alembic.runtime.migration import MigrationContext
from alembic.runtime.migration import MigrationStep
from alembic.script import Script
from alembic.script import ScriptDirectory
from alembic.script.revision import ResolutionError
from flask import current_app
from flask import Flask

if t.TYPE_CHECKING:
    import typing_extensions as te

t_rev: te.TypeAlias = (
    "str | Script | list[str] | list[Script] | tuple[str, ...] | tuple[Script, ...]"
)


class Alembic:
    """Provide an Alembic environment and migration API.

    If instantiated without an app instance, :meth:`init_app` is used to
    register an app at a later time.

    Configures basic logging to ``stderr`` for the ``sqlalchemy`` and
    ``alembic`` loggers if they do not already have handlers.

    :param app: Call ``init_app`` on this app.
    :param run_mkdir: Run :meth:`mkdir` during ``init_app``.
    :param command_name: Register a Click command with this name during
        ``init_app``, unless it is the empty string.
    :param metadatas: One or more :class:`~sqlalchemy.MetaData` to inspect when
        generating migrations. A single metadata or list will be assigned to
        the ``"default"`` key. Or a map can be given that specifies one or more
        metadata for each key. When using Flask-SQLAlchemy, ``db.metadata`` is
        used if this is not given.
    :param engines: One or more engines to perform migrations on. Must match the
        keys in ``metadatas``. A single engine will be assigned to the
        ``"default"`` key. Or a map can be given that specifies the engine for
        each key. When using Flask-SQLAlchemy(-Lite), ``db.engines`` is used
        if this is not given.

    .. versionchanged:: 3.1
        Added the ``metadatas`` and ``enginess`` arguments. Support
        Flask-SQLAlchemy-Lite and plain SQLAlchemy in addition to
        Flask-SQLAlchemy. Support multiple databases and multiple metadata per
        database.

    .. versionchanged:: 3.1
        ``run_mkdir`` and ``command_name`` are keyword-only arguments.
    """

    def __init__(
        self,
        app: Flask | None = None,
        *,
        run_mkdir: bool = True,
        command_name: str = "db",
        metadatas: sa.MetaData
        | list[sa.MetaData]
        | dict[str, sa.MetaData | list[sa.MetaData]]
        | None = None,
        engines: sa.Engine | dict[str, sa.Engine] | None = None,
    ):
        self._cache: WeakKeyDictionary[Flask, _Cache] = WeakKeyDictionary()
        self.run_mkdir: bool = run_mkdir
        self.command_name: str = command_name
        self.metadatas: dict[str, sa.MetaData | list[sa.MetaData]]
        self.engines: dict[str, sa.Engine]

        if metadatas is None:
            self.metadatas = {}
        elif isinstance(metadatas, (sa.MetaData, list)):
            self.metadatas = {"default": metadatas}
        else:
            self.metadatas = metadatas

        if engines is None:
            self.engines = {}
        elif isinstance(engines, sa.Engine):
            self.engines = {"default": engines}
        else:
            self.engines = engines

        # add logging handler if not configured
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.formatter = logging.Formatter(
            fmt="%(levelname)-5.5s [%(name)s] %(message)s", datefmt="%H:%M:%S"
        )

        sqlalchemy_logger = logging.getLogger("sqlalchemy")
        alembic_logger = logging.getLogger("alembic")

        if not sqlalchemy_logger.hasHandlers():
            sqlalchemy_logger.setLevel(logging.WARNING)
            sqlalchemy_logger.addHandler(console_handler)

        # alembic adds a null handler, remove it
        if len(alembic_logger.handlers) == 1 and isinstance(
            alembic_logger.handlers[0], logging.NullHandler
        ):
            alembic_logger.removeHandler(alembic_logger.handlers[0])

        if not alembic_logger.hasHandlers():
            alembic_logger.setLevel(logging.INFO)
            alembic_logger.addHandler(console_handler)

        if app is not None:
            self.init_app(app)

    def init_app(
        self,
        app: Flask,
        *,
        run_mkdir: None = None,
        command_name: None = None,
    ) -> None:
        """Register this extension on an app. Will automatically set up
        migration directory by default.

        Keyword arguments on this method override those set during
        :meth:`__init__` if not ``None``.

        :param app: App to register.

        .. versionchanged:: 3.1
            ``run_mkdir`` and ``command_name`` are deprecated and will be
            removed in Flask-Alembic 3.2. Use them in the constructor instead.
        """
        app.extensions["alembic"] = self

        config = app.config.setdefault("ALEMBIC", {})
        config.setdefault("script_location", "migrations")
        config.setdefault("version_locations", [])
        ctx = app.config.setdefault("ALEMBIC_CONTEXT", {})
        ctx.setdefault("compare_server_default", True)

        self._cache[app] = cache = _Cache()
        app.teardown_appcontext(cache.clear)

        if run_mkdir is not None:
            import warnings

            warnings.warn(
                "The 'run_mkdir' argument is deprecated and will be removed in"
                " Flask-Alembic 3.2. Pass it to the constructor instead.",
                DeprecationWarning,
                stacklevel=2,
            )

        if run_mkdir or (run_mkdir is None and self.run_mkdir):
            with app.app_context():
                self.mkdir()

        if command_name is not None:
            import warnings

            warnings.warn(
                "The 'command_name' argument is deprecated and will be removed"
                " in Flask-Alembic 3.2. Pass it to the constructor instead.",
                DeprecationWarning,
                stacklevel=2,
            )

        if command_name or (command_name is None and self.command_name):
            from .cli import cli

            app.cli.add_command(cli, command_name or self.command_name)

    def _get_cache(self) -> _Cache:
        """Get the cache of Alembic objects for the current app."""
        app = current_app._get_current_object()  # type: ignore[attr-defined]
        return self._cache[app]

    def rev_id(self) -> str:
        """Generate a unique id for a revision.

        By default, this uses the current UTC timestamp. Override this
        method, or assign a static method, to change this.

        .. versionchanged:: 3.0
            Uses the current UTC timestamp instead of a UUID.
        """
        return str(int(datetime.now(timezone.utc).timestamp()))

    @property
    def config(self) -> Config:
        """Get the Alembic :class:`~alembic.config.Config` for the
        current app.
        """
        cache = self._get_cache()

        if cache.config is not None:
            return cache.config

        cache.config = c = Config()
        script_location = current_app.config["ALEMBIC"]["script_location"]

        if not os.path.isabs(script_location) and ":" not in script_location:
            script_location = os.path.join(current_app.root_path, script_location)

        version_locations = [script_location]

        for item in current_app.config["ALEMBIC"]["version_locations"]:
            version_location = item if isinstance(item, str) else item[1]

            if not os.path.isabs(version_location) and ":" not in version_location:
                version_location = os.path.join(current_app.root_path, version_location)

            version_locations.append(version_location)

        c.set_main_option("script_location", script_location)
        c.set_main_option("version_locations", ",".join(version_locations))

        for key, value in current_app.config["ALEMBIC"].items():
            if key in ("script_location", "version_locations"):
                continue

            if isinstance(value, dict):
                for inner_key, inner_value in value.items():
                    c.set_section_option(key, inner_key, inner_value)
            else:
                c.set_main_option(key, value)

        if len(self.metadatas) > 1:
            # Add the names used by the multidb template.
            c.set_main_option("databases", ", ".join(self.metadatas))

        return cache.config

    @property
    def script_directory(self) -> ScriptDirectory:
        """Get the Alembic
        :class:`~alembic.script.ScriptDirectory` for the current app.
        """
        cache = self._get_cache()

        if cache.script is None:
            cache.script = ScriptDirectory.from_config(self.config)

        return cache.script

    @property
    def environment_context(self) -> EnvironmentContext:
        """Get the Alembic
        :class:`~alembic.runtime.environment.EnvironmentContext` for the
        current app.
        """
        cache = self._get_cache()

        if cache.env is None:
            cache.env = EnvironmentContext(self.config, self.script_directory)

        return cache.env

    def _prepare_targets(
        self,
    ) -> tuple[dict[str, sa.Engine], dict[str, sa.MetaData | list[sa.MetaData]]]:
        cache = self._get_cache()

        if cache.engines is not None and cache.metadatas is not None:
            return cache.engines, cache.metadatas

        sa_ext = current_app.extensions.get("sqlalchemy")
        metadatas = self.metadatas
        engines = self.engines

        if not metadatas and sa_ext is not None and hasattr(sa_ext, "metadata"):
            metadatas = {"default": sa_ext.metadata}

        if not metadatas:
            raise RuntimeError(
                "When not using Flask-SQLAlchemy, pass 'metadatas' when"
                " creating the Alembic extension."
            )

        if not engines and sa_ext is not None:
            engines = sa_ext.engines

            if None in sa_ext.engines:
                # Re-key Flask-SQLAlchemy default engine.
                engines = engines.copy()
                engines["default"] = sa_ext.engine

        if not engines:
            raise RuntimeError(
                "Either use Flask-SQLAlchemy(-Lite) with engines configured, or"
                " pass 'engines' when creating the Alembic extension."
            )

        missing = metadatas.keys() - engines.keys()

        if missing:
            plural = "config" if len(missing) == 1 else "configs"
            missing_str = ", ".join(f"'{n}'" for n in missing)
            raise RuntimeError(f"Missing engine {plural} for {missing_str}.")

        cache.engines = engines
        cache.metadatas = metadatas
        return engines, metadatas

    @property
    def migration_contexts(self) -> dict[str, MigrationContext]:
        """Get the map of Alembic
        :class:`~alembic.runtime.migration.MigrationContext` for each configured
        database key for the current app. Each context's connection will be
        closed when the Flask application context ends.

        .. versionadded:: 3.1
        """
        cache = self._get_cache()

        if cache.contexts is not None:
            return cache.contexts

        engines, metadatas = self._prepare_targets()
        env = self.environment_context
        config = current_app.config["ALEMBIC_CONTEXT"]
        cache.contexts = {}

        if len(metadatas) == 1:
            env.configure(
                connection=engines["default"].connect(),
                target_metadata=metadatas["default"],
                **config,
            )
            cache.contexts["default"] = env.get_context()
        else:
            for name in metadatas:
                # Set the upgrade and downgrade tokens for each context.
                env.configure(
                    connection=engines[name].connect(),
                    target_metadata=metadatas[name],
                    upgrade_token=f"{name}_upgrades",
                    downgrade_token=f"{name}_downgrades",
                    **config,
                )
                cache.contexts[name] = env.get_context()
                # The migration context is passed a reference to the env's
                # context_ops dict. Copy and replace it so that the next
                # context is isolated from this one.
                env.context_opts = env.context_opts.copy()

        return cache.contexts

    @property
    def migration_context(self) -> MigrationContext:
        """Get the Alembic
        :class:`~alembic.runtime.migration.MigrationContext` for the current
        app. If multiple databases are configured, this is the context for the
        ``"default"`` key. The context's connection will be closed when the
        Flask application context ends.
        """
        return self.migration_contexts["default"]

    @property
    def ops(self) -> dict[str, Operations]:
        """Get the Alembic :class:`~alembic.operations.Operations` context for
        each configured database key for the current app.

        .. versionadded:: 3.1
        """
        cache = self._get_cache()

        if cache.ops is not None:
            return cache.ops

        cache.ops = {}

        for name, _context in self.migration_contexts.items():
            cache.ops[name] = Operations(self.migration_context)

        return cache.ops

    @property
    def op(self) -> Operations:
        """Get the Alembic :class:`~alembic.operations.Operations` context for
        the current app. If multiple databases are configured, this is the
        context for the ``"default"`` key.
        """
        return self.ops["default"]

    def run_migrations(
        self,
        fn: t.Callable[
            [str | list[str] | tuple[str, ...], MigrationContext], list[MigrationStep]
        ],
        **kwargs: t.Any,
    ) -> None:
        """Configure an Alembic
        :class:`~alembic.runtime.migration.MigrationContext` to run
        migrations for the given function.

        This takes the place of Alembic's ``env.py`` file, specifically
        the ``run_migrations_online`` function.

        :param fn: Use this function to control what migrations are run.
        :param kwargs: Extra arguments passed to ``upgrade`` or
            ``downgrade`` in each revision.

        .. versionchanged:: 3.1
            Support multiple databases.
        """
        contexts = self.migration_contexts
        multi = len(contexts) > 1

        # Enter all transactions before running any migrations. If any
        # migrations fail, all will be rolled back. Otherwise, each will commit
        # and if any commit fails, the remainder will be rolled back.
        with ExitStack() as stack:
            for context in contexts.values():
                stack.enter_context(context.begin_transaction())

            for name, context in contexts.items():
                # env.configure would have set this, but it wasn't available
                # when creating the contexts. There's no public way to set it.
                context._migrations_fn = fn  # type: ignore[assignment]

                if multi:
                    kwargs["engine_name"] = name

                # env.run_migrations would always use the last configured
                # context. Do what it would with each context directly.
                with Operations.context(context):
                    context.run_migrations(**kwargs)

    def mkdir(self) -> None:
        """Create the script directory and template.

        Alembic's ``generic`` template is used if a single database is
        configured. The ``multidb`` template if multiple databases are
        configured.

        .. versionchanged:: 3.1
            Support multiple databases.
        """
        script_dir = self.config.get_main_option("script_location")
        assert script_dir is not None
        template = "multidb" if len(self.metadatas) > 1 else "generic"
        template_src = os.path.join(
            self.config.get_template_directory(), template, "script.py.mako"
        )
        template_dest = os.path.join(script_dir, "script.py.mako")

        if not os.access(template_src, os.F_OK):
            raise util.CommandError(f"Template {template_src} does not exist")

        if not os.access(script_dir, os.F_OK):
            os.makedirs(script_dir)

        if not os.access(template_dest, os.F_OK):
            shutil.copy(template_src, template_dest)

        for version_location in self.script_directory._version_locations:
            if not os.access(version_location, os.F_OK):
                os.makedirs(version_location)

    def current(self) -> tuple[Script, ...]:
        """Get the list of current revisions."""
        return self.script_directory.get_revisions(
            self.migration_context.get_current_heads()
        )

    def heads(self, resolve_dependencies: bool = False) -> tuple[Script, ...]:
        """Get the list of revisions that have no child revisions.

        :param resolve_dependencies: Treat dependencies as down
            revisions.
        """
        if resolve_dependencies:
            return self.script_directory.get_revisions("heads")

        return self.script_directory.get_revisions(self.script_directory.get_heads())

    def branches(self) -> list[Script]:
        """Get the list of revisions that have more than one next
        revision.
        """
        return [
            revision
            for revision in self.script_directory.walk_revisions()
            if revision.is_branch_point
        ]

    def _simplify_rev(
        self,
        rev: t_rev | int,
        handle_current: bool = False,
        handle_int: bool = False,
    ) -> list[str]:
        if isinstance(rev, str):
            if rev == "current" and handle_current:
                return [r.revision for r in self.current()]
            elif handle_int:
                try:
                    return [f"{int(rev):+d}"]
                except ValueError:
                    return [rev]
            else:
                return [rev]

        if isinstance(rev, Script):
            return [rev.revision]

        if isinstance(rev, int):
            # Positive relative ids must have + prefix.
            return [f"{rev:+d}"]

        return [r.revision if isinstance(r, Script) else r for r in rev]

    def log(self, start: t_rev = "base", end: t_rev = "heads") -> list[Script]:
        """Get the list of revisions in the order they will run.

        :param start: Only get entries since this revision.
        :param end: Only get entries until this revision.
        """
        return list(
            self.script_directory.walk_revisions(
                self._simplify_rev(start, handle_current=True),  # type: ignore[arg-type]
                self._simplify_rev(end, handle_current=True),  # type: ignore[arg-type]
            )
        )

    def stamp(self, target: t_rev = "heads") -> None:
        """Set the current database revision without running migrations.

        :param target: Revision to set to.
        """
        target_arg = self._simplify_rev(target)

        def do_stamp(
            revision: str | list[str] | tuple[str, ...], context: MigrationContext
        ) -> list[MigrationStep]:
            return self.script_directory._stamp_revs(target_arg, revision)  # type: ignore[return-value]

        self.run_migrations(do_stamp)

    def upgrade(self, target: int | str | Script = "heads") -> None:
        """Run migrations to upgrade database.

        :param target: Revision to go up to.
        """
        target_arg: list[str] | str = self._simplify_rev(target, handle_int=True)

        if len(target_arg) == 1:
            # Despite its signature, _upgrade_revs can take a list of ids. But
            # if it's a relative id (+1), it must be a single value.
            target_arg = target_arg[0]

        def do_upgrade(
            revision: str | list[str] | tuple[str, ...], context: MigrationContext
        ) -> list[MigrationStep]:
            return self.script_directory._upgrade_revs(  # type: ignore[return-value]
                target_arg,  # type: ignore[arg-type]
                revision,  # type: ignore[arg-type]
            )

        self.run_migrations(do_upgrade)

    def downgrade(self, target: int | str | Script = -1) -> None:
        """Run migrations to downgrade database.

        :param target: Revision to go down to.
        """
        # Unlike upgrade, downgrade always requires a single id.
        target_arg = self._simplify_rev(target, handle_int=True)[0]

        def do_downgrade(
            revision: str | list[str] | tuple[str, ...], context: MigrationContext
        ) -> list[MigrationStep]:
            return self.script_directory._downgrade_revs(  # type: ignore[return-value]
                target_arg,
                revision,  # type: ignore[arg-type]
            )

        self.run_migrations(do_downgrade)

    def revision(
        self,
        message: str,
        empty: bool = False,
        branch: str = "default",
        parent: t_rev = "head",
        splice: bool = False,
        depend: t_rev | None = None,
        label: str | list[str] | None = None,
        path: str | None = None,
    ) -> list[Script | None]:
        """Create a new revision. By default, auto-generate operations
        by comparing models and database.

        :param message: Description of revision.
        :param empty: Don't auto-generate operations.
        :param branch: Use this independent branch name.
        :param parent: Parent revision(s) of this revision.
        :param splice: Allow non-head parent revision.
        :param depend: Revision(s) this revision depends on.
        :param label: Label(s) to apply to this revision.
        :param path: Where to store this revision.
        :return: List of new revisions.
        """
        parent_arg = self._simplify_rev(parent)
        depend_arg = self._simplify_rev(depend) if depend is not None else None

        if label is None:
            label = []
        elif isinstance(label, str):
            label = [label]
        else:
            label = list(label)

        # manage independent branches
        if branch:
            for i, item in enumerate(parent_arg):
                if item in ("base", "head"):
                    parent_arg[i] = f"{branch}@{item}"

            if not path:
                branch_path = dict(
                    item
                    for item in current_app.config["ALEMBIC"]["version_locations"]
                    if not isinstance(item, str)
                ).get(branch)

                if branch_path:
                    path = branch_path

            try:
                branch_exists = any(
                    r
                    for r in self.script_directory.revision_map.get_revisions(branch)
                    if r is not None
                )
            except ResolutionError:
                branch_exists = False

            if not branch_exists:
                # label the first revision of a separate branch and start it from base
                label.insert(0, branch)
                parent_arg = ["base"]

        if not path:
            path = self.script_directory.dir

        # relative path is relative to app root
        if path and not os.path.isabs(path) and ":" not in path:
            path = os.path.join(current_app.root_path, path)

        revision_context = autogenerate.RevisionContext(
            self.config,
            self.script_directory,
            {
                "message": message,
                "sql": False,
                "head": parent_arg,
                "splice": splice,
                "branch_label": label,
                "version_path": path,
                "rev_id": self.rev_id(),
                "depends_on": depend_arg,
            },
        )

        def do_revision(
            revision: str | list[str] | tuple[str, ...], context: MigrationContext
        ) -> list[MigrationStep]:
            if empty:
                revision_context.run_no_autogenerate(revision, context)
            else:
                revision_context.run_autogenerate(revision, context)

            return []

        if not empty or util.asbool(
            self.config.get_main_option("revision_environment")
        ):
            self.run_migrations(do_revision)

        return list(revision_context.generate_scripts())

    def merge(
        self,
        revisions: t_rev = "heads",
        message: str | None = None,
        label: str | list[str] | None = None,
    ) -> Script | None:
        """Create a merge revision.

        :param revisions: Revisions to merge.
        :param message: Description of merge, will default to
            ``revisions`` param.
        :param label: Label(s) to apply to this revision.
        :return: A new revision object.
        """
        revisions_arg = self._simplify_rev(revisions)

        if message is None:
            message = f"merge {', '.join(revisions_arg)}"

        return self.script_directory.generate_revision(
            revid=self.rev_id(),
            message=message,
            head=revisions_arg,
            branch_labels=label,
            config=self.config,
        )

    def produce_migrations(self) -> MigrationScript:
        """Generate the :class:`~alembic.operations.ops.MigrationScript`
        object that would generate a new revision.
        """
        scripts = []

        for context in self.migration_contexts.values():
            scripts.append(
                autogenerate.produce_migrations(
                    context, context.opts["target_metadata"]
                )
            )

        script = scripts[0]

        if len(scripts) > 1:
            # Combine the ops for each database into one script.
            script.upgrade_ops = [s.upgrade_ops for s in scripts]  # type: ignore[assignment]
            script.downgrade_ops = [s.downgrade_ops for s in scripts]  # type: ignore[assignment]

        return script

    def compare_metadata(self) -> list[tuple[t.Any, ...]]:
        """Describe the operations that would be present in a new revision.

        This only supports a single database. For multiple databases, use the
        following instead:

        .. code-block:: python

            for ops in alembic.produce_migrations().upgrade_ops_list:
                name = ops.upgrade_token.removesuffix("_upgrades")
                diff = ops.as_diffs()
        """
        script = self.produce_migrations()
        assert script.upgrade_ops is not None
        return script.upgrade_ops.as_diffs()  # type: ignore[no-any-return]


@dataclasses.dataclass
class _Cache:
    """Cached Alembic objects for a given Flask app."""

    engines: dict[str, sa.Engine] | None = None
    metadatas: dict[str, sa.MetaData | list[sa.MetaData]] | None = None
    config: Config | None = None
    script: ScriptDirectory | None = None
    env: EnvironmentContext | None = None
    contexts: dict[str, MigrationContext] | None = None
    ops: dict[str, Operations] | None = None

    def clear(self, exc: BaseException | None = None) -> None:
        """Clear the cached Alembic objects. Not all objects are cleared, only
        those with connections that must be recreated on next access.

        This is called automatically during app context teardown.
        """
        if self.contexts is not None:
            for context in self.contexts.values():
                if context.connection is not None:
                    context.connection.close()

        self.contexts = None
        self.ops = None
