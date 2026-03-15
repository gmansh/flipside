#!/usr/bin/env bash
# Run all tests (unit + e2e).
# Usage: ./test.sh [--unit | --e2e] [pytest args...]
#   --unit   Run only unit tests
#   --e2e    Run only e2e browser tests
#   (none)   Run all tests

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Activate venv if present and not already active
if [ -z "$VIRTUAL_ENV" ] && [ -d .venv ]; then
    source .venv/bin/activate
fi

case "${1:-}" in
    --unit)
        shift
        echo "==> Running unit tests..."
        pytest tests/ -v -m "not e2e" "$@"
        ;;
    --e2e)
        shift
        echo "==> Running e2e tests..."
        pytest tests/e2e/ -v "$@"
        ;;
    *)
        echo "==> Running unit tests..."
        pytest tests/ -v -m "not e2e" "$@"
        echo ""
        echo "==> Running e2e tests..."
        pytest tests/e2e/ -v "$@"
        ;;
esac
