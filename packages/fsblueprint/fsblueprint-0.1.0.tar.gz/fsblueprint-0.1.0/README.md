# FSBlueprint

**FSBlueprint** is a Python tool for bidirectional conversion between YAML blueprints and directory structures. Effortlessly scaffold complex projects from a single YAML file, or generate a reproducible YAML blueprint from any existing folder tree—including file contents.

## Features

- Scaffold entire directory trees (with files and contents) from YAML
- Generate a YAML blueprint from any existing directory structure
- Supports nested folders, empty files, and multi-line file contents
- Simple CLI and Python API

## Installation

Install from PyPI:

```bash
pip install fsblueprint
```

## Usage

### Create a directory structure from YAML

```bash
fsblueprint scaffold project.yaml ./my_project
```

### Generate a YAML blueprint from an existing directory

```bash
fsblueprint blueprint ./existing_project blueprint.yaml
```

Or use the Python API:

```python
from fsblueprint.core import create_from_yaml, create_yaml_from_structure

# Create structure from YAML
create_from_yaml('project.yaml', 'my_project')

# Generate YAML from directory
create_yaml_from_structure('existing_project', 'blueprint.yaml')
```

## Example YAML

```yaml
my_project:
  README.md: |
    # My Project
    Hello world!
  src:
    main.py: |
      def main():
          print("Hello!")
    utils:
      helper.py: ""
  tests:
    test_main.py: ""
```

## License

MIT
