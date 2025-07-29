import yaml
from pathlib import Path

# Default patterns to ignore
DEFAULT_IGNORE_PATTERNS = {
    # Version control
    '.git', '.gitignore', '.gitkeep', '.gitmodules', '.gitattributes',
    '.hg', '.hgignore', '.hgtags',
    '.svn',
    
    # Python
    '__pycache__', '*.pyc', '*.pyo', '*.pyd', '.Python',
    'build', 'develop-eggs', 'dist', 'downloads', 'eggs', '.eggs',
    'lib', 'lib64', 'parts', 'sdist', 'var', 'wheels',
    '*.egg-info', '.installed.cfg', '*.egg',
    '.pytest_cache', '.coverage', '.tox', '.cache',
    '.mypy_cache', '.dmypy.json', 'dmypy.json',
    
    # Node.js
    'node_modules', 'npm-debug.log*', 'yarn-debug.log*', 'yarn-error.log*',
    '.npm', '.yarn-integrity',
    
    # IDEs and editors
    '.vscode', '.idea', '*.swp', '*.swo', '*~', '.DS_Store',
    'Thumbs.db', '.sublime-project', '.sublime-workspace',
    
    # OS
    '.DS_Store', '.DS_Store?', '._*', '.Spotlight-V100', '.Trashes',
    'ehthumbs.db', 'Thumbs.db',
    
    # Logs and temporary files
    '*.log', 'logs', 'temp', 'tmp', '.tmp',
    
    # Environment files
    '.env', '.env.local', '.env.*.local',
    
    # Package managers
    '.uv', '.venv', 'venv', 'env', 'ENV',
}

def should_ignore(path, ignore_patterns=None):
    """Check if a path should be ignored based on patterns"""
    if ignore_patterns is None:
        ignore_patterns = DEFAULT_IGNORE_PATTERNS
    
    name = path.name
    
    # Check exact matches
    if name in ignore_patterns:
        return True
    
    # Check wildcard patterns
    for pattern in ignore_patterns:
        if '*' in pattern:
            # Simple wildcard matching (*.ext)
            if pattern.startswith('*') and name.endswith(pattern[1:]):
                return True
            if pattern.endswith('*') and name.startswith(pattern[:-1]):
                return True
    
    return False

# Custom YAML representer for multiline strings
def multiline_string_representer(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

# Register the custom representer
yaml.add_representer(str, multiline_string_representer)

def create_from_yaml(yaml_file, target_dir="."):
    """Create folder/file structure from YAML"""
    with open(yaml_file, 'r') as f:
        structure = yaml.safe_load(f)
    
    _create_structure(structure, Path(target_dir))

def _create_structure(structure, base_path):
    """Recursively create structure"""
    for name, content in structure.items():
        path = base_path / name
        
        if isinstance(content, dict):
            # It's a directory
            path.mkdir(parents=True, exist_ok=True)
            _create_structure(content, path)
        else:
            # It's a file - write content (or empty if None/empty string)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content or "")

def create_yaml_from_structure(source_dir, output_yaml, ignore_patterns=None):
    """Generate YAML blueprint from existing directory structure"""
    structure = _scan_structure(Path(source_dir), ignore_patterns)
    
    with open(output_yaml, 'w') as f:
        yaml.dump(structure, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

def _scan_structure(path, ignore_patterns=None):
    """Recursively scan directory structure"""
    if not path.exists():
        raise FileNotFoundError(f"Path {path} does not exist")
    
    if path.is_file():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Handle binary files
            return f"<binary file: {path.name}>"
    
    result = {}
    
    # Get all items and sort them (directories first, then files)
    items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
    
    for item in items:
        # Skip ignored files/directories - but only if we have ignore patterns
        if ignore_patterns is not None and should_ignore(item, ignore_patterns):
            continue
            
        if item.is_dir():
            sub_structure = _scan_structure(item, ignore_patterns)
            # Only include directory if it has content after filtering
            if sub_structure:
                result[item.name] = sub_structure
        else:
            try:
                with open(item, 'r', encoding='utf-8') as f:
                    result[item.name] = f.read()
            except UnicodeDecodeError:
                # Handle binary files
                result[item.name] = f"<binary file: {item.name}>"
    
    return result

