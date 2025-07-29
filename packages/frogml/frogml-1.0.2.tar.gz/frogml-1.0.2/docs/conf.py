# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "FrogML"
copyright = "2024, Jfrog"
author = "JFrog"
release = "0.0.2"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "python"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
html_logo = "_static/jfrogml_logo.png"

import os
import sys

sys.path.insert(0, os.path.abspath("../"))
# Alabaster theme options

html_theme_options = {
    "description": "FrogML is a Python library designed to manage ML models within JFrog Artifactory.",
    "github_user": "yourusername",
    "github_repo": "FrogML",
    "fixed_sidebar": True,
    "show_related": False,
    "nav_title": "FrogML",
}
