from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MemoryFact:
    fact_id: str
    category: str
    summary: str
    detail: str
    source: str
    created_at: str
    updated_at: str
    synced: bool = False

    @classmethod
    def create(cls, category: str, summary: str, detail: str, source: str) -> "MemoryFact":
        now = utc_now()
        return cls(
            fact_id=str(uuid.uuid4()),
            category=category,
            summary=summary,
            detail=detail,
            source=source,
            created_at=now,
            updated_at=now,
            synced=False,
        )


@dataclass
class ConversationEntry:
    entry_id: str
    role: str
    text: str
    mode: str
    created_at: str
    synced: bool = False

    @classmethod
    def create(cls, role: str, text: str, mode: str) -> "ConversationEntry":
        return cls(
            entry_id=str(uuid.uuid4()),
            role=role,
            text=text,
            mode=mode,
            created_at=utc_now(),
            synced=False,
        )


@dataclass
class UploadRecord:
    upload_id: str
    kind: str
    filename: str
    path: str
    summary: str
    created_at: str
    synced: bool = False

    @classmethod
    def create(cls, kind: str, filename: str, path: str, summary: str) -> "UploadRecord":
        return cls(
            upload_id=str(uuid.uuid4()),
            kind=kind,
            filename=filename,
            path=path,
            summary=summary,
            created_at=utc_now(),
            synced=False,
        )


@dataclass
class Contact:
    contact_id: str
    name: str
    phone: str
    notes: str = ""

    @classmethod
    def create(cls, name: str, phone: str, notes: str = "") -> "Contact":
        return cls(contact_id=str(uuid.uuid4()), name=name, phone=phone, notes=notes)


@dataclass
class QueryResult:
    text: str
    mode: str
    interface_mode: str
    reasoning: list[str] = field(default_factory=list)
    action_url: str | None = None
    action_label: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
