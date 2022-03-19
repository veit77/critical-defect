# Distribute the project as package 
## Build Package
Befor building the package, update the `setup.py` in the root directory with the new version number and author information.

    python -m build

This command must be called from the directory containing the `setup.py` file.
# Installing and Deinstalling the Package
## Installation
    pip install quality_assessment.tar.gz

Here, it is assumed that the file `quality_assessment.tar.gz` is in the same directory from which pip is called.

## Editable Installation from Source
    pip install -e .

Here, it is assumed that `pip` is called from the root directory of the source tree.

## Deinstallieren
    pip uninstall quality-assessment

# Documentation
To automatically generate a documentation of the source code, the Sphinx package is used. To make sure the following works, please install Sphinx by calling:

    pip install Sphinx
## Building the Documentation
From the `docs` directory containing `Makefile` and `make.bat`, call:

    make html

to automatically make a html based documentation from the doc strings in the source code. Or call: holds List

    make latexpdf

to make a PDF.

## Class Diagram
A class diagram is provided in this project via the Mermaid markdown extension in the `mermaid`directory. To view a preview of the diagram in the preview window of VS Code, install a Mermaid preview extension like [Markdown Preview Mermaid Support](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid).