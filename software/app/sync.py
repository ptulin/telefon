from __future__ import annotations

import os
import requests


class SyncClient:
    def __init__(self, settings: dict):
        self.settings = settings

    def sync_memories(self, records: list[dict]) -> set[str]:
        xai = self.settings["xai"]
        api_key = os.environ.get(xai["api_key_env"], "")
        if not api_key:
            return set()
        response = requests.post(
            f'{xai["base_url"]}/edge/sync',
            timeout=20,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"memories": records},
        )
        if response.status_code >= 400:
            return set()
        return {record["memory_id"] for record in records}
