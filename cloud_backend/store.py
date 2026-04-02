from __future__ import annotations

from pathlib import Path
import json
import os

import requests


class JsonStore:
    def load(self, name: str, default):
        raise NotImplementedError

    def save(self, name: str, value):
        raise NotImplementedError


class LocalJsonStore(JsonStore):
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        return self.root / name

    def load(self, name: str, default):
        path = self._path(name)
        if not path.exists():
            return default
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def save(self, name: str, value):
        with self._path(name).open("w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2)


class SupabaseStorageJsonStore(JsonStore):
    def __init__(self, base_url: str, service_role_key: str, bucket: str, prefix: str = "state"):
        self.base_url = base_url.rstrip("/")
        self.service_role_key = service_role_key
        self.bucket = bucket
        self.prefix = prefix.strip("/")

    def _headers(self, content_type: str = "application/json") -> dict:
        return {
            "Authorization": f"Bearer {self.service_role_key}",
            "apikey": self.service_role_key,
            "Content-Type": content_type,
        }

    def _object_path(self, name: str) -> str:
        return f"{self.prefix}/{name}" if self.prefix else name

    def ensure_bucket(self):
        response = requests.get(
            f"{self.base_url}/storage/v1/bucket",
            timeout=20,
            headers=self._headers("application/json"),
        )
        response.raise_for_status()
        buckets = response.json()
        if any(bucket.get("name") == self.bucket for bucket in buckets):
            return
        create = requests.post(
            f"{self.base_url}/storage/v1/bucket",
            timeout=20,
            headers=self._headers("application/json"),
            json={"name": self.bucket, "public": False},
        )
        create.raise_for_status()

    def load(self, name: str, default):
        object_path = self._object_path(name)
        response = requests.get(
            f"{self.base_url}/storage/v1/object/authenticated/{self.bucket}/{object_path}",
            timeout=20,
            headers=self._headers("application/json"),
        )
        if response.status_code in (400, 404):
            return default
        response.raise_for_status()
        return response.json()

    def save(self, name: str, value):
        object_path = self._object_path(name)
        response = requests.post(
            f"{self.base_url}/storage/v1/object/{self.bucket}/{object_path}",
            timeout=20,
            headers={**self._headers("application/json"), "x-upsert": "true"},
            data=json.dumps(value),
        )
        if response.status_code in (200, 201):
            return
        if response.status_code == 400 and "Duplicate" in response.text:
            update = requests.put(
                f"{self.base_url}/storage/v1/object/{self.bucket}/{object_path}",
                timeout=20,
                headers={**self._headers("application/json"), "x-upsert": "true"},
                data=json.dumps(value),
            )
            update.raise_for_status()
            return
        response.raise_for_status()


def build_store() -> JsonStore:
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_service_role = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    supabase_bucket = os.environ.get("SUPABASE_STATE_BUCKET", "personal-ai-phone")
    if supabase_url and supabase_service_role:
        store = SupabaseStorageJsonStore(supabase_url, supabase_service_role, supabase_bucket)
        store.ensure_bucket()
        return store
    return LocalJsonStore(Path(os.environ.get("EDGE_CLOUD_DATA", "cloud_backend/data")))
