# Configuration file for the Sphinx documentation builder.

import os
import sys
from datetime import datetime
from typing import Any, Dict

# Import sphinx_rtd_theme only once
import sphinx_rtd_theme  # noqa: F401

from prs_commons import __version__

# Add the project root to the Python path
project_root = os.path.abspath("../../")
sys.path.insert(0, project_root)

# Add the src directory to the Python path
src_path = os.path.join(project_root, "src")
sys.path.insert(0, src_path)

# Get version from package


# -- Project information -----------------------------------------------------
project = "PRS Commons"
# Using html_last_updated_fmt instead of copyright to avoid shadowing built-in
html_last_updated_fmt = datetime.now().strftime("%Y-%m-%d %H:%M")
author = "Isha Foundation IT"

# Set a dummy copyright to satisfy Sphinx
copyright = f"{datetime.now().year}, {author}"  # noqa: A001

# The full version, including alpha/beta/rc tags
release = __version__
version = ".".join(release.split(".")[:2])  # Major.Minor version

# Extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "myst_parser",
]

# Autosummary settings
autosummary_generate = True
autosummary_imported_members = True

# Theme options are theme-specific and customize the look and feel of a theme
# Theme settings
html_theme = "sphinx_rtd_theme"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# Add custom template paths
templates_path = ["_templates"]

# Ensure the template directory exists
if not os.path.exists("_templates"):
    os.makedirs("_templates")

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**/tests"]

# Theme options
try:
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
except ImportError:
    pass

# Theme options with type annotation
html_theme_options = {
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": True,
    "style_nav_header_background": "#2e8b57",  # Dark green
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 3,
    "includehidden": True,
    "titles_only": False,
}

# Enable Markdown support
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# The master toctree document.
master_doc = "index"

# Auto-generate API documentation
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# Intersphinx configuration
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "odoo": ("https://www.odoo.com/documentation/16.0/", None),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages
html_theme = "sphinx_rtd_theme"

# Remove duplicate theme options section

# Add any paths that contain custom static files (such as style sheets)
html_static_path = ["_static"]

# Custom CSS
html_css_files = [
    "css/custom.css",
]

# -- Options for Markdown support -------------------------------------------

# Enable MyST extensions
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_image",
]

# Enable numbering for figures with numref
numfig = True


# -- Options for autodoc ----------------------------------------------------
# Make sure __init__ methods are documented
def skip(
    _app: Any, _what: str, name: str, _obj: Any, would_skip: bool, _options: Any
) -> bool:
    """Skip members in autodoc, except for __init__ methods.

    Args:
        _app: Unused - The Sphinx application object
        _what: Unused - The type of the object which the docstring belongs to
        name: The full name of the object
        _obj: Unused - The object being documented
        would_skip: Whether the member would be skipped by default
        _options: Unused - The options given to the directive

    Returns:
        bool: Whether to skip the member
    """
    # Always show __init__ methods
    if name == "__init__":
        return False
    return would_skip


def setup(app: Any) -> Dict[str, bool]:
    """Set up Sphinx extension.

    Args:
        app: The Sphinx application object

    Returns:
        Dict[str, bool]: Extension metadata with boolean flags
    """
    app.connect("autodoc-skip-member", skip)
    app.add_css_file("css/custom.css")
    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
