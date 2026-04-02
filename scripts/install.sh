#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_SRC="$ROOT_DIR/software/config/device.example.yaml"
CONFIG_DST="$ROOT_DIR/software/config/device.yaml"

sudo apt-get update
sudo apt-get install -y \
  python3 python3-pip python3-venv \
  modemmanager network-manager \
  ollama \
  espeak-ng libatlas-base-dev portaudio19-dev \
  python3-tk

python3 -m venv "$ROOT_DIR/.venv"
source "$ROOT_DIR/.venv/bin/activate"
pip install --upgrade pip
pip install -r "$ROOT_DIR/software/requirements.txt"

if [[ ! -f "$CONFIG_DST" ]]; then
  cp "$CONFIG_SRC" "$CONFIG_DST"
fi

sudo mkdir -p /var/lib/edge-node/memory
sudo mkdir -p /var/lib/edge-node/uploads
sudo chown -R "$USER":"$USER" /var/lib/edge-node

ollama pull phi3.5:mini || true
ollama pull gemma2:2b || true

echo "Installation complete. Edit software/config/device.yaml and set XAI_API_KEY plus EDGE_NODE_TOKEN if using backend auth."
