# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import pyqbf

project = 'PyQBF'
copyright = '2024-2025, Mark Peyrer, Maximilian Heisinger, Martina Seidl'
author = 'Mark Peyrer, Maximilian Heisinger, Martina Seidl'
version = u''
release = pyqbf.__version__
docpage = 'https://qbf.pages.sai.jku.at/pyqbf/index.html'
citation = "https://qbf.pages.sai.jku.at/pyqbf/manual/citing.html"
html_context = {
    'release': release,
    'docpage': docpage,
    'citation': citation
}


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [    
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.mathjax']

templates_path = ['_templates']
source_suffix = ".rst"
master_doc = "index"
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

pygments_style = "sphinx"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"  #same as pysat

html_theme_options = {
    "github_url": "https://gitlab.sai.jku.at/qbf/pyqbf",
    "show_nav_level": 2,
    "navbar_start": ["logo"],
    "navbar_center": ["version"],
    "navbar_end": ["navbar-icon-links"],
    "footer_center": ["citation"]
}

html_sidebars = {
    "**": []
}

# Autodoc settings
autodoc_default_flags = ['members', 'special-members']

html_static_path = ['_static']
html_css_files = ['css/custom.css']

