from fsblueprint.core import create_from_yaml, create_yaml_from_structure

print("=== Creating structure with content ===")
create_from_yaml('./examples/test_with_content.yaml', './content_test')
print("Done! Check ./content_test folder and file contents")

print("\n=== Generating YAML from structure ===")
create_yaml_from_structure('./content_test', './reverse_content.yaml')
print("Generated ./reverse_content.yaml")

print("\n=== Content of main.py ===")
with open('./content_test/my_app/src/main.py', 'r') as f:
    print(f.read())