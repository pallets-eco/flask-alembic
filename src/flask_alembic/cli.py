from __future__ import annotations

import typing as t

import click
from alembic.script import Script
from flask import current_app

if t.TYPE_CHECKING:
    from .extension import Alembic


@click.group("db")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Perform database migrations."""
    ctx.obj = current_app.extensions["alembic"]


@cli.command()
@click.pass_obj
def mkdir(alembic: Alembic) -> None:
    """Create the migration directory if it does not exist."""
    alembic.mkdir()


@cli.command()
@click.pass_obj
@click.option("-v", "--verbose", is_flag=True)
def current(alembic: Alembic, verbose: bool = False) -> None:
    """Show the list of current revisions."""
    for r in alembic.current():
        if r is None:
            click.echo("None")
        else:
            _echo_cmd(r, verbose)


@cli.command()
@click.pass_obj
@click.option(
    "--resolve-dependencies", is_flag=True, help="Treat dependencies as down revisions."
)
@click.option("-v", "--verbose", is_flag=True)
def heads(
    alembic: Alembic, resolve_dependencies: bool = False, verbose: bool = False
) -> None:
    """Show the list of revisions that have no child revisions."""
    for r in alembic.heads(resolve_dependencies):
        _echo_cmd(r, verbose)


@cli.command()
@click.pass_obj
@click.option("-v", "--verbose", is_flag=True)
def branches(alembic: Alembic, verbose: bool = False) -> None:
    """Show the list of revisions that have more than one next revision."""
    get_revision = alembic.script_directory.get_revision

    for r in alembic.branches():
        _echo_cmd(r, verbose)

        for nr_name in r.nextrev:
            nr = get_revision(nr_name)
            click.echo(f"    -> {_cmd_format(nr, False)}")


@cli.command()
@click.pass_obj
@click.option("--start", default="base", help="Show since this revision.")
@click.option("--end", default="heads", help="Show until this revision.")
@click.option("-v", "--verbose", is_flag=True)
def log(
    alembic: Alembic, start: str = "base", end: str = "heads", verbose: bool = False
) -> None:
    """Show the list of revisions in the order they will run."""
    for r in alembic.log(start, end):
        _echo_cmd(r, verbose)


@cli.command()
@click.pass_obj
@click.argument("revisions", nargs=-1)
def show(alembic: Alembic, revisions: list[str]) -> None:
    """Show the given revisions."""
    for r in alembic.script_directory.get_revisions(revisions):
        click.echo(r.cmd_format(True))


@cli.command()
@click.pass_obj
@click.argument("target", default="heads")
def stamp(alembic: Alembic, target: str = "heads") -> None:
    """Set the current revision without running migrations."""
    alembic.stamp(target)


@cli.command()
@click.pass_obj
@click.argument("target", default="heads")
def upgrade(alembic: Alembic, target: str = "heads") -> None:
    """Run migrations to upgrade the database."""
    alembic.upgrade(target)


@cli.command()
@click.pass_obj
@click.argument("target", default="-1")
def downgrade(alembic: Alembic, target: str = "-1") -> None:
    """Run migration to downgrade the database."""
    try:
        # If an integer was given, ensure it's negative, since it's hard to
        # give negative numbers as CLI args.
        target = str(-abs(int(target)))
    except ValueError:
        pass

    alembic.downgrade(target)


@cli.command()
@click.pass_obj
@click.argument("message")
@click.option("--empty", is_flag=True, help="Create empty script.")
@click.option(
    "-b", "--branch", default="default", help="Use this independent branch name."
)
@click.option(
    "-p",
    "--parent",
    multiple=True,
    default=["head"],
    help="Parent revision(s) of this revision.",
)
@click.option("--splice", is_flag=True, help="Allow non-head parent revision.")
@click.option(
    "-d", "--depend", multiple=True, help="Revision(s) this revision depends on."
)
@click.option("-l", "--label", multiple=True, help="Label(s) to apply to the revision.")
@click.option("--path", help="Where to store the revision.")
def revision(
    alembic: Alembic,
    message: str,
    empty: bool = False,
    branch: str = "default",
    parent: str = "head",
    splice: bool = False,
    depend: list[str] | None = None,
    label: list[str] | None = None,
    path: str | None = None,
) -> None:
    """Generate a new revision."""
    alembic.revision(message, empty, branch, parent, splice, depend, label, path)


@cli.command()
@click.pass_obj
@click.argument("revisions", nargs=-1)
@click.option("-m", "--message")
@click.option("-l", "--label", multiple=True, help="Label(s) to apply to the revision.")
def merge(
    alembic: Alembic,
    revisions: list[str],
    message: str | None = None,
    label: list[str] | None = None,
) -> None:
    """Generate a merge revision."""
    alembic.merge(revisions, message, label)


def _cmd_format(r: Script, verbose: bool) -> str:
    return r.cmd_format(
        verbose,
        include_branches=True,
        include_doc=True,
        include_parents=True,
        tree_indicators=True,
    )


def _echo_cmd(r: Script, verbose: bool) -> None:
    click.echo(_cmd_format(r, verbose))
