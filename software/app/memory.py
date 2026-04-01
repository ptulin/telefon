from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import uuid


@dataclass
class MemoryRecord:
    memory_id: str
    text: str
    created_at: str
    synced: bool = False


class MemoryVault:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.index_file = self.root / "memory.jsonl"

    def add(self, text: str) -> MemoryRecord:
        record = MemoryRecord(
            memory_id=str(uuid.uuid4()),
            text=text,
            created_at=datetime.now(timezone.utc).isoformat(),
            synced=False,
        )
        with self.index_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.__dict__) + "\n")
        return record

    def pending_sync(self) -> list[MemoryRecord]:
        if not self.index_file.exists():
            return []
        records: list[MemoryRecord] = []
        with self.index_file.open("r", encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                if not row.get("synced", False):
                    records.append(MemoryRecord(**row))
        return records

    def mark_synced(self, synced_ids: set[str]):
        if not self.index_file.exists():
            return
        rows = []
        with self.index_file.open("r", encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                if row["memory_id"] in synced_ids:
                    row["synced"] = True
                rows.append(row)
        with self.index_file.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row) + "\n")
