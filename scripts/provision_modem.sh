#!/usr/bin/env bash
set -euo pipefail

MODEM_INDEX="${1:-0}"

mmcli -m "$MODEM_INDEX"
echo "To enable voice and packet data, verify carrier profile, APN, and audio routing."
echo "Sample APN setup:"
echo "  nmcli connection add type gsm ifname '*' con-name edge-node apn <your-apn>"
