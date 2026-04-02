from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import yaml


@dataclass
class Settings:
    raw: dict

    @property
    def storage_root(self) -> Path:
        return Path(self.raw["device"]["storage_root"])

    @property
    def ui_port(self) -> int:
        return int(self.raw["device"]["ui_port"])

    @property
    def device_id(self) -> str:
        return str(self.raw["device"]["device_id"])


def load_settings() -> Settings:
    config_path = Path(os.environ.get("EDGE_NODE_CONFIG", "software/config/device.yaml"))
    if not config_path.is_absolute():
        config_path = Path.cwd() / config_path
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return Settings(raw=data)
