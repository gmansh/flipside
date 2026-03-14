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

echo "Starting Flipside..."
exec python main.py "$@"
