#!/usr/bin/env python3
"""Update all frontend apps to import pre-built CSS from @unistax/frontend instead of raw Tailwind."""

import re
from pathlib import Path

def update_main_tsx(file_path):
    """Update main.tsx to import pre-built CSS."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace index.css import with unistax styles
        old_import = "import './index.css';"
        new_import = "import '@unistax/frontend/styles.css';"

        if old_import in content:
            new_content = content.replace(old_import, new_import)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False

    except Exception as e:
        print(f"  Error processing {file_path}: {e}")
        return False

def main():
    """Update all frontend main.tsx files."""
    root_dir = Path(__file__).parent
    frontends_dir = root_dir / 'examples' / 'frontends'

    if not frontends_dir.exists():
        print(f"Frontends directory not found: {frontends_dir}")
        return

    count = 0

    # Find all main.tsx files
    for main_file in frontends_dir.glob('*/src/main.tsx'):
        if update_main_tsx(main_file):
            app_name = main_file.parent.parent.name
            print(f"Updated CSS import in: {app_name}")
            count += 1

    print(f"\nTotal files updated: {count}")

if __name__ == '__main__':
    main()
