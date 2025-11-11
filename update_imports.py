#!/usr/bin/env python3
"""Update all imports from toolkit to unistax."""

import os
import re
from pathlib import Path

def update_imports_in_file(file_path):
    """Update imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Replace various import patterns
        patterns = [
            (r'from toolkit\.', 'from unistax.'),
            (r'import toolkit\.', 'import unistax.'),
            (r'from toolkit import', 'from unistax import'),
            (r'import toolkit', 'import unistax'),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Update imports in all Python files."""
    root_dir = Path(__file__).parent
    count = 0

    # Directories to search
    search_dirs = [
        root_dir / 'python' / 'src' / 'unistax',
        root_dir / 'examples' / 'backends',
    ]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue

        print(f"Searching in {search_dir}...")
        for py_file in search_dir.rglob('*.py'):
            if update_imports_in_file(py_file):
                print(f"  Updated: {py_file.relative_to(root_dir)}")
                count += 1

    print(f"\nTotal files updated: {count}")

if __name__ == '__main__':
    main()
