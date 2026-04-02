#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 -m venv "$ROOT_DIR/.venv-backend"
source "$ROOT_DIR/.venv-backend/bin/activate"
pip install --upgrade pip
pip install -r "$ROOT_DIR/software/requirements.txt"

mkdir -p "$ROOT_DIR/cloud_backend/data"
echo "Backend environment ready. Export XAI_API_KEY before running uvicorn."
