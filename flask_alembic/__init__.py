from __future__ import absolute_import
from collections import namedtuple
from alembic.config import Config
from alembic.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from flask import current_app


PreparedContext = namedtuple(
    'PreparedContext',
    ['config', 'script_directory', 'environment_context', 'migration_context']
)


class Alembic(object):
    def __init__(self, app=None):
        self._prepare_cache = {}

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.extensions['alembic'] = self

        app.config.setdefault('ALEMBIC', {})
        app.config.setdefault('ALEMBIC_CONTEXT', {})

        self._prepare_cache[app] = prepare_cache = {}

        def clear_prepare_cache():
            prepare_cache.clear()

        app.teardown_appcontext(clear_prepare_cache)

    def make_config(self):
        c = Config()

        for key, value in current_app.config['ALEMBIC'].iteritems():
            c.set_main_option(key, value)

        return c

    def make_script_directory(self, config):
        sd = ScriptDirectory.from_config(config)
        sd.versions = sd.dir

        return sd

    def make_environment_context(self, config, script_directory):
        return EnvironmentContext(config, script_directory)

    def make_migration_context(self, environment_context, fn):
        db = current_app.extensions['sqlalchemy'].db
        connection = db.engine.connect()

        context = current_app.config['ALEMBIC_CONTEXT'].copy()
        context['fn'] = fn

        environment_context.configure(connection=connection, target_metadata=db.metadata, **context)

        return environment_context.get_context()

    def prepare(self, fn=None):
        cache = self._prepare_cache[current_app._get_current_object()]

        if fn in cache:
            return cache[fn]

        config = self.make_config()
        script_directory = self.make_script_directory(config)
        environment_context = self.make_environment_context(config, script_directory)
        migration_context = self.make_migration_context(environment_context, fn)

        context = PreparedContext(config, script_directory, environment_context, migration_context)
        cache[fn] = context

        return context

    def run(self, context=None, fn=None):
        if context is None or fn is not None:
            context = self.prepare(fn)

        migration_context = context.migration_context

        try:
            with migration_context.begin_transaction():
                migration_context.run_migrations()
        finally:
            migration_context.connection.close()


def prepare(fn=None):
    return current_app.extensions['alembic'].prepare(fn)


def run(fn=None):
    return current_app.extensions['alembic'].run(fn=fn)
