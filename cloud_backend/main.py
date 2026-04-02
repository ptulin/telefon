from __future__ import annotations

from dataclasses import asdict
import base64
import hashlib
import hmac
import os
import secrets
import time
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from pydantic import BaseModel, EmailStr

from cloud_backend.orchestrator import CloudOrchestrator
from cloud_backend.store import build_store
from cloud_backend.web import (
    manifest_payload,
    render_app_page,
    render_download_page,
    render_landing_page,
    service_worker_payload,
)
from shared.models import Contact, ConversationEntry, MemoryFact, utc_now


app = FastAPI(title="Personal AI Phone")
store = build_store()
orchestrator = CloudOrchestrator(
    xai_base_url=os.environ.get("EDGE_XAI_BASE_URL", "https://api.x.ai/v1"),
    xai_api_key_env=os.environ.get("EDGE_XAI_API_ENV", "XAI_API_KEY"),
    model=os.environ.get("EDGE_CLOUD_MODEL", "grok-4-fast"),
)

SESSION_COOKIE = "personal_ai_session"
SESSION_SECRET = os.environ.get("SESSION_SECRET", "personal-ai-phone-session-secret")


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


class RegisterRequest(BaseModel):
    display_name: str
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    identifier: str
    password: str


class ProfileUpdateRequest(BaseModel):
    display_name: str
    preference_summary: str = ""
    voice_guidance: bool = True
    text_scale: str = "large"


class AppContactRequest(BaseModel):
    name: str
    phone: str
    notes: str = ""
    shared: bool = False


class TrustedCircleRequest(BaseModel):
    name: str
    email: EmailStr
    role: str


class AppMemoryRequest(BaseModel):
    category: str
    summary: str
    detail: str = ""


def _load_list(name: str) -> list[dict]:
    return store.load(name, [])


def _save_list(name: str, rows: list[dict]):
    store.save(name, rows)


def _load_users() -> list[dict]:
    return store.load("users.json", [])


def _save_users(rows: list[dict]):
    store.save("users.json", rows)


def _user_record_key(user_id: str) -> str:
    return f"user-record-{user_id}.json"


def _user_lookup_key(kind: str, value: str) -> str:
    digest = hashlib.sha256(value.lower().strip().encode("utf-8")).hexdigest()
    return f"user-lookup-{kind}-{digest}.json"


def _save_user_record(user: dict):
    store.save(_user_record_key(user["user_id"]), user)
    store.save(_user_lookup_key("email", user["email"]), {"user_id": user["user_id"]})
    store.save(_user_lookup_key("username", user["username"]), {"user_id": user["user_id"]})


def _password_hash(salt: str, password: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000).hex()


def _default_user_state(user: dict) -> dict:
    return {
        "profile": {
            "display_name": user["display_name"],
            "username": user["username"],
            "email": user["email"],
        },
        "accessibility": {
            "voice_guidance": True,
            "text_scale": "large",
        },
        "preferences": [],
        "habits": [],
        "relationships": [],
        "life_details": [],
        "contacts": [],
        "trusted_circle": [],
        "assistant_history": [],
    }


def _user_state_key(user_id: str) -> str:
    return f"user-state-{user_id}.json"


def _legacy_section_state(user_id: str, defaults: dict) -> dict:
    return {
        "profile": defaults["profile"],
        "accessibility": store.load(f"user-{user_id}-accessibility.json", defaults["accessibility"]),
        "preferences": store.load(f"user-{user_id}-preferences.json", defaults["preferences"]),
        "habits": store.load(f"user-{user_id}-habits.json", defaults["habits"]),
        "relationships": store.load(f"user-{user_id}-relationships.json", defaults["relationships"]),
        "life_details": store.load(f"user-{user_id}-life_details.json", defaults["life_details"]),
        "contacts": store.load(f"user-{user_id}-contacts.json", defaults["contacts"]),
        "trusted_circle": store.load(f"user-{user_id}-trusted_circle.json", defaults["trusted_circle"]),
        "assistant_history": store.load(f"user-{user_id}-assistant_history.json", defaults["assistant_history"]),
    }


