#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KICAD_DIR="$ROOT_DIR/hardware/kicad"
OUT_DIR="$ROOT_DIR/hardware/fabrication/gerbers"

mkdir -p "$OUT_DIR"
echo "Open $KICAD_DIR/edge-node.kicad_pcb in KiCad and generate fabrication outputs into $OUT_DIR."
echo "This helper is intentionally conservative until the PCB is finalized."
