#!/usr/bin/env bash
# Initial setup for the Flipside project.
# Creates a virtual environment, installs dependencies, and sets up Playwright.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

MIN_MINOR=10

# Find a Python >= 3.MIN_MINOR, checking versioned binaries then bare python3
PYTHON=""
for minor in $(seq 20 -1 "$MIN_MINOR"); do
    candidate="python3.$minor"
    if command -v "$candidate" &>/dev/null; then
        PYTHON="$candidate"
        break
    fi
done
if [ -z "$PYTHON" ] && command -v python3 &>/dev/null; then
    if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,$MIN_MINOR) else 1)" 2>/dev/null; then
        PYTHON="python3"
    fi
fi

if [ -z "$PYTHON" ]; then
    echo "Error: Python 3.$MIN_MINOR or later is required but not found."
    echo "Install a supported version and re-run ./setup.sh"
    exit 1
fi

echo "==> Using $($PYTHON --version)"

echo "==> Creating virtual environment..."
$PYTHON -m venv .venv
source .venv/bin/activate

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo "==> Installing Playwright browsers..."
playwright install chromium --with-deps

echo ""
echo "Setup complete. Run ./start.sh to launch Flipside."
