import importlib.metadata

# Project --------------------------------------------------------------

project = "Flask-Alembic"
version = release = importlib.metadata.version(project).partition(".dev")[0]

# General --------------------------------------------------------------

default_role = "code"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "myst_parser",
    "sphinxcontrib.log_cabinet",
]
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_preserve_defaults = True
extlinks = {
    "issue": ("https://github.com/pallets-eco/flask-alembic/issues/%s", "#%s"),
    "pr": ("https://github.com/pallets-eco/flask-alembic/pull/%s", "#%s"),
}
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "alembic": ("https://alembic.sqlalchemy.org/en/latest/", None),
}
myst_enable_extensions = [
    "fieldlist",
]
myst_heading_anchors = 2

# HTML -----------------------------------------------------------------

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["theme.css"]
html_copy_source = False
html_theme_options = {
    "source_repository": "https://github.com/pallets-eco/flask-alembic/",
    "source_branch": "main",
    "source_directory": "docs/",
    "light_css_variables": {
        "font-stack": "'Atkinson Hyperlegible', sans-serif",
        "font-stack--monospace": "'Source Code Pro', monospace",
    },
}
pygments_style = "default"
pygments_style_dark = "github-dark"
html_show_copyright = False
html_use_index = False
html_domain_indices = False
