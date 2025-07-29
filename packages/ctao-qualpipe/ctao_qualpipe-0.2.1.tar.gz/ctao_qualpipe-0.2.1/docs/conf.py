"""
Configuration file for the Sphinx documentation builder.

This file only contains a selection of the most common options. For a full
list see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

# -- Project information -----------------------------------------------------
# import your own package here
import qualpipe

project = "qualpipe"
copyright = "2023, UniGE-UniBern-CTAO DPPS QualPipe Group"
author = "UniGE-UniBern-CTAO DPPS QualPipe Group"
version = qualpipe.__version__
# The full version, including alpha/beta/rc tags.
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "numpydoc",
    "sphinx_changelog",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
    "sphinx.ext.mathjax",
    "sphinx_paramlinks",
    "myst_parser",
    "sphinxarg.ext",
    "nbsphinx",
]

myst_enable_extensions = [
    "linkify",
]

myst_heading_anchors = 3

# Default options for autodoc directives
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# intersphinx allows referencing other packages sphinx docs
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "astropy": ("https://docs.astropy.org/en/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "ctapipe": ("https://ctapipe.readthedocs.io/en/stable/", None),
}

nitpick_ignore = [
    ("py:class", "StrDict"),
    ("py:class", "ClassesType"),
    ("py:obj", "parent=self"),
]

# autosectionlabel_prefix_document = True

# Generate todo blocks
todo_include_todos = True

# Add any paths that contain templates here, relative to this directory.
templates_path = []

# The suffix of source filenames.
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# The master toctree document.
master_doc = "index"

# Ignore example notebook errors
nbsphinx_allow_errors = True
nbsphinx__timeout = 200  # allow max 2 minutes to build each notebook

numpydoc_show_class_members = False

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["changes"]

# have all links automatically associated with the right domain.
default_role = "py:obj"


# -- Options for HTML output -------------------------------------------------

html_theme = "ctao"
html_theme_options = dict(
    navigation_with_keys=False,
    logo=dict(text="QualPipe"),
    # setup for displaying multiple versions, also see setup in .gitlab-ci.yml
    switcher=dict(
        json_url="http://cta-computing.gitlab-pages.cta-observatory.org/dpps/qualpipe/qualpipe/versions.json",  # noqa: E501
        version_match="latest" if ".dev" in version else f"v{version}",
    ),
    navbar_center=["version-switcher", "navbar-nav"],
)

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]
