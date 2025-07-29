import argparse
import sys
from pathlib import Path
from .core import create_from_yaml, create_yaml_from_structure

def main():
    parser = argparse.ArgumentParser(
        description="FSBlueprint - YAML ↔ Directory Structure Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fsblueprint scaffold project.yaml ./my_app     # Create structure from YAML
  fsblueprint blueprint ./existing_app out.yaml # Generate YAML from structure
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
                
            create_yaml_from_structure(args.source_dir, args.yaml_file)
            print(f"✅ Blueprint saved to '{args.yaml_file}'")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()