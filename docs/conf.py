from pallets_sphinx_themes import get_version
from pallets_sphinx_themes import ProjectLink

# Project --------------------------------------------------------------

project = "Flask-Alembic"
copyright = "2015 David Lord"
author = "David Lord"
release, version = get_version("Flask-Alembic")

# General --------------------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "pallets_sphinx_themes",
    "sphinxcontrib.log_cabinet",
    "sphinx_issues",
]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "alembic": ("https://alembic.sqlalchemy.org/en/latest/", None),
    "flask_script": ("https://flask-script.readthedocs.io/en/latest/", None),
}
issues_github_path = "davidism/flask-alembic"

# HTML -----------------------------------------------------------------

html_theme = "flask"
html_context = {
    "project_links": [
        ProjectLink("Donate to Flask", "https://www.palletsprojects.com/donate"),
        ProjectLink("PyPI Releases", "https://pypi.org/project/Flask-Alembic/"),
        ProjectLink("Source Code", "https://github.com/davidism/flask-alembic"),
        ProjectLink(
            "Issue Tracker", "https://github.com/davidism/flask-alembic/issues/"
        ),
    ]
}
html_sidebars = {
    "index": ["project.html", "localtoc.html", "searchbox.html"],
    "**": ["localtoc.html", "relations.html", "searchbox.html"],
}
singlehtml_sidebars = {"index": ["project.html", "localtoc.html"]}
html_title = f"{project} Documentation ({version})"
html_show_sourcelink = False
