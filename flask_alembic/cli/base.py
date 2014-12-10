"""Base functions that write information to the terminal."""

from flask import current_app


def get_alembic():
    """Get the alembic extension for the current app."""

    return current_app.extensions['alembic']


def mkdir():
    """Create the migration directory if it does not exist."""

    get_alembic().mkdir()


def current(verbose=False):
    """Show the list of current revisions."""

    a = get_alembic()
    print_stdout = a.config.print_stdout

    for r in a.current():
        print_stdout(r.cmd_format(verbose) if r is not None else None)


def heads(resolve_dependencies=False, verbose=False):
    """Show the list of revisions that have no child revisions."""

    a = get_alembic()
    print_stdout = a.config.print_stdout

    for r in a.heads(resolve_dependencies):
        print_stdout(r.cmd_format(verbose, include_branches=True, tree_indicators=False))


def branches(verbose=0):
    """Show the list of revisions that have more than one next revision."""

    a = get_alembic()
    print_stdout = a.config.print_stdout
    get_revision = a.script.get_revision

    for r in a.branches():
        print_stdout(r.cmd_format(verbose > 0, include_branches=True))

        if verbose > 1:
            for nr in r.nextrev:
                print_stdout('    -> {0}'.format(
                    get_revision(nr).cmd_format(False, include_branches=True, include_doc=verbose > 2)
                ))


def log(start='base', end='heads', verbose=False):
    """Show the list of revisions in the order they will run."""

    a = get_alembic()
    print_stdout = a.config.print_stdout

    for r in a.log(start, end):
        print_stdout(r.cmd_format(verbose, include_branches=True, include_doc=True, include_parents=True))


def show(revisions):
    """Show the given revisions."""

    a = get_alembic()
    print_stdout = a.config.print_stdout

    if revisions == ('current',):
        current(verbose=True)
    else:
        for r in a.script.get_revisions(revisions):
            print_stdout(r.log_entry)


def stamp(revision='heads'):
    """Set the current revision without running migrations."""

    get_alembic().stamp(revision)


def upgrade(target='heads'):
    """Run migrations to upgrade the database."""

    get_alembic().upgrade(target)


def downgrade(target=-1):
    """Run migration to downgrade the database."""

    get_alembic().downgrade(target)


def revision(message, empty=False, head=None, splice=False, branch_labels=None, version_path=None):
    """Generate a new revision."""

    get_alembic().revision(message, empty, head, splice, branch_labels, version_path)


def merge(revisions, message=None, branch_labels=None):
    """Generate a merge revision."""

    get_alembic().merge(revisions, message, branch_labels)
