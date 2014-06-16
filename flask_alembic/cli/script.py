"""Integration with Flask-Script::

    from flask_alembic.cli.script import manager as alembic_manager
    manager.add_command('db', alembic_manager)

\\
"""
from flask_script import Manager
from flask_alembic.cli import base

manager = Manager(help='Perform database migrations.', description='Perform database migrations.')


@manager.command
def mkdir():
    """Make migration directory.."""
    base.mkdir()


@manager.option('-v', '--verbose', action='store_true')
def current(verbose):
    """Show current revision.."""
    base.current(verbose)


@manager.option('revision', nargs='?', default='head')
def stamp(revision):
    """Set current revision."""
    base.stamp(revision)


@manager.option('--start', default='base', help='Show since this revision.')
@manager.option('--end', default='head', help='Show until this revision.')
@manager.option('-v', '--verbose', action='store_true')
def log(start, end, verbose):
    """Show revision log."""
    base.log(start, end, verbose)


@manager.command
def branches():
    """Show branches in upgrade path."""
    base.branches()


@manager.option('target', nargs='?', default='head')
def upgrade(target):
    """Run upgrade migrations."""
    base.upgrade(target)


@manager.option('target', nargs='?', default=-1)
def downgrade(target):
    """Run downgrade migrations."""
    base.downgrade(target)


@manager.option('message')
@manager.option('--empty', action='store_true', help='Create empty script.')
def revision(message, empty):
    """Create new migration."""
    base.revision(message, empty)
