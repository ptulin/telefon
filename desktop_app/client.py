from __future__ import annotations

import requests


class BackendClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def query(self, prompt: str, interface_mode: str = "chat") -> dict:
        response = requests.post(
            f"{self.base_url}/v1/query",
            timeout=45,
            json={"prompt": prompt, "interface_mode": interface_mode, "source": "desktop"},
        )
        response.raise_for_status()
        return response.json()

    def profile(self) -> dict:
        response = requests.get(f"{self.base_url}/v1/profile", timeout=20)
        response.raise_for_status()
        return response.json()

    def contacts(self) -> dict:
        response = requests.get(f"{self.base_url}/v1/address-book", timeout=20)
        response.raise_for_status()
        return response.json()
