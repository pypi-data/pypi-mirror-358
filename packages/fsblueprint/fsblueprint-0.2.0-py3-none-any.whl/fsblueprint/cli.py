import argparse
import sys
from pathlib import Path
from .core import create_from_yaml, create_yaml_from_structure, DEFAULT_IGNORE_PATTERNS

def main():
    parser = argparse.ArgumentParser(
        description="FSBlueprint - YAML ↔ Directory Structure Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fsblueprint scaffold project.yaml ./my_app     # Create structure from YAML
  fsblueprint blueprint ./existing_app out.yaml # Generate YAML from structure
  fsblueprint blueprint ./my_app out.yaml --no-ignore  # Include all files
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scaffold command (YAML -> Structure)
    scaffold_parser = subparsers.add_parser('scaffold', help='Create directory structure from YAML')
    scaffold_parser.add_argument('yaml_file', help='Input YAML file')
    scaffold_parser.add_argument('target_dir', help='Target directory to create structure')
    
    # Blueprint command (Structure -> YAML)  
    blueprint_parser = subparsers.add_parser('blueprint', help='Generate YAML from directory structure')
    blueprint_parser.add_argument('source_dir', help='Source directory to scan')
    blueprint_parser.add_argument('yaml_file', help='Output YAML file')
    blueprint_parser.add_argument('--no-ignore', action='store_true', 
                                help='Include all files (disable default ignore patterns)')
    blueprint_parser.add_argument('--ignore', nargs='+', 
                                help='Additional patterns to ignore')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'scaffold':
            if not Path(args.yaml_file).exists():
                print(f"Error: YAML file '{args.yaml_file}' not found")
                sys.exit(1)
            
            create_from_yaml(args.yaml_file, args.target_dir)
            print(f"✅ Structure created at '{args.target_dir}'")
            
        elif args.command == 'blueprint':
            if not Path(args.source_dir).exists():
                print(f"Error: Directory '{args.source_dir}' not found")
                sys.exit(1)
            
            # Handle ignore patterns
            ignore_patterns = None if args.no_ignore else DEFAULT_IGNORE_PATTERNS.copy()
            
            if args.ignore and ignore_patterns is not None:
                ignore_patterns.update(args.ignore)
            elif args.ignore and ignore_patterns is None:
                ignore_patterns = set(args.ignore)
                
            create_yaml_from_structure(args.source_dir, args.yaml_file, ignore_patterns)
            print(f"✅ Blueprint saved to '{args.yaml_file}'")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()