from __future__ import annotations

from pathlib import Path
import json

from shared.models import ConversationEntry, MemoryFact


class MemoryVault:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.facts_file = self.root / "memory_facts.json"
        self.conversations_file = self.root / "conversations.json"
        self.profile_file = self.root / "profile.json"

    def _load_json(self, path: Path, default):
        if not path.exists():
            return default
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _save_json(self, path: Path, payload):
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

    def add_fact(self, category: str, summary: str, detail: str, source: str = "device") -> dict:
        rows = self._load_json(self.facts_file, [])
        record = MemoryFact.create(category, summary, detail, source).__dict__
        rows.append(record)
        self._save_json(self.facts_file, rows)
        self._apply_profile_fact(record)
        return record

    def add_conversation(self, role: str, text: str, mode: str) -> dict:
        rows = self._load_json(self.conversations_file, [])
        record = ConversationEntry.create(role, text, mode).__dict__
        rows.append(record)
        self._save_json(self.conversations_file, rows)
        return record

    def _apply_profile_fact(self, fact: dict):
        profile = self.profile()
        profile.setdefault(fact["category"], [])
        profile[fact["category"]].append(fact)
        self._save_json(self.profile_file, profile)

    def profile(self) -> dict:
        return self._load_json(
            self.profile_file,
            {"preferences": [], "habits": [], "relationships": [], "life_details": []},
        )

    def pending_sync(self) -> dict:
        facts = [row for row in self._load_json(self.facts_file, []) if not row.get("synced", False)]
        conversations = [row for row in self._load_json(self.conversations_file, []) if not row.get("synced", False)]
        return {"memory_facts": facts, "conversations": conversations}

    def mark_synced(self, fact_ids: set[str], conversation_ids: set[str]):
        facts = self._load_json(self.facts_file, [])
        for row in facts:
            if row["fact_id"] in fact_ids:
                row["synced"] = True
        self._save_json(self.facts_file, facts)

        conversations = self._load_json(self.conversations_file, [])
        for row in conversations:
            if row["entry_id"] in conversation_ids:
                row["synced"] = True
        self._save_json(self.conversations_file, conversations)

    def merge_remote(self, payload: dict):
        if payload.get("memory_facts"):
            self._save_json(self.facts_file, payload["memory_facts"])
        if payload.get("conversations"):
            self._save_json(self.conversations_file, payload["conversations"])
        if payload.get("profile"):
            self._save_json(self.profile_file, payload["profile"])