def _normalize_user_state(user: dict, state: dict | None) -> dict:
    defaults = _default_user_state(user)
    current = state or {}
    normalized = {
        "profile": {
            "display_name": user["display_name"],
            "username": user["username"],
            "email": user["email"],
        },
        "accessibility": current.get("accessibility", defaults["accessibility"]),
        "preferences": current.get("preferences", defaults["preferences"]),
        "habits": current.get("habits", defaults["habits"]),
        "relationships": current.get("relationships", defaults["relationships"]),
        "life_details": current.get("life_details", defaults["life_details"]),
        "contacts": current.get("contacts", defaults["contacts"]),
        "trusted_circle": current.get("trusted_circle", defaults["trusted_circle"]),
        "assistant_history": current.get("assistant_history", defaults["assistant_history"]),
    }
    if not isinstance(normalized["contacts"], list):
        normalized["contacts"] = []
    if not isinstance(normalized["trusted_circle"], list):
        normalized["trusted_circle"] = []
    if not isinstance(normalized["assistant_history"], list):
        normalized["assistant_history"] = []
    return normalized


def _load_user_state(user_id: str, user: dict | None = None) -> dict:
    user = user or _find_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    current = store.load(_user_state_key(user_id), None)
    if current:
        return _normalize_user_state(user, current)

    legacy_states = store.load("user_states.json", {})
    if user_id in legacy_states:
        normalized = _normalize_user_state(user, legacy_states[user_id])
        store.save(_user_state_key(user_id), normalized)
        return normalized

    defaults = _default_user_state(user)
    legacy_nested = store.load(f"user/{user_id}/state.json", None)
    if legacy_nested:
        normalized = _normalize_user_state(user, legacy_nested)
    else:
        normalized = _normalize_user_state(user, _legacy_section_state(user_id, defaults))

    store.save(_user_state_key(user_id), normalized)
    return normalized


def _save_user_state(user_id: str, state: dict, user: dict | None = None):
    user = user or _find_user_by_id(user_id) or {
        "display_name": state.get("profile", {}).get("display_name", "User"),
        "username": state.get("profile", {}).get("username", user_id),
        "email": state.get("profile", {}).get("email", ""),
    }
    store.save(_user_state_key(user_id), _normalize_user_state(user, state))


def _find_user_by_id(user_id: str) -> dict | None:
    for _ in range(4):
        found = store.load(_user_record_key(user_id), None)
        if found:
            return found
        found = next((user for user in _load_users() if user["user_id"] == user_id), None)
        if found:
            return found
        time.sleep(0.2)
    return None


def _find_user(identifier: str) -> dict | None:
    lowered = identifier.lower().strip()
    for _ in range(4):
        for kind in ("email", "username"):
            lookup = store.load(_user_lookup_key(kind, lowered), None)
            if lookup and lookup.get("user_id"):
                found = _find_user_by_id(lookup["user_id"])
                if found:
                    return found
        found = next(
            (
                user
                for user in _load_users()
                if user["email"].lower() == lowered or user["username"].lower() == lowered
            ),
            None,
        )
        if found:
            if found.get("user_id") and "password_salt" not in found:
                hydrated = _find_user_by_id(found["user_id"])
                if hydrated:
                    return hydrated
            return found
        time.sleep(0.2)
    return None


