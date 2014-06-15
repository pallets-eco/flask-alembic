"""Base functions that write information to the terminal."""
from flask import current_app


def get_alembic():
    """Get the alembic extension for the current app."""
    return current_app.extensions['alembic']


def mkdir():
    """Create the migration directory if it does not exist."""
    get_alembic().mkdir()


def current(verbose=False):
    """Show the current revision."""
    a = get_alembic()
    revision = a.current()

    if revision is None:
        a.config.print_stdout(None)
    elif verbose:
        a.config.print_stdout(revision.log_entry)
    else:
        a.config.print_stdout(revision)


def stamp(revision):
    """Set the current revision without running migrations."""
    get_alembic().stamp(revision)


def log(start='base', end='head', verbose=False):
    """Show the revision upgrade path."""
    a = get_alembic()
    print_stdout = a.config.print_stdout

    for revision in a.log(start, end):
        if verbose:
            print_stdout(revision.log_entry)
        else:
            print_stdout(revision)


def branches():
    """Show any branches that must be resolved."""
    a = get_alembic()
    print_stdout = a.config.print_stdout
    script = a.script

    for point in a.branches():
        print_stdout(point)

        indent = ' ' * len(str(point.down_revision))

        for branch in point.nextrev:
            print_stdout('{0} -> {1}'.format(indent, script.get_revision(branch)))


def upgrade(target='head'):
    """Run migrations to upgrade the database."""
    get_alembic().upgrade(target)


def downgrade(target=-1):
    """Run migration to downgrade the database."""
    get_alembic().downgrade(target)


def revision(message, empty=False):
    """Generate a new revision."""
    get_alembic().revision(message, empty)
