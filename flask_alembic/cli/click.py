"""Integration with Click::

    from flask_alembic.cli.click import cli as alembic_cli
    app.cli.add_command(alembic_cli, 'db')

\\
"""

from __future__ import absolute_import
import click
from flask.cli import AppGroup
from flask_alembic.cli import base


@click.command(cls=AppGroup)
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
@click.option('--resolve-dependencies', is_flag=True, help='Treat dependencies as down revisions.')
@click.option('-v', '--verbose', is_flag=True)
def heads(resolve_dependencies, verbose):
    """Show latest revisions."""

    base.heads(resolve_dependencies, verbose)


@cli.command()
@click.option('-v', '--verbose', count=True)
def branches(verbose):
    """Show branch points."""

    base.branches(verbose)


@cli.command()
@click.option('--start', default='base', help='Show since this revision.')
@click.option('--end', default='heads', help='Show until this revision.')
@click.option('-v', '--verbose', is_flag=True)
def log(start, end, verbose):
    """Show revision log."""

    base.log(start, end, verbose)


@cli.command()
@click.argument('revisions', nargs=-1)
def show(revisions):
    """Show the given revisions."""

    base.show(revisions)


@cli.command()
@click.argument('revision', default='heads')
def stamp(revision):
    """Set current revision."""

    base.stamp(revision)


@cli.command()
@click.argument('target', default='heads')
def upgrade(target):
    """Run upgrade migrations."""

    base.upgrade(target)


@cli.command()
@click.argument('target', default='1')
def downgrade(target):
    """Run downgrade migrations."""

    base.downgrade(target)


@cli.command()
@click.argument('message')
@click.option('--empty', is_flag=True, help='Create empty script.')
@click.option('--head', help='Base off this revision.')
@click.option('--splice', is_flag=True, help='Allow non-head base revision.')
@click.option('-l', '--branch-label', multiple=True, help='Apply a label to the revision.  Can be specified multiple times.')
@click.option('--version-path', help='Where to store the revision.')
def revision(message, empty, head, splice, branch_label, version_path):
    """Create new migration."""

    base.revision(message, empty, head, splice, branch_label, version_path)


@cli.command()
@click.argument('revisions', nargs=-1)
@click.option('-m', '--message')
@click.option('-l', '--branch-label', multiple=True, help='Apply a label to the revision.  Can be specified multiple times.')
@click.option('--version-path', help='Where to store the revision.')
def merge(revisions, message, branch_label):
    """Create merge revision."""

    base.merge(revisions, message, branch_label)
