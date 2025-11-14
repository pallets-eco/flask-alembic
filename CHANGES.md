## Version 3.2.0

Unreleased

-   Drop support for Python 3.9.
-   Remove previously deprecated code.
    -   `init_app` args `run_mkdir` and `command_name` are removed.
-   Add `path_separator` to config to suppress Alembic warning. {issue}`48`

## Version 3.1.1

Released 2024-08-29

- `flask db merge` merges all heads by default and does not require an argument.
  {issue}`40`

## Version 3.1.0

Released 2024-06-16

- Drop support for Python 3.8. {pr}`28`
- Support Flask-SQLAlchemy-Lite and plain SQLAlchemy, in addition to
  Flask-SQLAlchemy. {pr}`26`
- Support multiple databases, and multiple metadata per database. {pr}`26`
- The constructor args `run_mkdir` and `command_name` are keyword only. {pr}`27`
- Deprecate the `init_app` args `run_mkdir` and `command_name`. They can be
  passed to the constructor instead. {pr}`27`
- Dict values in the `ALEMBIC` config are treated as Alembic config sections,
  allowing use of Alembic features like `post_write_hooks`. {pr}`29`

## Version 3.0.1

Released 2024-02-22

- Fix handling of relative ids (`+1`, `-1`) passed to `downgrade` and `upgrade`.

## Version 3.0.0

Released 2024-02-08

- Minimum supported version of Python is 3.8. Drop support for Python 2.
- Minimum supported version of Flask is 3.0.
- Minimum supported version of SQLAlchemy is 2.0.
- Minimum supported version of Flask-SQLAlchemy is 3.1.
- Minimum supported version of Alembic is 1.13.
- Drop support for Flask-Script.
- Add type annotations.
- Adding the CLI is skipped if `command_name` is empty rather than `False`.
- The internal cache only holds a weak reference to the Flask app.
- Various arguments no longer use a default value when passed `None`.
- `compare_server_default` defaults to `True`. Alembic already defaults
  `compare_type` to `True`.
- `rev_id` defaults to the current UTC timestamp instead of a UUID.

## Version 2.0.1

Released 2016-08-31

- Fix `merge` command.

## Version 2.0.0

Released 2016-07-14

- Support Alembic 0.8.
- Automatically register Click group.
- Allow customizing revision id.
- Configure Alembic and SQLAlchemy loggers.
- Update Python 2 and 3 compatibility.
- Don't require Flask-Script.

## Version 1.2.1

Released 2015-08-26

- Support Flask-Click for Flask 0.10.

## Version 1.2.0

Released 2015-08-13

- Fix Python 2 compatibility.
- Commands output revision information consistently.
- Default branch gets "default" label.
- Restrict to Alembic < 0.8 until compatibility can be addressed.

## Version 1.1.0

Released 2014-12-15

- Add independent named branches feature.
- Commands default to working on all heads.

## Version 1.0.2

Released 2014-08-26

- Fix Flask app context for Click CLI.

## Version 1.0.1

Released 2014-08-26

- Python 3 compatibility.

## Version 1.0.0

Released 2014-06-16
