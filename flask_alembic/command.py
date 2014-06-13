from alembic import autogenerate, util
from tick.ext.alembic import current_alembic, run_migrations


def adapt_revision(script, revision):
    if isinstance(revision, basestring):
        return script.get_revision(revision)

    return revision


def init():
    pass


def current():
    out = []

    def do_current(revision, context):
        out.append((context.connection.engine.url, revision))

        return []

    run_migrations(do_current)

    return out


def stamp(revision):
    script = current_alembic.script
    new = adapt_revision(script, revision)

    def do_stamp(revision, context):
        revision = adapt_revision(script, revision)
        context._update_current_rev(revision, new)

        return []

    run_migrations(do_stamp)


def history(rev_range=None):
    pass


def branches():
    pass


def upgrade(revision):
    pass


def downgrade(revision):
    pass


def revision(message, empty=False):
    config = current_alembic.config
    script = current_alembic.script

    template_args = {
        'config': config
    }

    if empty:
        def do_revision(revision, context):
            return []
    else:
        def do_revision(revision, context):
            if revision is not script.get_revision('head'):
                raise util.CommandError('Target database is not up to date')

            autogenerate._produce_migration_diffs(context, template_args, set())

            return []

    use_env = util.asbool(config.get_main_option('revision_environment'))

    if not empty or use_env:
        run_migrations(do_revision)

    script.generate_revision(util.rev_id(), message, True, **template_args)
