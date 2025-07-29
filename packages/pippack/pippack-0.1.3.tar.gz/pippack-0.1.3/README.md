# pippack

A simple command-line tool to help you manage your Python packages with pip.

## Features
- List top-level installed packages (excluding dependencies, pip, pippack, setuptools)
- List all installed packages (including dependencies)
- Show outdated packages
- Export requirements (filtered or all)
- Show details for a specific package

## Command Usage

### List top-level installed packages (excluding dependencies, pip, pippack, setuptools)
```
pippack
```

### List all installed packages (including dependencies)
```
pippack all
```

### Show outdated packages
```
pippack outdated
```

### Export top-level packages (excluding dependencies, pip, pippack, setuptools) to requirements.txt
```
pippack export
```

### Export all installed packages to requirements.txt
```
pippack export-all
```

### Show details for a specific package
```
pippack show <pkg>
```

## Cross-platform
Works on Windows, macOS, and Linux.

