from __future__ import annotations

import os
from typing import Any

import requests


class HybridRouter:
    def __init__(self, settings: dict, connectivity):
        self.settings = settings
        self.connectivity = connectivity

    def generate(self, prompt: str, tools: list[str] | None = None) -> dict[str, Any]:
        if self.connectivity.online:
            try:
                return self._cloud_generate(prompt, tools or [])
            except Exception:
                return self._local_generate(prompt)
        return self._local_generate(prompt)

    def _cloud_generate(self, prompt: str, tools: list[str]) -> dict[str, Any]:
        xai = self.settings["xai"]
        api_key = os.environ.get(xai["api_key_env"], "")
        response = requests.post(
            f'{xai["base_url"]}/chat/completions',
            timeout=30,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": self.settings["models"]["cloud_model"],
                "messages": [{"role": "user", "content": prompt}],
                "metadata": {"device_mode": "edge-hybrid", "tools": tools},
            },
        )
        response.raise_for_status()
        payload = response.json()
        return {
            "mode": "cloud",
            "text": payload["choices"][0]["message"]["content"],
            "raw": payload,
        }

    def _local_generate(self, prompt: str) -> dict[str, Any]:
        ollama = self.settings["ollama"]
        response = requests.post(
            f'{ollama["base_url"]}/api/generate',
            timeout=120,
            json={"model": self.settings["models"]["local_default"], "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        payload = response.json()
        return {"mode": "local", "text": payload.get("response", ""), "raw": payload}
