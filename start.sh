#!/usr/bin/env bash
# Start the Flipside web UI and automation server.
# Usage: ./start.sh [--port PORT] [--host HOST]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Activate venv if present and not already active
if [ -z "$VIRTUAL_ENV" ] && [ -d .venv ]; then
    source .venv/bin/activate
fi

# Don't write .pyc files — avoids stale bytecode after code changes
export PYTHONDONTWRITEBYTECODE=1

# Clear any leftover bytecode from previous runs
find "$SCRIPT_DIR" -path ./.venv -prune -o -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true

echo "Starting Flipside..."
exec python main.py "$@"
