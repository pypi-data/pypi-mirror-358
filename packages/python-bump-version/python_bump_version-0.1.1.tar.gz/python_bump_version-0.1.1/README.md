# Bump Version

[English | [中文说明](./README.zh-CN.md)]

A simple and easy-to-use Python version management tool, similar to npm version.

## Features

- 🚀 **Easy to use** - CLI interface similar to npm version
- 📦 **Multi-file support** - Supports `__init__.py`, `version.py`, `setup.py`, `pyproject.toml`
- 🏷️ **Semantic versioning** - Full semver support
- 🔄 **Pre-release support** - Supports alpha, beta, rc, etc.
- 🐙 **Git integration** - Auto commit, tag, and push
- 🔧 **Flexible config** - Custom version file and commit message

## Installation

```bash
pip install python-bump-version
```

## Quick Start

### Basic Usage

```bash
# Bump patch version (1.0.0 -> 1.0.1)
bump patch

# Bump minor version (1.0.0 -> 1.1.0)
bump minor

# Bump major version (1.0.0 -> 2.0.0)
bump major
```

### Pre-release Versions

```bash
# Create prepatch version (1.0.0 -> 1.0.1-0)
bump prepatch

# Create preminor version (1.0.0 -> 1.1.0-0)
bump preminor

# Create premajor version (1.0.0 -> 2.0.0-0)
bump premajor

# Increment prerelease (1.0.1-0 -> 1.0.1-1)
bump prerelease
```

### Git Integration

```bash
# Auto push to remote
bump patch --push

# Custom commit message
bump minor --message "feat: add new feature"

# Dry run (preview only)
bump major --dry-run
```

### Custom Version File

```bash
# Use custom version file
bump patch --file custom_version.py

# Use pyproject.toml
bump minor --file pyproject.toml
```

## Version Types

| Command      | Description         | Example           |
|-------------|--------------------|-------------------|
| `patch`     | Patch version      | 1.0.0 → 1.0.1     |
| `minor`     | Minor version      | 1.0.0 → 1.1.0     |
| `major`     | Major version      | 1.0.0 → 2.0.0     |
| `prepatch`  | Prepatch version   | 1.0.0 → 1.0.1-0   |
| `preminor`  | Preminor version   | 1.0.0 → 1.1.0-0   |
| `premajor`  | Premajor version   | 1.0.0 → 2.0.0-0   |
| `prerelease`| Prerelease bump    | 1.0.1-0 → 1.0.1-1 |

## Supported File Formats

### Python Files

```python
# __init__.py or version.py
__version__ = "1.0.0"

# setup.py
version = "1.0.0"
```

### pyproject.toml

```toml
[project]
version = "1.0.0"

[tool.bump-version]
version = "1.0.0"
```

## Library Usage

```python
from version_manager import VersionManager

# Basic usage
vm = VersionManager()
new_version = vm.bump('patch')
print(f"New version: {new_version}")

# Custom version file
vm = VersionManager('custom_version.py')
vm.bump('minor')

# Validate version
is_valid = vm.validate('1.0.0')  # True
is_valid = vm.validate('invalid')  # False
```

## CLI Options

```bash
usage: bump [-h] [--file FILE] [--push] [--message MESSAGE] \
            [--dry-run] [--verbose] \
            {patch,minor,major,prepatch,preminor,premajor,prerelease}

Bump Version - A simple and easy-to-use version management tool

positional arguments:
  {patch,minor,major,prepatch,preminor,premajor,prerelease}
                        Version type

optional arguments:
  -h, --help            Show this help message and exit
  --file FILE, -f FILE  Version file path (auto-detect by default)
  --push, -p            Auto push to remote
  --message MESSAGE, -m MESSAGE
                        Custom commit message
  --dry-run             Show what would be done, but don't actually do it
  --verbose, -v         Show verbose output
```

## Development

### Install Dev Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black src tests
isort src tests
```

### Type Checking

```bash
mypy src
```

## Contributing

Pull requests and issues are welcome!

## License

MIT License

## Related Projects

- [npm version](https://docs.npmjs.com/cli/v8/commands/npm-version) - Node.js version management
- [semver](https://semver.org/) - Semantic Versioning 