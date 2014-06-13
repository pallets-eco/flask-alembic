from alembic.script import Script
from tick.ext.alembic import prepare


def _adapt_revision(script_directory, revision):
    if isinstance(revision, Script):
        return revision

    return script_directory.get_revision(revision)


def init():
    pass


def current():
    return prepare().migration_context.get_current_revision()


def stamp(revision):
    p = prepare()
    new = _adapt_revision(p.script_directory, revision)
    p.migration_context._update_current_rev(current(), new)


def history(rev_range=None):
    pass


def branches():
    pass


def upgrade(revision):
    pass


def downgrade(revision):
    pass


def revision(message, empty=False):
    pass