def _create_session(user: dict) -> str:
    issued_at = utc_now()
    payload = "|".join(
        [
            user["user_id"],
            user["display_name"],
            user["username"],
            user["email"],
            issued_at,
        ]
    )
    signature = hmac.new(SESSION_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    token = base64.urlsafe_b64encode(f"{payload}|{signature}".encode("utf-8")).decode("utf-8")
    return token


def _decode_session(token: str) -> dict | None:
    try:
        decoded = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        user_id, display_name, username, email, issued_at, signature = decoded.split("|", 5)
    except Exception:
        return None
    payload = "|".join([user_id, display_name, username, email, issued_at])
    expected = hmac.new(SESSION_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return None
    return {
        "user_id": user_id,
        "display_name": display_name,
        "username": username,
        "email": email,
        "issued_at": issued_at,
    }


def _current_user(request: Request) -> dict:
    token = request.cookies.get(SESSION_COOKIE, "")
    if not token:
        raise HTTPException(status_code=401, detail="not signed in")
    session = _decode_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="invalid session")
    return {
        "user_id": session["user_id"],
        "display_name": session["display_name"],
        "username": session["username"],
        "email": session["email"],
    }


def _assistant_response(prompt: str, interface_mode: str, user_state: dict) -> dict[str, Any]:
    lower = prompt.lower()
    contacts = user_state.get("contacts", [])
    matched_contact = next((contact for contact in contacts if contact["name"].lower() in lower), None)

    if interface_mode == "call" and matched_contact:
        text = (
            f"I found {matched_contact['name']} at {matched_contact['phone']}. "
            "On a phone-capable client I would launch the dialer next."
        )
        return {"text": text, "mode": "cloud-prototype", "interface_mode": "call", "reasoning": ["user_contact_match"]}

    if interface_mode == "calendar" and any(token in lower for token in ["schedule", "meeting", "appointment", "lunch"]):
        text = (
            "I can help schedule that. In this web-first version I’ll gather the details, save the intent to your "
            "assistant history, and prepare for future calendar and agent-to-agent scheduling."
        )
        return {"text": text, "mode": "cloud-prototype", "interface_mode": "calendar", "reasoning": ["calendar_intent"]}

    if any(token in lower for token in ["buy", "order", "purchase"]):
        text = (
            "I can help with that purchase workflow. The safe next step is to confirm the item, budget, and delivery "
            "preferences before handing it off to a shopping agent."
        )
        return {"text": text, "mode": "cloud-prototype", "interface_mode": "talk", "reasoning": ["commerce_intent"]}

    result = orchestrator.respond(prompt, interface_mode)
    return result.to_dict()


def _build_daily_briefing(state: dict) -> dict[str, Any]:
    shared_contacts = [contact for contact in state.get("contacts", []) if contact.get("shared")]
    suggestions = [
        "Call a favorite contact without searching through apps.",
        "Save a life detail so the assistant gets more personal over time.",
        "Invite a trusted helper who can share important contacts.",
    ]
    if not state.get("contacts"):
        suggestions[0] = "Add your first contact so voice calling feels instant later."
    if not state.get("trusted_circle"):
        suggestions[2] = "Add a trusted family member or caregiver for shared support."
    return {
        "headline": "Your assistant is ready to simplify the day.",
        "summary": (
            f"{len(state.get('contacts', []))} contacts, "
            f"{len(shared_contacts)} shared contacts, "
            f"{len(state.get('trusted_circle', []))} trusted people, and "
            f"{len(state.get('preferences', []))} saved preferences."
        ),
        "suggestions": suggestions,
    }


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    try:
        _current_user(request)
        return RedirectResponse("/app", status_code=302)
    except HTTPException:
        return HTMLResponse(render_landing_page())


@app.get("/app", response_class=HTMLResponse)
def app_page(request: Request):
    _current_user(request)
    return HTMLResponse(render_app_page())


@app.get("/download", response_class=HTMLResponse)
def download_page(request: Request):
    user = _current_user(request)
    return HTMLResponse(render_download_page(user["display_name"]))


@app.get("/manifest.webmanifest")
def manifest():
    return Response(content=manifest_payload(), media_type="application/manifest+json")


@app.get("/sw.js")
def service_worker():
    return Response(content=service_worker_payload(), media_type="application/javascript")


@app.post("/auth/register")
def register(payload: RegisterRequest):
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="password must be at least 8 characters")
    if _find_user(payload.email):
        raise HTTPException(status_code=400, detail="email is already registered")
    if _find_user(payload.username):
        raise HTTPException(status_code=400, detail="username is already taken")

    users = _load_users()
    salt = secrets.token_hex(16)
    user = {
        "user_id": secrets.token_hex(12),
        "display_name": payload.display_name.strip() or payload.username.strip(),
        "username": payload.username.strip(),
        "email": payload.email.strip(),
        "password_salt": salt,
        "password_hash": _password_hash(salt, payload.password),
        "created_at": utc_now(),
    }
    users.append(user)
    _save_users(users)
    _save_user_record(user)
    _save_user_state(user["user_id"], _default_user_state(user), user)

    token = _create_session(user)
    response = JSONResponse({"ok": True, "user": {"display_name": user["display_name"], "username": user["username"]}})
    response.set_cookie(SESSION_COOKIE, token, httponly=True, secure=True, samesite="lax", max_age=60 * 60 * 24 * 30)
    return response


@app.post("/auth/login")
def login(payload: LoginRequest):
    user = _find_user(payload.identifier)
    if not user:
        raise HTTPException(status_code=401, detail="account not found")
    if user.get("user_id") and "password_salt" not in user:
        user = _find_user_by_id(user["user_id"]) or user
    if "password_salt" not in user or "password_hash" not in user:
        raise HTTPException(status_code=401, detail="account not ready")
    expected = _password_hash(user["password_salt"], payload.password)
    if not hmac.compare_digest(expected, user["password_hash"]):
        raise HTTPException(status_code=401, detail="incorrect password")

    token = _create_session(user)
    response = JSONResponse({"ok": True, "user": {"display_name": user["display_name"], "username": user["username"]}})
    response.set_cookie(SESSION_COOKIE, token, httponly=True, secure=True, samesite="lax", max_age=60 * 60 * 24 * 30)
    return response


@app.post("/auth/logout")
def logout(request: Request):
    response = JSONResponse({"ok": True})
    response.delete_cookie(SESSION_COOKIE)
    return response


