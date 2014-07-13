from __future__ import absolute_import
import os
import shutil
from alembic import autogenerate, util
from alembic.config import Config
from alembic.environment import EnvironmentContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory
from flask import current_app
from flask._compat import iteritems


class Alembic(object):
    """Provide an Alembic environment and migration API.

    If instantiated without an app instance, :meth:`init_app` is used to register an app at a later time.

    :param app: call :meth:`init_app` on this app
    :param run_mkdir: whether to run :meth:`mkdir` during :meth:`init_app`
    """
    def __init__(self, app=None, run_mkdir=True):
        self._cache = {}
        self.run_mkdir = run_mkdir

        if app is not None:
            self.init_app(app)

    def init_app(self, app, run_mkdir=None):
        """Register this extension on an app.  Will automatically set up migration directory by default.

        :param app: app to register
        :param run_mkdir: whether to run :meth:`mkdir`
        """
        app.extensions['alembic'] = self

        config = app.config.setdefault('ALEMBIC', {})
        config.setdefault('script_location', 'migrations')
        app.config.setdefault('ALEMBIC_CONTEXT', {})

        self._cache[app] = {}

        app.teardown_appcontext(self._clear_cache)

        if run_mkdir or self.run_mkdir:
            self.mkdir(app)

    def _clear_cache(self, exc=None):
        """Clear the cached objects for the current app.

        :param exc: exception from teardown handler
        """
        cache = self._get_cache()

        if 'context' in cache:
            cache['context'].connection.close()

        cache.clear()

    def _get_app(self, app=None):
        """Get an app instance to operate on.

        :param app: if None, use current_app
        """
        return app or current_app._get_current_object()

    def _get_cache(self, app=None):
        """Get the cache for the given app.

        :param app: if None, use current_app
        """
        return self._cache[self._get_app(app)]

    def _get_config(self, app=None):
        """Get the Alembic :meth:`Config`.

        Is exposed as a method instead of a property so that :meth:`mkdir` can be called without an app context during :meth:`init_app`.

        :param app: get config from this app, or current_app
        :return: Alembic config instance
        """
        app = self._get_app(app)
        cache = self._get_cache(app)

        if 'config' not in cache:
            cache['config'] = c = Config()

            for key, value in iteritems(app.config['ALEMBIC']):
                if key == 'script_location' and not os.path.isabs(value) and ':' not in value:
                    value = os.path.join(app.root_path, value)

                c.set_main_option(key, value)

        return cache['config']

    @property
    def config(self):
        """Get the Alembic :class:`~alembic.config.Config` for the current app."""
        return self._get_config()

    @property
    def script(self):
        """Get the Alembic :class:`~alembic.script.ScriptDirectory` for the current app."""
        cache = self._get_cache()

        if 'script' not in cache:
            cache['script'] = sd = ScriptDirectory.from_config(self.config)
            sd.versions = sd.dir

        return cache['script']

    @property
    def env(self):
        """Get the Alembic :class:`~alembic.environment.EnvironmentContext` for the current app."""
        cache = self._get_cache()

        if 'env' not in cache:
            cache['env'] = EnvironmentContext(self.config, self.script)

        return cache['env']

    @property
    def context(self):
        """Get the Alembic :class:`~alembic.migration.MigrationContext` for the current app."""
        cache = self._get_cache()

        if 'context' not in cache:
            db = current_app.extensions['sqlalchemy'].db
            conn = db.engine.connect()

            env = self.env
            env.configure(
                connection=conn, target_metadata=db.metadata,
                **current_app.config['ALEMBIC_CONTEXT']
            )
            cache['context'] = env.get_context()

        return cache['context']

    @property
    def op(self):
        """Get the Alembic :class:`~alembic.operations.Operations` context for the current app."""
        cache = self._get_cache()

        if 'op' not in cache:
            cache['op'] = Operations(self.context)

        return cache['op']

    def run_migrations(self, fn, **kwargs):
        """Configure an Alembic :class:`~alembic.migration.MigrationContext` to run migrations for the given function.

        This takes the place of Alembic's env.py file, specifically the ``run_migrations_online`` function.

        :param fn: use this function to control what migrations are run
        :param kwargs: extra arguments passed to revision function
        """
        db = current_app.extensions['sqlalchemy'].db
        conn = db.engine.connect()

        env = self.env
        env.configure(
            connection=conn, target_metadata=db.metadata, fn=fn,
            **current_app.config['ALEMBIC_CONTEXT']
        )

        try:
            with env.begin_transaction():
                env.run_migrations(**kwargs)
        finally:
            conn.close()

    def mkdir(self, app=None, ignore_existing=True):
        """Create the migration directory and script template.

        :param app: used during :meth:`init_app` to operate without an app context
        :param ignore_existing: don't raise an error if directory already exists
        :return: True if directory was created
        """
        config = self._get_config(app)
        script_dir = config.get_main_option('script_location')
        template_src = os.path.join(config.get_template_directory(), 'generic', 'script.py.mako')
        template_dest = os.path.join(script_dir, 'script.py.mako')

        if os.access(script_dir, os.F_OK):
            if ignore_existing:
                return False

            raise util.CommandError('Directory {0} already exists'.format(script_dir))

        if not os.access(template_src, os.F_OK):
            raise util.CommandError('Template {0} does not exist'.format(template_src))

        os.makedirs(script_dir)
        shutil.copy(template_src, template_dest)
        return True

    def current(self):
        """Get the current database revision."""
        script = self.script
        context = self.context

        return script.get_revision(context.get_current_revision())

    def stamp(self, revision='head'):
        """Set the current database revision without running migrations.

        :param revision: revision to set to, default 'head'
        """
        script = self.script
        context = self.context

        dest = script.get_revision(revision)
        dest = dest and dest.revision

        context._update_current_rev(context.get_current_revision(), dest)

    def log(self, start='base', end='head'):
        """Get a list of revisions in the order they will run.

        :param start: only get since this revision
        :param end: only get until this revision
        :return: list of revisions in order
        """
        if start is None:
            start = 'base'
        elif start == 'current':
            r = self.current()
            start = r.revision if r else None
        else:
            start = str(start)

        if end is None:
            end = 'head'
        elif end == 'current':
            r = self.current()
            end = r.revision if r else None
        else:
            end = str(end)

        return list(self.script.walk_revisions(start, end))

    def branches(self):
        """Get a list of revisions that have more than one next revision.

        :return: list of branchpoint revisions
        """
        return [revision for revision in self.script.walk_revisions() if revision.is_branch_point]

    def upgrade(self, target='head'):
        """Run migrations to upgrade database.

        :param target: revision to go to, default 'head'
        """
        def do_upgrade(revision, context):
            return self.script._upgrade_revs(str(target), revision)

        self.run_migrations(do_upgrade)

    def downgrade(self, target=-1):
        """Run migrations to downgrade database.

        :param target: revision to go down to, default -1
        """
        def do_downgrade(revision, context):
            return self.script._downgrade_revs(str(target), revision)

        self.run_migrations(do_downgrade)

    def revision(self, message, empty=False):
        """Create a new revision.  By default, auto-generate operations by comparing models and database.

        :param message: description of revision
        :param empty: don't auto-generate operations
        :return: new revision
        """
        config = self.config
        script = self.script

        template_args = {
            'config': config
        }

        if empty:
            def do_revision(revision, context):
                return []
        else:
            def do_revision(revision, context):
                if script.get_revision(revision) is not script.get_revision('head'):
                    raise util.CommandError('Target database is not up to date')

                autogenerate._produce_migration_diffs(context, template_args, set())

                return []

        use_env = util.asbool(config.get_main_option('revision_environment'))

        if not empty or use_env:
            self.run_migrations(do_revision)

        return script.generate_revision(util.rev_id(), message, True, **template_args)

    def compare_metadata(self):
        """Generate a list of operations that would be present in a new revision."""

        db = self._get_app().extensions['sqlalchemy'].db
        return autogenerate.compare_metadata(self.context, db.metadata)
