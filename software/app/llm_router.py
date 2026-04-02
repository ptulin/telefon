from __future__ import annotations

from typing import Any
import os

import requests

from .interface import AdaptiveInterface


class HybridRouter:
    def __init__(self, settings: dict, connectivity):
        self.settings = settings
        self.connectivity = connectivity
        self.interface = AdaptiveInterface()

    def generate(self, prompt: str, tools: list[str] | None = None, preferred_mode: str | None = None) -> dict[str, Any]:
        interface_mode = preferred_mode or self.interface.resolve_mode(prompt)
        if self.connectivity.online:
            try:
                return self._cloud_generate(prompt, tools or [], interface_mode)
            except Exception:
                return self._local_generate(prompt, interface_mode)
        return self._local_generate(prompt, interface_mode)

    def _cloud_generate(self, prompt: str, tools: list[str], interface_mode: str) -> dict[str, Any]:
        backend = self.settings["backend"]
        token = os.environ.get(backend["auth_token_env"], "")
        response = requests.post(
            f'{backend["base_url"]}/v1/query',
            timeout=30,
            headers={"Authorization": f"Bearer {token}"} if token else {},
            json={
                "prompt": prompt,
                "interface_mode": interface_mode,
                "source": "device",
                "tools": tools,
            },
        )
        response.raise_for_status()
        payload = response.json()
        payload["mode"] = payload.get("mode", "cloud")
        payload["interface_mode"] = payload.get("interface_mode", interface_mode)
        return payload

    def _local_generate(self, prompt: str, interface_mode: str) -> dict[str, Any]:
        ollama = self.settings["ollama"]
        response = requests.post(
            f'{ollama["base_url"]}/api/generate',
            timeout=120,
            json={"model": self.settings["models"]["local_default"], "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        payload = response.json()
        return {
            "mode": "local",
            "interface_mode": interface_mode,
            "text": payload.get("response", ""),
            "reasoning": ["offline_fallback", "local_model"],
            "raw": payload,
        }
