from __future__ import annotations

import dataclasses
import logging
import os
import shutil
import sys
import typing as t
from datetime import datetime
from datetime import timezone
from weakref import WeakKeyDictionary

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
    """

    def __init__(
        self,
        app: Flask | None = None,
        run_mkdir: bool = True,
        command_name: str = "db",
    ):
        self._cache: WeakKeyDictionary[Flask, _Cache] = WeakKeyDictionary()
        self.run_mkdir: bool = run_mkdir
        self.command_name: str = command_name

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
        run_mkdir: bool | None = None,
        command_name: str | None = None,
    ) -> None:
        """Register this extension on an app. Will automatically set up
        migration directory by default.

        Keyword arguments on this method override those set during
        :meth:`__init__` if not ``None``.

        :param app: App to register.
        :param run_mkdir: Run :meth:`mkdir` automatically.
        :param command_name: Register a Click command with this name, unless it
            is the empty string.
        """
        app.extensions["alembic"] = self

        config = app.config.setdefault("ALEMBIC", {})
        config.setdefault("script_location", "migrations")
        config.setdefault("version_locations", [])
        ctx = app.config.setdefault("ALEMBIC_CONTEXT", {})
        ctx.setdefault("compare_server_default", True)

        self._cache[app] = cache = _Cache()
        app.teardown_appcontext(cache.clear)

        if run_mkdir or (run_mkdir is None and self.run_mkdir):
            with app.app_context():
                self.mkdir()

        if command_name or (command_name is None and self.command_name):
            from .cli import cli

            app.cli.add_command(cli, command_name or self.command_name)

    def _get_cache(self) -> _Cache:
        """Get the cache of Alembic objects for the current app."""
        return self._cache[current_app._get_current_object()]  # type: ignore[attr-defined]

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

        if cache.config is None:
            cache.config = c = Config()

            script_location = current_app.config["ALEMBIC"]["script_location"]

            if not os.path.isabs(script_location) and ":" not in script_location:
                script_location = os.path.join(current_app.root_path, script_location)

            version_locations = [script_location]

            for item in current_app.config["ALEMBIC"]["version_locations"]:
                version_location = item if isinstance(item, str) else item[1]

                if not os.path.isabs(version_location) and ":" not in version_location:
                    version_location = os.path.join(
                        current_app.root_path, version_location
                    )

                version_locations.append(version_location)

            c.set_main_option("script_location", script_location)
            c.set_main_option("version_locations", ",".join(version_locations))

            for key, value in current_app.config["ALEMBIC"].items():
                if key in ("script_location", "version_locations"):
                    continue

                c.set_main_option(key, value)

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

    @property
    def migration_context(self) -> MigrationContext:
        """Get the Alembic
        :class:`~alembic.runtime.migration.MigrationContext` for the
        current app.

        Accessing this property opens a database connection but can't
        close it automatically. Make sure to call
        ``migration_context.connection.close()`` when you're done.
        """
        cache = self._get_cache()

        if cache.context is None:
            db = current_app.extensions["sqlalchemy"]
            env = self.environment_context
            conn = db.engine.connect()
            env.configure(
                connection=conn,
                target_metadata=db.metadata,
                **current_app.config["ALEMBIC_CONTEXT"],
            )
            cache.context = env.get_context()

        return cache.context

    @property
    def op(self) -> Operations:
        """Get the Alembic :class:`~alembic.operations.Operations`
        context for the current app.

        Accessing this property opens a database connection but can't
        close it automatically. Make sure to call
        ``migration_context.connection.close()`` when you're done.
        """
        cache = self._get_cache()

        if cache.op is None:
            cache.op = Operations(self.migration_context)

        return cache.op

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
        """
        db = current_app.extensions["sqlalchemy"]
        env = self.environment_context

        with db.engine.connect() as connection:
            env.configure(
                connection=connection,
                target_metadata=db.metadata,
                fn=fn,
                **current_app.config["ALEMBIC_CONTEXT"],
            )

            with env.begin_transaction():
                env.run_migrations(**kwargs)

    def mkdir(self) -> None:
        """Create the script directory and template."""
        script_dir = self.config.get_main_option("script_location")
        assert script_dir is not None
        template_src = os.path.join(
            self.config.get_template_directory(), "generic", "script.py.mako"
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
                    return [str(int(rev))]
                except ValueError:
                    return [rev]
            else:
                return [rev]

        if isinstance(rev, Script):
            return [rev.revision]

        if isinstance(rev, int):
            return [str(rev)]

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
        target_arg = self._simplify_rev(target, handle_int=True)

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
        target_arg = self._simplify_rev(target, handle_int=True)

        def do_downgrade(
            revision: str | list[str] | tuple[str, ...], context: MigrationContext
        ) -> list[MigrationStep]:
            return self.script_directory._downgrade_revs(  # type: ignore[return-value]
                target_arg,  # type: ignore[arg-type]
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
        db = current_app.extensions["sqlalchemy"]
        return autogenerate.produce_migrations(self.migration_context, db.metadata)

    def compare_metadata(self) -> list[tuple[t.Any, ...]]:
        """Generate a list of operations that would be present in a new
        revision.
        """
        db = current_app.extensions["sqlalchemy"]
        return autogenerate.compare_metadata(self.migration_context, db.metadata)  # type: ignore[no-any-return]


@dataclasses.dataclass
class _Cache:
    """Cached Alembic objects for a given Flask app."""

    config: Config | None = None
    script: ScriptDirectory | None = None
    env: EnvironmentContext | None = None
    context: MigrationContext | None = None
    op: Operations | None = None

    def clear(self, exc: BaseException | None = None) -> None:
        """Clear the cached Alembic objects.

        This is called automatically during app context teardown.

        :param exc: Exception from teardown handler.
        """
        if self.context is not None and self.context.connection is not None:
            self.context.connection.close()

        self.config = None
        self.script = None
        self.env = None
        self.context = None
        self.op = None
