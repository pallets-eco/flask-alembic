from alembic import autogenerate, util
import os
from flask_alembic import current_alembic


def init():
    config = current_alembic.config
    script_dir = config.get_main_option('script_location')
    template_src = os.path.join(config.get_template_directory(), 'generic', 'script.py.mako')
    template_dest = os.path.join(script_dir, 'script.py.mako')

    if os.access(script_dir, os.F_OK):
        raise util.CommandError('Directory {0} already exists'.format(script_dir))

    if not os.access(template_src, os.F_OK):
        raise util.CommandError('Template {0} does not exist'.format(template_src))

    util.status('Creating directory {0}'.format(script_dir), os.makedirs, script_dir)
    current_alembic.script._copy_file(template_src, template_dest)


def current():
    script = current_alembic.script
    context = current_alembic.context

    return script.get_revision(context.get_current_revision())


def stamp(revision):
    context = current_alembic.context
    context._update_current_rev(context.get_current_revision(), revision)


def history(revision_range=None):
    if revision_range is not None:
        if revision_range.count(':') != 1:
            raise util.CommandError('History range requires [start]:[end], [start]:, or :[end]')

        start, end = revision_range.strip().split(':')

        if not start:
            start = 'base'
        elif start == 'current':
            start = current().revision

        if not end:
            end = 'head'
        elif end == 'current':
            end = current().revision
    else:
        start, end = 'base', 'head'

    return list(current_alembic.script.walk_revisions(start, end))


def branches():
    return [revision for revision in current_alembic.script.walk_revisions() if revision.is_branch_point]


def upgrade(target='head'):
    def do_upgrade(revision, context):
        return current_alembic.script._upgrade_revs(target, revision)

    current_alembic.run_migrations(do_upgrade)


def downgrade(target='-1'):
    def do_downgrade(revision, context):
        return current_alembic.script._downgrade_revs(target, revision)

    current_alembic.run_migrations(do_downgrade)


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
            if script.get_revision(revision) is not script.get_revision('head'):
                raise util.CommandError('Target database is not up to date')

            autogenerate._produce_migration_diffs(context, template_args, set())

            return []

    use_env = util.asbool(config.get_main_option('revision_environment'))

    if not empty or use_env:
        current_alembic.run_migrations(do_revision)

    return script.generate_revision(util.rev_id(), message, True, **template_args)
