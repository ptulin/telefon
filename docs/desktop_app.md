# Desktop App

The desktop app is a cross-platform companion that exposes the same AI identity and memory graph as the pocket device.

## UX Principles

- one primary AI window
- adaptive panels rather than separate apps
- persistent voice + text parity
- instant access to memory, calls, uploads, and camera-derived artifacts

## Modes

- `chat`: main assistant interaction
- `memory`: facts, summaries, and relationship history
- `phone`: address book and call launch shortcuts
- `documents`: upload and summarize files
- `camera`: inspect synced captures from the edge device

## Implementation

- Tkinter for simple cross-platform packaging
- backend over HTTP
- shared JSON data contracts from `shared/`
