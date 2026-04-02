from __future__ import annotations

from pathlib import Path
import json
import shutil

from shared.models import UploadRecord


class UploadManager:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.documents_dir = self.root / "documents"
        self.photos_dir = self.root / "photos"
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        self.photos_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / "uploads.json"

    def _load(self) -> list[dict]:
        if not self.index_path.exists():
            return []
        with self.index_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _save(self, rows: list[dict]):
        with self.index_path.open("w", encoding="utf-8") as handle:
            json.dump(rows, handle, indent=2)

    def add_document(self, source_path: Path, summary: str = "") -> dict:
        target = self.documents_dir / source_path.name
        shutil.copy2(source_path, target)
        record = UploadRecord.create("document", source_path.name, str(target), summary).__dict__
        rows = self._load()
        rows.append(record)
        self._save(rows)
        return record

    def add_photo_record(self, record: dict):
        rows = self._load()
        rows.append(record)
        self._save(rows)

    def pending(self) -> list[dict]:
        return [row for row in self._load() if not row.get("synced", False)]

    def mark_synced(self, upload_ids: set[str]):
        rows = self._load()
        for row in rows:
            if row["upload_id"] in upload_ids:
                row["synced"] = True
        self._save(rows)
