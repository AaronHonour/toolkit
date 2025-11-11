#!/usr/bin/env python3
"""Update frontend imports from @frontend-toolkit to @unistax."""

import re
from pathlib import Path

def update_imports_in_file(file_path):
    """Update imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content

        # Replace imports
        patterns = [
            (r'@frontend-toolkit/atoms', '@unistax/atoms'),
            (r'@frontend-toolkit/performance', '@unistax/performance'),
            (r'@frontend-toolkit/design-tokens', '@unistax/design-tokens'),
            (r'@frontend-toolkit/layouts', '@unistax/layouts'),
        ]

        for old_pattern, new_pattern in patterns:
            content = content.replace(old_pattern, new_pattern)

        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Update all TypeScript/JavaScript files in frontends."""
    root_dir = Path(__file__).parent
    count = 0

    # Search in both examples/frontends and frontend/packages
    search_dirs = [
        root_dir / 'examples' / 'frontends',
        root_dir / 'frontend' / 'packages',
    ]

    for search_dir in search_dirs:
        if not search_dir.exists():
            print(f"Directory not found: {search_dir}")
            continue

        print(f"Searching in {search_dir}...")

        # Find all .ts, .tsx, .js, .jsx files
        for ext in ['**/*.ts', '**/*.tsx', '**/*.js', '**/*.jsx']:
            for file_path in search_dir.glob(ext):
                # Skip node_modules
                if 'node_modules' in str(file_path):
                    continue

                if update_imports_in_file(file_path):
                    print(f"  Updated: {file_path.relative_to(root_dir)}")
                    count += 1

    print(f"\nTotal files updated: {count}")

if __name__ == '__main__':
    main()
