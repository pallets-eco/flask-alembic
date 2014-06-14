from __future__ import absolute_import
import os
from alembic.config import Config
from alembic.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from flask import current_app
from werkzeug.local import LocalProxy


class Alembic(object):
    def __init__(self, app=None):
        self._cache = {}

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.extensions['alembic'] = self

        config = app.config.setdefault('ALEMBIC', {})
        config.setdefault('script_location', 'migrations')
        app.config.setdefault('ALEMBIC_CONTEXT', {})

        self._cache[app] = {}

        app.teardown_appcontext(self._clear_cache)

    def _clear_cache(self, exc=None):
        cache = self._get_cache()

        if 'context' in cache:
            cache['context'].connection.close()

        cache.clear()

    def _get_cache(self):
        return self._cache[current_app._get_current_object()]

    @property
    def config(self):
        cache = self._get_cache()

        if 'config' not in cache:
            cache['config'] = c = Config()

            for key, value in current_app.config['ALEMBIC'].iteritems():
                if key == 'script_location' and not os.path.isabs(value) and ':' not in value:
                    value = os.path.join(current_app.root_path, value)

                c.set_main_option(key, value)

        return cache['config']

    @property
    def script(self):
        cache = self._get_cache()

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
        env.configure(connection=conn, target_metadata=db.metadata, fn=fn)

        try:
            with env.begin_transaction():
                env.run_migrations(**kwargs)
        finally:
            conn.close()


current_alembic = LocalProxy(lambda: current_app.extensions['alembic'])
