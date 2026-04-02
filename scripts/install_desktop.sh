#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 -m venv "$ROOT_DIR/.venv-desktop"
source "$ROOT_DIR/.venv-desktop/bin/activate"
pip install --upgrade pip
pip install requests

echo "Desktop app environment ready. Run: python3 desktop_app/main.py"
