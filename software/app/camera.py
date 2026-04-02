from __future__ import annotations

from pathlib import Path
import shutil

from shared.models import UploadRecord


class CameraManager:
    def __init__(self, uploads_root: Path):
        self.photos_root = uploads_root / "photos"
        self.photos_root.mkdir(parents=True, exist_ok=True)

    def import_photo(self, source_path: Path, summary: str = "") -> dict:
        target = self.photos_root / source_path.name
        shutil.copy2(source_path, target)
        return UploadRecord.create("photo", source_path.name, str(target), summary).__dict__

    def analyze_stub(self, prompt: str) -> dict:
        return {
            "mode": "camera",
            "interface_mode": "camera",
            "text": f"Queued camera analysis request: {prompt}",
            "reasoning": ["camera_mode", "vision_requested"],
        }
