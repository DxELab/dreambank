# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import time
import sys
from importlib.metadata import metadata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1].joinpath("src")))
import dreambank


project = dreambank.__name__
version = dreambank.__version__[:3]
release = dreambank.__version__
author = metadata("dreambank").get("Author-email").split(" <")[0]
curryear = time.strftime("%Y")
copyright = f"2024-{curryear}, {author}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # "sphinx.ext.doctest",
    # "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",  # Core Sphinx library for auto html doc generation from docstrings
    "sphinx.ext.autosummary",  # Create neat summary tables for modules/classes/methods etc
    "sphinx.ext.intersphinx",  # Link to other project's documentation (see mapping below)
    "sphinx.ext.autosectionlabel",
    # "sphinx_autodoc_typehints",  # Automatically document param types (less noise in class signature)
    # "numpydoc",
    "sphinx_copybutton",  # Adds a copy button to code blocks (for pasting)
    "sphinx_design",  # more options for pydatasphinx theme, eg, dropdowns, tabs
    # "sphinx.ext.linkcode",
    # "jupyter_sphinx",
]

# sphinx.ext.autosectionlabel option
# Make sure the target is unique
autosectionlabel_prefix_document = True
# autosectionlabel_maxdepth = 1

source_suffix = ".rst"
source_encoding = "utf-8"
# master_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
# include_patterns = "**"
templates_path = ["_templates"]
rst_epilog = """
.. |dreambank| replace:: `dreambank`

.. role:: python(code)
   :language: python

"""


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_title = f"dreambank v{release}"  # defaults to "<project> v<revision> documentation"
html_short_title = "dreambank"
html_logo = None
html_favicon = None
html_css_files = []
html_static_path = ["_static"]
html_last_updated_fmt = ""  # empty string is equivalent to "%b %d, %Y"
html_permalinks = True
html_domain_indices = True
html_use_index = False
html_show_sourcelink = False
html_show_copyright = False
html_show_sphinx = False
html_output_encoding = "utf-8"
html_sidebars = {
    # "**": [],  # remove sidebar from all pages
    "usage": [],  # remove sidebar from usage page
    "contributing": [],  # remove sidebar from contributing page
}
html_additional_pages = {}
# :html_theme.sidebar_secondary.remove: true

# I think this is just for showing source?
html_context = {
    # "github_url": "https://github.com",
    "github_user": "DxELab",
    "github_repo": "dreambank",
    "github_version": "main",
    "doc_path": "docs",
    "default_mode": "auto",  # light, dark, auto
}


# Full list:
# https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/layout.html#references
html_theme_options = {
    "navigation_with_keys": False,
    "external_links": [
        {"name": "Releases", "url": "https://github.com/DxELab/dreambank/releases"},
    ],
    "header_links_before_dropdown": 4,
    "navbar_start": ["navbar-logo"],  # "version-switcher"
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["navbar-icon-links"],
    # "navbar_persistent": [],  # Default is a nice search bubble that I otherwise don't get
    "navbar_align": "left",  # left/content/right
    "search_bar_text": "Search...",
    # "article_header_start": ["breadcrumbs"],
    # "article_header_end": [],
    # "article_footer_items": [],
    "footer_start": ["last-updated"],  # "search-field" "search-button"
    "footer_center": [],
    "footer_end": [],  # "theme-switcher"
    "content_footer_items": [],
    "show_prev_next": False,
    # "sidebarwidth": 230,
    # "navbar_start": ["navbar-logo", "version-switcher"],
    "show_version_warning_banner": True,
    "announcement": "This project is being developed by the <a href='https://www.dreamengineeringlab.com'>Dream Engineering Lab</a> in collaboration with the <a href='https://sleepanddreamdatabase.org'>Sleep and Dream Database</a>.",
    "show_nav_level": 1,
    "show_toc_level": 1,  # How many to show (rest are still uncollapsible)
    "navigation_depth": 3,
    "collapse_navigation": False,
    # "secondary_sidebar_items": [],
    # "secondary_sidebar_items": {"**": []},
    "use_edit_page_button": True,
    # "use_repository_button": True,
    # "icon_links_label": "Quick Links",
    "icon_links": [
        {
            "name": "dreambank on GitHub",
            "url": "https://github.com/DxELab/dreambank",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        },
    ],
}

# configure sphinx-copybutton
# https://github.com/executablebooks/sphinx-copybutton
# copybutton_prompt_text = r">>> |\.\.\. |\$ "
# copybutton_prompt_is_regexp = True


# -- Options for autosummary/autodoc output ------------------------------------
# Generate the API documentation when building
autosummary_generate = True  # Turn on sphinx.ext.autosummary
# autodoc_typehints = "description"
# autodoc_member_order = "groupwise"
autodoc_default_options = {
    "members": True,
    "member-order": "groupwise",
    "undoc-members": False,
}


# -- Intersphinx ------------------------------------------------

intersphinx_mapping = {
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    "pooch": ("https://www.fatiando.org/pooch/latest", None),
    "python": ("https://docs.python.org/3", None),
}
