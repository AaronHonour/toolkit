#!/bin/sh
set -e

# Check if turbo is available, if not install dependencies
if ! command -v turbo >/dev/null 2>&1; then
  echo "Turbo not found. Installing dependencies..."
  if [ -f package-lock.json ]; then
    npm ci --prefer-offline --no-audit
  else
    npm install
  fi
else
  echo "Dependencies already installed. Starting development server..."
fi

# Execute the command passed to the container
exec "$@"
