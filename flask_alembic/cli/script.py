from flask_script import Manager
from flask_alembic import command

manager = Manager(help='Perform database migrations.', description='Perform database migrations.')

manager.command(
    command.mkdir
)

manager.option('-v', '--verbose', action='store_true', help='Show more information.')(
    command.current
)

manager.option('revision', default='head', help='Identifier to set as current')(
    command.stamp
)

manager.option('-v', '--verbose', action='store_true', help='Show more information.')(
    manager.option('range', nargs='?', help='Format [start]:[end], accepts identifier, "base", "head", or "current".')(
        command.history
    )
)

manager.command(
    command.branches
)

manager.option('target', nargs='?', default='head', help='Identifier to upgrade to, or +N relative to current.')(
    command.upgrade
)

manager.option('target', nargs='?', default='head', help='Identifier to upgrade to, or +N relative to current.')(
    command.downgrade
)

manager.option('--empty', action='store_true', help='Do not auto-generate operations.')(
    manager.option('message', help='Description of changes in this revision.')(
        command.revision
    )
)
