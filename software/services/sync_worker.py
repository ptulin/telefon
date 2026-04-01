from __future__ import annotations

from pathlib import Path
import time

from software.app.config import load_settings
from software.app.memory import MemoryVault
from software.app.sync import SyncClient


def main():
    settings = load_settings()
    vault = MemoryVault(Path(settings.storage_root) / "memory")
    sync = SyncClient(settings.raw)
    interval = int(settings.raw["memory"]["sync_interval_seconds"])

    while True:
        pending = vault.pending_sync()
        if pending:
            synced_ids = sync.sync_memories([record.__dict__ for record in pending])
            if synced_ids:
                vault.mark_synced(synced_ids)
        time.sleep(interval)


if __name__ == "__main__":
    main()
