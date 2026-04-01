# Hybrid AI Edge Node

Hybrid AI Edge Node is a pocket-sized AI companion built around a Raspberry Pi Compute Module 4 / Pi 5-class architecture with cellular voice/data, offline local AI fallback, and cloud-first orchestration for Grok/xAI.

This repository is organized as a prototype manufacturing package plus deployable device software:

- `docs/` system architecture, manufacturing notes, assembly, and validation plans
- `hardware/` KiCad project sources, BOMs, fabrication outputs, and interface specs
- `mechanical/` enclosure CAD source and manufacturing notes
- `software/` edge services, UI, sync engine, memory vault, and local/cloud AI routing
- `scripts/` installation, provisioning, and export helpers
- `systemd/` auto-start services for device runtime

## Current Scope

This repo provides a serious first prototype package for EVT-style builds:

- Hardware architecture and schematic capture starter files
- Preliminary PCB floorplanning constraints and fabrication package structure
- BOM and CPL templates for JLCPCB / PCBWay workflows
- A deployable Python software stack for hybrid AI, telephony integration, voice I/O, memory sync, and small-screen UI
- Assembly and bring-up documentation

Before production release, the design still requires:

- Full schematic review and ERC cleanup in KiCad
- RF layout review for LTE/5G, GNSS, antennas, and EMC
- Thermal and battery safety validation
- Carrier certification planning for cellular voice support
- Mechanical tolerance verification and material selection sign-off

## Recommended Prototype Configuration

- SoC: Raspberry Pi Compute Module 4, 8GB RAM, 32GB eMMC
- Display: 3.2" OLED or e-paper capacitive touch panel over SPI/DSI
- Modem: Quectel EC25-E for LTE voice/data EVT, RM520N-GL for later 5G variant
- Audio: I2S MEMS microphone + Class-D speaker amplifier
- Power: 1500-2200 mAh LiPo, USB-C PD input, solar trickle input via MPPT charger
- Storage: 128GB industrial microSD for logs, models, and local memory vault

## Quick Start

```bash
cd /Users/patu/Documents/CursorProjects/telefon
chmod +x scripts/install.sh
./scripts/install.sh
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable edge-node.service edge-node-monitor.service edge-node-sync.service
sudo systemctl start edge-node.service
```

## Software Highlights

- Online mode routes high-complexity requests to Grok/xAI tools
- Offline mode falls back to Ollama-hosted small models
- Memory vault stores encrypted local notes and embeddings, then syncs upstream
- Telephony layer uses ModemManager or AT-command fallback
- Voice stack supports streaming ASR/TTS and wake interaction patterns

## Repository Layout

```text
hardware/
  bom/
  fabrication/
  kicad/
  specs/
mechanical/
  case/
docs/
software/
  app/
  config/
  services/
  ui/
scripts/
systemd/
```
