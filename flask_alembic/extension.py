from __future__ import absolute_import
import os
import shutil
from alembic import autogenerate, util
from alembic.config import Config
from alembic.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from flask import current_app


class Alembic(object):
    def __init__(self, app=None, makedir=True):
        self._cache = {}

        if app is not None:
            self.init_app(app, makedir)

    def init_app(self, app, makedir=True):
        app.extensions['alembic'] = self

        config = app.config.setdefault('ALEMBIC', {})
        config.setdefault('script_location', 'migrations')
        app.config.setdefault('ALEMBIC_CONTEXT', {})

        self._cache[app] = {}

        app.teardown_appcontext(self._clear_cache)

        if makedir:
            self.mkdir(app)

    def _clear_cache(self, exc=None):
        cache = self._get_cache()

        if 'context' in cache:
            cache['context'].connection.close()

        cache.clear()

    def _get_app(self, app=None):
        return app or current_app._get_current_object()

    def _get_cache(self, app=None):
        return self._cache[self._get_app(app)]

    def _get_config(self, app=None):
        app = self._get_app(app)
        cache = self._get_cache(app)

        if 'config' not in cache:
            cache['config'] = c = Config()

            for key, value in app.config['ALEMBIC'].iteritems():
                if key == 'script_location' and not os.path.isabs(value) and ':' not in value:
                    value = os.path.join(app.root_path, value)

                c.set_main_option(key, value)

        return cache['config']

    @property
    def config(self):
        return self._get_config()

    @property
    def script(self, app=None):
        cache = self._get_cache(app)

        if 'script' not in cache:
            cache['script'] = sd = ScriptDirectory.from_config(self.config)
            sd.versions = sd.dir

        return cache['script']

    @property
    def env(self):
        cache = self._get_cache()

        if 'env' not in cache:
            cache['env'] = EnvironmentContext(self.config, self.script)

        return cache['env']

    @property
    def context(self):
        cache = self._get_cache()

        if 'context' not in cache:
            db = current_app.extensions['sqlalchemy'].db
            conn = db.engine.connect()

            env = self.env
            env.configure(connection=conn, target_metadata=db.metadata)
            cache['context'] = env.get_context()

        return cache['context']

    def run_migrations(self, fn, **kwargs):
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
        script = self.script
        context = self.context

        return script.get_revision(context.get_current_revision())

    def stamp(self, revision='head'):
        script = self.script
        context = self.context

        dest = script.get_revision(revision)
        dest = dest and dest.revision

        context._update_current_rev(context.get_current_revision(), dest)

    def history(self, range=None):
        if range is not None:
            if range.count(':') != 1:
                raise util.CommandError('History range requires [start]:[end], [start]:, or :[end]')

            start, end = range.strip().split(':')

            if not start:
                start = 'base'
            elif start == 'current':
                start = self.current().revision

            if not end:
                end = 'head'
            elif end == 'current':
                end = self.current().revision
        else:
            start, end = 'base', 'head'

        return list(self.script.walk_revisions(start, end))

    def branches(self):
        return [revision for revision in self.script.walk_revisions() if revision.is_branch_point]

    def upgrade(self, target='head'):
        def do_upgrade(revision, context):
            return self.script._upgrade_revs(str(target), revision)

        self.run_migrations(do_upgrade)

    def downgrade(self, target=-1):
        def do_downgrade(revision, context):
            return self.script._downgrade_revs(str(target), revision)

        self.run_migrations(do_downgrade)

    def revision(self, message, empty=False):
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
