# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import pathlib
import tomllib

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'game280'
author = 'Roman Weiss'

release = tomllib.load(open(pathlib.Path(__file__).parent.parent / 'pyproject.toml', 'rb'))['project']['version']
version = '.'.join(release.split('.')[:2])

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.apidoc', 'sphinx.ext.napoleon']

apidoc_modules = [
	{'path': '../src/game280', 'destination': 'api/', 'exclude_patterns': ['**/examples/**']}
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_permalinks_icon = '§'
html_show_copyright = False
html_theme = 'sphinx_rtd_theme'
