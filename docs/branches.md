# Independent Named Branches

Alembic supports [named branches][], but its syntax is hard to remember and verbose.
Flask-Alembic makes it easier by providing a central configuration for branch names and
revision directories and simplifying the syntax to the `revision` command.

[named branches]: https://alembic.sqlalchemy.org/en/latest/branches.html#working-with-multiple-bases

Alembic allows configuration of multiple version locations. `version_locations` is a
list of directories to search for migration scripts. Flask-Alembic extends this to allow
tuples as well as strings in the list. Each tuple is a `(branch, directory)` pair. The
`script_location` is automatically given the label `default` and added to the
`version_locations`.

```python
ALEMBIC = {
    "version_locations": [
        # not a branch, just another search location
        "other_migrations",
        # posts branch migrations will be placed here
        ("posts", "/path/to/posts_extension/migrations"),
        # relative paths are relative to the application root
        ("users", "users/migrations"),
    ],
}
```

The `revision` command takes a `--branch` option (defaults to `default`). This
takes the place of specifying `--parent`, `--label`, and `--path`. This will
automatically start the branch from the base revision, label the revision correctly, and
place the revisions in the correct location.

```text
$ flask db revision --branch users "create user model"

# equivalent to (if branch is new)
$ alembic revision --autogenerate --head base --branch-label users --version-path users/migrations -m "create user model"

# or (if branch exists)
$ alembic revision --autogenerate --head users@head -m "create user model"
```
