from __future__ import annotations

from pathlib import Path
import time

from software.app.config import load_settings
from software.app.memory import MemoryVault
from software.app.sync import SyncClient
from software.app.uploads import UploadManager


def main():
    settings = load_settings()
    vault = MemoryVault(Path(settings.storage_root) / "memory")
    uploads = UploadManager(Path(settings.raw["uploads"]["root"]))
    sync = SyncClient(settings.raw)
    interval = int(settings.raw["memory"]["sync_interval_seconds"])

    while True:
        pending = vault.pending_sync()
        pending_uploads = uploads.pending()
        pushed = sync.sync_push(
            settings.device_id,
            pending.get("memory_facts", []),
            pending.get("conversations", []),
            pending_uploads,
        )
        if pushed:
            vault.mark_synced(
                {row["fact_id"] for row in pending.get("memory_facts", [])},
                {row["entry_id"] for row in pending.get("conversations", [])},
            )
            uploads.mark_synced({row["upload_id"] for row in pending_uploads})
            remote = sync.sync_pull(settings.device_id)
            vault.merge_remote(remote)
        time.sleep(interval)


if __name__ == "__main__":
    main()
