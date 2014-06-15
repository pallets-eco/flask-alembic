from flask_script import Manager
from flask_alembic import command

manager = Manager(help='Perform database migrations.', description='Perform database migrations.')


@manager.command
def mkdir():
    """Make migration directory.."""

    command.mkdir()


@manager.option('-v', '--verbose', action='store_true')
def current(verbose):
    """Show current revision.."""

    command.current(verbose)


@manager.option('revision', nargs='?', default='head')
def stamp(revision):
    """Set current revision."""

    command.stamp(revision)


@manager.option('--start', default='base', help='Show since this revision.')
@manager.option('--end', default='head', help='Show until this revision.')
@manager.option('-v', '--verbose', action='store_true')
def log(start, end, verbose):
    """Show revision log."""

    command.log(start, end, verbose)


@manager.command
def branches():
    """Show branches in upgrade path."""

    command.branches()


@manager.option('target', nargs='?', default='head')
def upgrade(target):
    """Run upgrade migrations."""

    command.upgrade(target)


@manager.option('target', nargs='?', default=-1)
def downgrade(target):
    """Run downgrade migrations."""

    command.downgrade(target)


@manager.option('message')
@manager.option('--empty', action='store_true', help='Create empty script.')
def revision(message, empty):
    """Create new migration."""

    command.revision(message, empty)
