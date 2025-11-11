#!/usr/bin/env python3
"""Add CORS middleware to all backend FastAPI applications."""

import re
from pathlib import Path

def add_cors_to_file(file_path):
    """Add CORS middleware to a FastAPI main.py file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if CORS is already added
        if 'CORSMiddleware' in content:
            return False

        # Find the FastAPI import and add CORSMiddleware
        fastapi_import_pattern = r'(from fastapi import [^\n]+)'
        match = re.search(fastapi_import_pattern, content)

        if not match:
            print(f"  Could not find FastAPI import in {file_path}")
            return False

        # Add CORSMiddleware import after FastAPI imports
        cors_import = '\nfrom fastapi.middleware.cors import CORSMiddleware'

        # Find where to insert (after the last fastapi import)
        insert_pos = match.end()
        content = content[:insert_pos] + cors_import + content[insert_pos:]

        # Find the app = FastAPI(...) definition
        app_pattern = r'(app = FastAPI\([^)]*\))'
        match = re.search(app_pattern, content)

        if not match:
            print(f"  Could not find FastAPI app definition in {file_path}")
            return False

        # Add CORS middleware after app definition
        cors_config = '''

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)'''

        insert_pos = match.end()
        content = content[:insert_pos] + cors_config + content[insert_pos:]

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return True

    except Exception as e:
        print(f"  Error processing {file_path}: {e}")
        return False

def main():
    """Add CORS to all backend main.py files."""
    root_dir = Path(__file__).parent
    backends_dir = root_dir / 'examples' / 'backends'

    if not backends_dir.exists():
        print(f"Backends directory not found: {backends_dir}")
        return

    count = 0

    # Find all main.py files
    for main_file in backends_dir.glob('*/src/main.py'):
        if add_cors_to_file(main_file):
            print(f"Added CORS to: {main_file.relative_to(root_dir)}")
            count += 1

    print(f"\nTotal files updated: {count}")

if __name__ == '__main__':
    main()
