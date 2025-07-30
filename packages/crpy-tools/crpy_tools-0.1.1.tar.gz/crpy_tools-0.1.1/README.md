# crpy - Comment Removal for Python

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

crpy is a powerful tool for removing comments from Python files while preserving code structure and indentation. It offers both command-line interface (CLI) and graphical user interface (GUI) options for maximum flexibility.

## Features

- 🚀 Remove all types of Python comments (#-style)
- 📝 Optionally remove docstrings
- 📁 Process single files or entire directories
- 🔁 Recursive directory processing
- 🎨 Clean code formatting with preserved indentation
- 💻 CLI for scripting and automation
- 🖥️ GUI for easy interactive use
- 📊 Progress reporting and logging

## Installation

### Requirements
- Python 3.7+
- PySide6 (for GUI)

### Install from PyPI
```bash
pip install crpy-tools
```
### Example usage
```bash
# show help
crpy -h

# remove all comments from script.py
crpy script.py -o script_min.py -d
```