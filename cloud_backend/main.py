from __future__ import annotations

from pathlib import Path
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from cloud_backend.orchestrator import CloudOrchestrator
from cloud_backend.store import build_store
from shared.models import Contact, ConversationEntry, MemoryFact, utc_now


app = FastAPI(title="Hybrid AI Edge Node Cloud Backend")
store = build_store()
orchestrator = CloudOrchestrator(
    xai_base_url=os.environ.get("EDGE_XAI_BASE_URL", "https://api.x.ai/v1"),
    xai_api_key_env=os.environ.get("EDGE_XAI_API_ENV", "XAI_API_KEY"),
    model=os.environ.get("EDGE_CLOUD_MODEL", "grok-4-fast"),
)


class QueryRequest(BaseModel):
    prompt: str
    interface_mode: str = "chat"
    source: str = "device"


class SyncPushRequest(BaseModel):
    device_id: str
    memory_facts: list[dict] = []
    conversations: list[dict] = []
    uploads: list[dict] = []


class SyncPullRequest(BaseModel):
    device_id: str
    last_sync_at: str = ""


class UploadRequest(BaseModel):
    kind: str
    filename: str
    summary: str = ""
    source: str = "device"


class ContactRequest(BaseModel):
    name: str
    phone: str
    notes: str = ""


class FactRequest(BaseModel):
    category: str
    summary: str
    detail: str
    source: str = "cloud"


def _load_list(name: str) -> list[dict]:
    return store.load(name, [])


def _save_list(name: str, rows: list[dict]):
    store.save(name, rows)


@app.get("/health")
def health():
    return {"ok": True, "time": utc_now()}


@app.post("/v1/query")
def query(payload: QueryRequest):
    result = orchestrator.respond(payload.prompt, payload.interface_mode)
    conversations = _load_list("conversations.json")
    conversations.append(ConversationEntry.create("user", payload.prompt, payload.interface_mode).__dict__)
    conversations.append(ConversationEntry.create("assistant", result.text, payload.interface_mode).__dict__)
    _save_list("conversations.json", conversations)
    return result.to_dict()


@app.post("/v1/sync/push")
def sync_push(payload: SyncPushRequest):
    memory_facts = _load_list("memory_facts.json")
    conversations = _load_list("conversations.json")
    uploads = _load_list("uploads.json")
    memory_facts.extend(payload.memory_facts)
    conversations.extend(payload.conversations)
    uploads.extend(payload.uploads)
    _save_list("memory_facts.json", memory_facts)
    _save_list("conversations.json", conversations)
    _save_list("uploads.json", uploads)
    store.save("sync_meta.json", {"last_push_at": utc_now(), "device_id": payload.device_id})
    return {"accepted": True, "pushed_at": utc_now()}


@app.post("/v1/sync/pull")
def sync_pull(payload: SyncPullRequest):
    return {
        "memory_facts": _load_list("memory_facts.json"),
        "conversations": _load_list("conversations.json"),
        "uploads": _load_list("uploads.json"),
        "profile": store.load(
            "profile.json",
            {"preferences": [], "habits": [], "relationships": [], "life_details": []},
        ),
        "address_book": _load_list("address_book.json"),
        "server_time": utc_now(),
    }


@app.get("/v1/profile")
def profile():
    return store.load(
        "profile.json",
        {"preferences": [], "habits": [], "relationships": [], "life_details": []},
    )


@app.post("/v1/profile/facts")
def add_fact(payload: FactRequest):
    current = profile()
    if payload.category not in current:
        raise HTTPException(status_code=400, detail="unknown profile category")
    fact = MemoryFact.create(payload.category, payload.summary, payload.detail, payload.source).__dict__
    current[payload.category].append(fact)
    store.save("profile.json", current)
    return fact


@app.get("/v1/address-book")
def get_address_book():
    return {"contacts": _load_list("address_book.json")}


@app.post("/v1/address-book")
def add_contact(payload: ContactRequest):
    contacts = _load_list("address_book.json")
    contact = Contact.create(payload.name, payload.phone, payload.notes).__dict__
    contacts.append(contact)
    _save_list("address_book.json", contacts)
    return contact


@app.post("/v1/upload")
def upload(payload: UploadRequest):
    uploads = _load_list("uploads.json")
    record = {
        "upload_id": payload.filename + "-" + str(len(uploads) + 1),
        "kind": payload.kind,
        "filename": payload.filename,
        "summary": payload.summary,
        "source": payload.source,
        "created_at": utc_now(),
    }
    uploads.append(record)
    _save_list("uploads.json", uploads)
    return record
