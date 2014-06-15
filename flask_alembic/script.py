from flask import current_app
from flask_script import Manager

manager = Manager(help='Perform database migrations.', description='Perform database migrations.')


def get_alembic():
    """Get the alembic extension for the current app."""

    return current_app.extensions['alembic']


@manager.command
def mkdir():
    """Create the migration directory if it does not exist."""

    get_alembic().mkdir()


@manager.option('-v', '--verbose', action='store_true', help='Show more information.')
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


@manager.option('revision', default='head', help='Identifier to set as current')
def stamp(revision):
    """Set the current revision without running migrations."""

    get_alembic().stamp(revision)


@manager.option('-v', '--verbose', action='store_true', help='Show more information.')
@manager.option('range', nargs='?', help='Format [start]:[end], accepts identifier, "base", "head", or "current".')
def history(range=None, verbose=False):
    """Show the revision upgrade path."""

    a = get_alembic()
    print_stdout = a.config.print_stdout

    for revision in a.history(range):
        if verbose:
            print_stdout(revision.log_entry)
        else:
            print_stdout(revision)


@manager.option('target', nargs='?', default='head', help='Identifier to upgrade to, or +N relative to current.')
def upgrade(target='head'):
    """Run migrations to upgrade the database."""

    get_alembic().upgrade(target)


@manager.option('target', nargs='?', default=-1, help='Identifier to downgrade to, or -N relative to current.')
def downgrade(target=-1):
    """Run migration to downgrade the database."""

    get_alembic().downgrade(target)


@manager.option('--empty', action='store_true', help='Do not auto-generate operations.')
@manager.option('message', help='Description of changes in this revision.')
def revision(message, empty=False):
    """Generate a new revision."""

    get_alembic().revision(message, empty)
