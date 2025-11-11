#!/usr/bin/env python3
"""Update frontend package names from @frontend-toolkit to @unistax."""

import json
from pathlib import Path

def update_package_json(file_path):
    """Update a single package.json file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        modified = False

        # Update name
        if 'name' in data and '@frontend-toolkit/' in data['name']:
            data['name'] = data['name'].replace('@frontend-toolkit/', '@unistax/')
            modified = True

        # Update dependencies
        for dep_type in ['dependencies', 'devDependencies', 'peerDependencies']:
            if dep_type in data:
                for key in list(data[dep_type].keys()):
                    if '@frontend-toolkit/' in key:
                        value = data[dep_type][key]
                        new_key = key.replace('@frontend-toolkit/', '@unistax/')
                        del data[dep_type][key]
                        data[dep_type][new_key] = value
                        modified = True

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                f.write('\n')
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Update all package.json files."""
    root_dir = Path(__file__).parent
    count = 0

    # Search in examples/frontends and frontend/packages
    search_dirs = [
        root_dir / 'examples' / 'frontends',
        root_dir / 'frontend' / 'packages',
    ]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue

        print(f"Searching in {search_dir}...")
        for pkg_file in search_dir.rglob('package.json'):
            if update_package_json(pkg_file):
                print(f"  Updated: {pkg_file.relative_to(root_dir)}")
                count += 1

    print(f"\nTotal files updated: {count}")

if __name__ == '__main__':
    main()
