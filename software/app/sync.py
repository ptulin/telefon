from __future__ import annotations

import os
import requests


class SyncClient:
    def __init__(self, settings: dict):
        self.settings = settings

    def _headers(self) -> dict:
        backend = self.settings["backend"]
        token = os.environ.get(backend["auth_token_env"], "")
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def sync_push(self, device_id: str, memory_facts: list[dict], conversations: list[dict], uploads: list[dict]) -> bool:
        backend = self.settings["backend"]
        response = requests.post(
            f'{backend["base_url"]}/v1/sync/push',
            timeout=20,
            headers=self._headers(),
            json={
                "device_id": device_id,
                "memory_facts": memory_facts,
                "conversations": conversations,
                "uploads": uploads,
            },
        )
        return response.status_code < 400

    def sync_pull(self, device_id: str, last_sync_at: str = "") -> dict:
        backend = self.settings["backend"]
        response = requests.post(
            f'{backend["base_url"]}/v1/sync/pull',
            timeout=20,
            headers=self._headers(),
            json={"device_id": device_id, "last_sync_at": last_sync_at},
        )
        response.raise_for_status()
        return response.json()
