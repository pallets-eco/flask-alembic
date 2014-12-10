from __future__ import absolute_import
from collections.abc import Iterable
from alembic.revision import ResolutionError
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
        config.setdefault('version_locations', [])
        app.config.setdefault('ALEMBIC_CONTEXT', {})

        self._cache[app] = {}

        app.teardown_appcontext(self._clear_cache)

        if run_mkdir or (run_mkdir is None and self.run_mkdir):
            with app.app_context():
                self.mkdir()

    def _clear_cache(self, exc=None):
        """Clear the cached objects for the given app.

        This is called automatically during app context teardown.

        :param exc: exception from teardown handler
        :param app: if None, use current_app
        """

        cache = self._get_cache()

        if 'context' in cache:
            cache['context'].connection.close()

        cache.clear()

    def _get_cache(self):
        """Get the cache for the current app."""

        return self._cache[current_app._get_current_object()]

    @property
    def config(self):
        """Get the Alembic :class:`~alembic.config.Config` for the current app."""

        cache = self._get_cache()

        if 'config' not in cache:
            cache['config'] = c = Config()

            script_location = current_app.config['ALEMBIC']['script_location']

            if not os.path.isabs(script_location) and ':' not in script_location:
                script_location = os.path.join(current_app.root_path, script_location)

            version_locations = [script_location]

            for item in current_app.config['ALEMBIC']['version_locations']:
                version_location = item if isinstance(item, str) else item[1]

                if not os.path.isabs(version_location) and ':' not in version_location:
                    version_location = os.path.join(current_app.root_path, version_location)

                version_locations.append(version_location)

            c.set_main_option('script_location', script_location)
            c.set_main_option('version_locations', ','.join(version_locations))

            for key, value in iteritems(current_app.config['ALEMBIC']):
                if key in {'script_location', 'version_locations'}:
                    continue

                c.set_main_option(key, value)

        return cache['config']

    @property
    def script(self):
        """Get the Alembic :class:`~alembic.script.ScriptDirectory` for the current app."""

        cache = self._get_cache()

        if 'script' not in cache:
            cache['script'] = ScriptDirectory.from_config(self.config)

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

    def mkdir(self):
        """Create the script directory and template."""

        script_dir = self.config.get_main_option('script_location')
        template_src = os.path.join(self.config.get_template_directory(), 'generic', 'script.py.mako')
        template_dest = os.path.join(script_dir, 'script.py.mako')

        if not os.access(template_src, os.F_OK):
            raise util.CommandError('Template {0} does not exist'.format(template_src))

        if not os.access(script_dir, os.F_OK):
            os.makedirs(script_dir)

        if not os.access(template_dest, os.F_OK):
            shutil.copy(template_src, template_dest)

        for version_location in self.script._version_locations:
            if not os.access(version_location, os.F_OK):
                os.makedirs(version_location)

    def current(self):
        """Get the list of current revisions."""

        return self.script.get_revisions(self.context.get_current_heads())

    def heads(self, resolve_dependencies=False):
        """Get the list of revisions that have no child revisions.

        :param resolve_dependencies: treat dependencies as down revisions
        """

        if resolve_dependencies:
            return self.script.get_revisions('heads')

        return self.script.get_revisions(self.script.get_heads())

    def branches(self):
        """Get the list of revisions that have more than one next revision."""

        return [revision for revision in self.script.walk_revisions() if revision.is_branch_point]

    def log(self, start='base', end='heads'):
        """Get the list of revisions in the order they will run.

        :param start: only get since this revision
        :param end: only get until this revision
        """

        if start is None:
            start = 'base'
        elif start == 'current':
            start = [r.revision for r in self.current()]
        else:
            start = getattr(start, 'revision', start)

        if end is None:
            end = 'heads'
        elif end == 'current':
            end = [r.revision for r in self.current()]
        else:
            end = getattr(end, 'revision', end)

        return list(self.script.walk_revisions(start, end))

    def stamp(self, target='heads'):
        """Set the current database revision without running migrations.

        :param target: revision to set to, default 'heads'
        """

        if target is None:
            target = 'heads'
        else:
            target = getattr(target, 'revision', target)

        def do_stamp(revision, context):
            return self.script._stamp_revs(target, revision)

        self.run_migrations(do_stamp)

    def upgrade(self, target='heads'):
        """Run migrations to upgrade database.

        :param target: revision to go to, default 'heads'
        """

        if target is None:
            target = 'heads'
        else:
            target = getattr(target, 'revision', target)

        target = str(target)

        def do_upgrade(revision, context):
            return self.script._upgrade_revs(target, revision)

        self.run_migrations(do_upgrade)

    def downgrade(self, target=-1):
        """Run migrations to downgrade database.

        :param target: revision to go down to, default -1
        """

        try:
            target = int(target)
        except ValueError:
            target = getattr(target, 'revision', target)
        else:
            if target > 0:
                target = -target

        target = str(target)

        def do_downgrade(revision, context):
            return self.script._downgrade_revs(target, revision)

        self.run_migrations(do_downgrade)

    def revision(self, message, empty=False, head=None, splice=False, branch_labels=None, version_path=None):
        """Create a new revision.  By default, auto-generate operations by comparing models and database.

        :param message: description of revision
        :param empty: don't auto-generate operations
        :param head: base new revision off this revision
        :param splice: allow non-head base revision
        :param branch_labels: labels to apply to this revision
        :param version_path: where to store this revision
        :return: new revision
        """

        if head is None:
            head = 'head'
        else:
            head = getattr(head, 'revision', head)

        if branch_labels is None:
            branch_labels = []
        elif isinstance(branch_labels, str):
            branch_labels = [branch_labels]
        elif isinstance(branch_labels, Iterable):
            branch_labels = list(branch_labels)

        # import pdb; pdb.set_trace()

        branch = head.split('@')[0]
        path = dict(item for item in current_app.config['ALEMBIC']['version_locations'] if not isinstance(item, str)).get(branch)

        try:
            existing = [r for r in self.script.revision_map.get_revisions(head) if r is not None]
        except ResolutionError:
            existing = None

        if not existing and not version_path:
            if path is None:
                version_path = self.script.dir
            else:
                if not os.path.isabs(path) and ':' not in path:
                    path = os.path.join(current_app.root_path, path)

                version_path = path
                branch_labels.insert(0, head)

            head = 'base'

        template_args = {
            'config': self.config
        }

        if empty:
            def do_revision(revision, context):
                return []
        else:
            def do_revision(revision, context):
                if set(self.script.get_revisions(revision)) != set(self.script.get_revisions('heads')):
                    raise util.CommandError('Target database is not up to date')

                autogenerate._produce_migration_diffs(context, template_args, set())
                return []

        if not empty or util.asbool(self.config.get_main_option('revision_environment')):
            self.run_migrations(do_revision)

        return self.script.generate_revision(
            util.rev_id(), message,
            head=head, splice=splice,
            branch_labels=branch_labels, version_path=version_path,
            **template_args
        )

    def merge(self, revisions, message=None, branch_labels=None):
        """Create a merge revision.

        :param revisions: list of revisions to merge
        :param message: description of merge, will default to listing merged revisions
        :param branch_labels: labels to apply to this revision
        :return: new revision
        """

        revisions = [getattr(r, 'revision', r) for r in revisions]

        if message is None:
            message = 'merge {0}'.format(', '.join(revisions))

        return self.script.generate_revision(
            util.rev_id(), message,
            head=revisions,
            branch_labels=branch_labels,
            config=self.config
        )

    def compare_metadata(self):
        """Generate a list of operations that would be present in a new revision."""

        db = current_app.extensions['sqlalchemy'].db
        return autogenerate.compare_metadata(self.context, db.metadata)
