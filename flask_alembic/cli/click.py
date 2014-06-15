from __future__ import absolute_import
import click
from flask_alembic import command


@click.group()
def cli():
    """Perform database migrations."""

    pass


@cli.command()
def mkdir():
    """Make migration directory."""

    command.mkdir()


@cli.command()
@click.option('-v', '--verbose', is_flag=True)
def current(verbose):
    """Show current revision."""

    command.current(verbose)


@cli.command()
@click.argument('revision', default='head')
def stamp(revision):
    """Set current revision."""

    command.stamp(revision)


@cli.command()
@click.option('--start', default='base', help='Show since this revision.')
@click.option('--end', default='head', help='Show until this revision.')
@click.option('-v', '--verbose', is_flag=True)
def log(start, end, verbose):
    """Show revision log."""

    command.log(start, end, verbose)


@cli.command()
def branches():
    """Show branches in upgrade path."""

    command.branches()


@cli.command()
@click.argument('target', default='head')
def upgrade(target):
    """Run upgrade migrations."""

    command.upgrade(target)


@cli.command()
@click.argument('target', default='-1')
def downgrade(target):
    """Run downgrade migrations."""

    command.downgrade(target)


@cli.command()
@click.argument('message')
@click.option('--empty', is_flag=True, help='Create empty script.')
def revision(message, empty):
    """Create new migration."""

    command.revision(message, empty)
