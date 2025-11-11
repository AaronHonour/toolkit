#!/usr/bin/env python3
"""Update docker-compose.yml for new directory structure."""

import re
from pathlib import Path

def main():
    compose_file = Path('examples/docker-compose.yml')

    with open(compose_file, 'r') as f:
        content = f.read()

    # Fix context paths (should be ../python for backends, ../frontend for frontend)
    # Backend services build context
    content = re.sub(
        r'(# App \d+:.*?\n.*?build:\n\s+context: )\.',
        r'\1../python',
        content,
        flags=re.MULTILINE
    )

    # Fix volume mounts for backends
    # From: - ../<backend_dir>:/app
    # To: - ./backends/<backend_dir>:/app/backends/<backend_dir>
    content = re.sub(
        r'- \.\./backends/(\d+_[^:]+):/app/backends/\1',
        r'- ./backends/\1:/app/backends/\1',
        content
    )

    # Fix PYTHONPATH
    content = re.sub(
        r'PYTHONPATH: /app',
        r'PYTHONPATH: /app/backends',
        content
    )

    # Frontend context and volumes
    content = re.sub(
        r'(frontend:.*?build:\n\s+context: )\.\./frontend',
        r'\1../frontend',
        content,
        flags=re.DOTALL
    )

    content = re.sub(
        r'- \.\./frontend:/app',
        r'- ../frontend:/app/frontend\n      - ../examples/frontends:/app/frontends',
        content
    )

    with open(compose_file, 'w') as f:
        f.write(content)

    print("docker-compose.yml updated successfully")

if __name__ == '__main__':
    main()
