from __future__ import annotations

from pathlib import Path
import json

from shared.models import Contact


class AddressBook:
    def __init__(self, root: Path):
        self.path = root / "address_book.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def all(self) -> list[dict]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def add(self, name: str, phone: str, notes: str = "") -> dict:
        contacts = self.all()
        contact = Contact.create(name, phone, notes).__dict__
        contacts.append(contact)
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(contacts, handle, indent=2)
        return contact

    def match(self, query: str) -> dict | None:
        lowered = query.lower()
        for contact in self.all():
            if lowered in contact["name"].lower() or lowered in contact["phone"]:
                return contact
        return None
