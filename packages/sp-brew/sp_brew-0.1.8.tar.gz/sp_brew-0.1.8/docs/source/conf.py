"""Configure Sphinx for the sp_brew project documentation."""
import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
]

html_theme = "furo"
project = "sp_brew"
copyright = "2025, Damiano Massella"
author = "Damiano Massella"
release = "0.1.0"

templates_path = ["_templates"]
exclude_patterns = []
html_static_path = ["_static"]
