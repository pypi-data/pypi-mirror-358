# pippack

A simple command-line tool to help you manage your Python packages with pip.

## Features
- List top-level installed packages (excluding dependencies, pip, pippack, setuptools)
- List all installed packages (including dependencies)
- Show outdated packages
- Export requirements (filtered or all)
- Show details for a specific package

## Usage

```
pippack                # Show top-level installed packages (excluding dependencies, pip, pippack, setuptools)
pippack all            # Show all installed packages (including dependencies)
pippack outdated       # Show outdated packages
pippack export         # Export top-level packages (excluding dependencies, pip, pippack, setuptools) to requirements.txt
pippack export-all     # Export all installed packages to requirements.txt
pippack show <pkg>     # Show details for a specific package
```

## Cross-platform
Works on Windows, macOS, and Linux.

## Installation

After publishing to PyPI:
```
pip install pippack
```

## License
MIT
