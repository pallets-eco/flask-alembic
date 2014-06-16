"""Integration with Click::

    from flask_alembic.cli.click import cli as alembic_cli
    app.cli.add_command(alembic_cli, 'db')

\\
"""
from __future__ import absolute_import
import click
from flask_alembic.cli import base


@click.group()
def cli():
    """Perform database migrations."""
    pass


@cli.command()
def mkdir():
    """Make migration directory."""
    base.mkdir()


@cli.command()
@click.option('-v', '--verbose', is_flag=True)
def current(verbose):
    """Show current revision."""
    base.current(verbose)


@cli.command()
@click.argument('revision', default='head')
def stamp(revision):
    """Set current revision."""
    base.stamp(revision)


@cli.command()
@click.option('--start', default='base', help='Show since this revision.')
@click.option('--end', default='head', help='Show until this revision.')
@click.option('-v', '--verbose', is_flag=True)
def log(start, end, verbose):
    """Show revision log."""
    base.log(start, end, verbose)


@cli.command()
def branches():
    """Show branches in upgrade path."""
    base.branches()


@cli.command()
@click.argument('target', default='head')
def upgrade(target):
    """Run upgrade migrations."""
    base.upgrade(target)


@cli.command()
@click.argument('target', default='-1')
def downgrade(target):
    """Run downgrade migrations."""
    base.downgrade(target)


@cli.command()
@click.argument('message')
@click.option('--empty', is_flag=True, help='Create empty script.')
def revision(message, empty):
    """Create new migration."""
    base.revision(message, empty)