@app.get("/auth/me")
def auth_me(request: Request):
    user = _current_user(request)
    state = _load_user_state(user["user_id"], user)
    return {
        "user": {
            "display_name": user["display_name"],
            "username": user["username"],
            "email": user["email"],
        },
        "state": state,
        "daily_briefing": _build_daily_briefing(state),
    }


@app.get("/app/api/bootstrap")
def app_bootstrap(request: Request):
    user = _current_user(request)
    state = _load_user_state(user["user_id"], user)
    return {
        "user": {
            "display_name": user["display_name"],
            "username": user["username"],
            "email": user["email"],
        },
        "state": state,
        "daily_briefing": _build_daily_briefing(state),
    }


@app.post("/app/api/profile")
def update_profile(payload: ProfileUpdateRequest, request: Request):
    user = _current_user(request)
    users = _load_users()
    for row in users:
        if row["user_id"] == user["user_id"]:
            row["display_name"] = payload.display_name.strip() or row["display_name"]
            user = row
            break
    _save_users(users)
    _save_user_record(user)

    state = _load_user_state(user["user_id"], user)
    state["accessibility"]["voice_guidance"] = payload.voice_guidance
    state["accessibility"]["text_scale"] = payload.text_scale
    if payload.preference_summary.strip():
        state["preferences"] = [
            {
                "fact_id": secrets.token_hex(8),
                "summary": payload.preference_summary.strip(),
                "created_at": utc_now(),
            }
        ]
    state["profile"]["display_name"] = user["display_name"]
    _save_user_state(user["user_id"], state, user)
    return {
        "ok": True,
        "state": state,
        "user": {"display_name": user["display_name"], "username": user["username"], "email": user["email"]},
        "daily_briefing": _build_daily_briefing(state),
    }


@app.post("/app/api/contacts")
def add_app_contact(payload: AppContactRequest, request: Request):
    user = _current_user(request)
    state = _load_user_state(user["user_id"], user)
    contact = Contact.create(payload.name, payload.phone, payload.notes).__dict__
    contact["shared"] = payload.shared
    state["contacts"].append(contact)
    _save_user_state(user["user_id"], state, user)
    return {"contact": contact, "state": state, "daily_briefing": _build_daily_briefing(state)}


@app.post("/app/api/trusted-circle")
def add_trusted_circle(payload: TrustedCircleRequest, request: Request):
    user = _current_user(request)
    state = _load_user_state(user["user_id"], user)
    state["trusted_circle"].append(
        {
            "trusted_id": secrets.token_hex(8),
            "name": payload.name,
            "email": payload.email,
            "role": payload.role,
            "created_at": utc_now(),
        }
    )
    _save_user_state(user["user_id"], state, user)
    return {"ok": True, "state": state, "daily_briefing": _build_daily_briefing(state)}


@app.post("/app/api/memory")
def add_memory(payload: AppMemoryRequest, request: Request):
    user = _current_user(request)
    state = _load_user_state(user["user_id"], user)
    category = payload.category if payload.category in {"preferences", "habits", "relationships", "life_details"} else "life_details"
    state[category].append(
        {
            "fact_id": secrets.token_hex(8),
            "summary": payload.summary.strip(),
            "detail": payload.detail.strip(),
            "created_at": utc_now(),
        }
    )
    _save_user_state(user["user_id"], state, user)
    return {"ok": True, "state": state, "daily_briefing": _build_daily_briefing(state)}


@app.get("/app/api/daily-briefing")
def daily_briefing(request: Request):
    user = _current_user(request)
    state = _load_user_state(user["user_id"], user)
    return _build_daily_briefing(state)


@app.post("/app/api/assistant")
def app_assistant(payload: QueryRequest, request: Request):
    user = _current_user(request)
    state = _load_user_state(user["user_id"], user)
    result = _assistant_response(payload.prompt, payload.interface_mode, state)
    state["assistant_history"].append(
        {
            "entry_id": secrets.token_hex(8),
            "prompt": payload.prompt,
            "response": result["text"],
            "mode": payload.interface_mode,
            "created_at": utc_now(),
        }
    )
    _save_user_state(user["user_id"], state, user)
    return result


@app.get("/health")
def health():
    return {"ok": True, "time": utc_now()}


@app.post("/v1/query")
def query(payload: QueryRequest):
    result = orchestrator.respond(payload.prompt, payload.interface_mode)
    conversations = _load_list("conversations.json")
    conversations.append(asdict(ConversationEntry.create("user", payload.prompt, payload.interface_mode)))
    conversations.append(asdict(ConversationEntry.create("assistant", result.text, payload.interface_mode)))
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
