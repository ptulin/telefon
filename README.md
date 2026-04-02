# Personal AI Phone

Personal AI Phone is now a web-first, smartphone-friendly prototype for a simplified AI operating layer that can gradually replace the normal app model.

The product goal is straightforward:

- one primary AI interface instead of many apps
- voice and touch parity for everyday actions
- cloud-first intelligence with local fallback where practical
- persistent personal memory across phone, desktop, and cloud
- a path toward future agent-to-agent coordination and eventually a dedicated thin-client device

This branch reframes the project from a custom edge-device-first concept into a normal-smartphone MVP that can help older or non-technical users with calling, memory, trusted contacts, onboarding, install-to-phone flows, and later calendar, camera, and delegated task support.

## Product Direction

The app is meant to become an AI operating layer in stages:

1. Assist the user with normal smartphone features.
2. Perform multi-step tasks across services on the user’s behalf.
3. Coordinate with other agents and services over the internet.
4. Eventually reduce dependence on the traditional smartphone UI entirely.

## Current Web Product

- Public landing page with account creation and sign-in
- Older-user-friendly dashboard with large text and large touch targets
- Memory vault for habits, preferences, relationships, and life details
- Trusted-circle and shared-contact account model
- Install page for adding the web app to a phone home screen
- Unified AI interface with adaptive modes:
  - `talk`
  - `call`
  - `calendar`
  - `camera`
  - `documents`
  - `memory`
- Daily briefing and quick action prompts

## Core MVP Direction

- Contacts lookup and voice-driven call initiation
- Calendar read/create/update with AI confirmation
- Camera and document understanding
- Reminders and daily briefings
- Future native app reuse of the same account and profile

## Forward-Looking Architecture

This repo is designed to support future capabilities such as:

- agent-to-agent scheduling
- commerce and booking workflows
- autonomous follow-ups and delegated tasks
- trusted action policies for purchases, sharing, and sensitive operations
- eventual migration to a dedicated thin-client AI device

## Repository Layout

```text
cloud_backend/   cloud API, orchestration, sync, canonical memory
desktop_app/     desktop companion client
docs/            product, architecture, capability matrix, migration
mobile_app/      smartphone-first app scaffold
shared/          shared data contracts
software/        legacy edge-device runtime from earlier prototype
hardware/        legacy thin-client hardware package from earlier prototype
mechanical/      legacy enclosure package from earlier prototype
```

## Smartphone-First Notes

- `mobile_app/` is now the primary client direction for the prototype.
- `cloud_backend/` remains the canonical backend for memory, sync, and strong-model access.
- `software/`, `hardware/`, and `mechanical/` are retained as the legacy path toward the future dedicated device.

## Quick Start

### Cloud Backend

```bash
cd /Users/patu/Documents/CursorProjects/telefon
./scripts/install_backend.sh
uvicorn cloud_backend.main:app --host 0.0.0.0 --port 9000
```

Hosted prototype target:

- Vercel for API hosting
- Supabase Storage for canonical state persistence
- Current live API: `https://telefon-phi.vercel.app`
- Current live web app: `https://telefon-phi.vercel.app`

### Desktop App

```bash
python3 desktop_app/main.py
```

### Mobile App

```bash
cd /Users/patu/Documents/CursorProjects/telefon/mobile_app
npm install
npm run start
```

## Important Scope Boundaries

What a smartphone app can do well:

- contacts access
- call initiation
- calendar access
- camera capture and upload
- local encrypted storage and sync
- reminders, memory, and guided workflows

What remains constrained by mobile OS rules:

- deep call interception
- unrestricted background execution
- always-on camera/microphone behavior
- fully autonomous sensitive actions without explicit confirmation

## Docs To Read First

- [Product spec](/Users/patu/Documents/CursorProjects/telefon/docs/product_spec.md)
- [Capability matrix](/Users/patu/Documents/CursorProjects/telefon/docs/capability_matrix.md)
- [Smartphone architecture](/Users/patu/Documents/CursorProjects/telefon/docs/architecture.md)
- [Migration plan](/Users/patu/Documents/CursorProjects/telefon/docs/smartphone_migration.md)
