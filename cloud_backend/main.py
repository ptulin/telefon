from __future__ import annotations

from dataclasses import asdict
import base64
import hashlib
import hmac
import os
import secrets
import time
from typing import Any, Optional
from urllib.parse import quote

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from pydantic import BaseModel, EmailStr
import requests

from cloud_backend.orchestrator import CloudOrchestrator
from cloud_backend.store import build_store
from cloud_backend.web import (
    manifest_payload,
    render_app_page,
    render_download_page,
    render_landing_page,
    render_reset_password_page,
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


def _html_response(content: str) -> HTMLResponse:
    response = HTMLResponse(content)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def _friendly_validation_message(exc: RequestValidationError) -> str:
    errors = exc.errors()
    if not errors:
        return "Please check your details and try again."
    first = errors[0]
    field = first.get("loc", ["field"])[-1]
    if field == "email":
        return "Enter a valid email address."
    if field == "phone_number":
        return "Enter a valid phone number."
    if field == "password":
        return "Enter your password."
    label = str(field).replace("_", " ")
    return f"Please check your {label} and try again."


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": _friendly_validation_message(exc)})


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
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProfileUpdateRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str = ""
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


class DirectoryAddRequest(BaseModel):
    user_id: str


class ContactImportRow(BaseModel):
    name: str
    phone: str = ""
    email: str = ""
    notes: str = ""
    shared: bool = False


class ContactImportRequest(BaseModel):
    contacts: list[ContactImportRow]


class LinkDeliveryRequest(BaseModel):
    channel: str = "email"


class PasswordHelpRequest(BaseModel):
    email: EmailStr
    channel: str = "email"


class PasswordResetRequest(BaseModel):
    token: str
    new_password: str


class AdminUserUpdateRequest(BaseModel):
    user_id: str
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone_number: str = ""
    is_admin: Optional[bool] = None
    is_disabled: Optional[bool] = None


def _load_list(name: str) -> list[dict]:
    return store.load(name, [])


def _save_list(name: str, rows: list[dict]):
    store.save(name, rows)


def _load_users() -> list[dict]:
    return [_ensure_user_shape(row) for row in store.load("users.json", [])]


def _save_users(rows: list[dict]):
    store.save("users.json", [_ensure_user_shape(row) for row in rows])


def _user_record_key(user_id: str) -> str:
    return f"user-record-{user_id}.json"


def _user_lookup_key(kind: str, value: str) -> str:
    digest = hashlib.sha256(value.lower().strip().encode("utf-8")).hexdigest()
    return f"user-lookup-{kind}-{digest}.json"


def _compose_display_name(first_name: str, last_name: str, email: str = "") -> str:
    full_name = " ".join(part for part in [first_name.strip(), last_name.strip()] if part.strip()).strip()
    if full_name:
        return full_name
    if email.strip():
        return email.split("@", 1)[0]
    return "Friend"


def _ensure_user_shape(user: dict | None) -> dict | None:
    if not user:
        return None
    normalized = dict(user)
    first_name = normalized.get("first_name", "").strip()
    last_name = normalized.get("last_name", "").strip()
    if not first_name and not last_name:
        display_name = normalized.get("display_name", "").strip()
        if display_name:
            parts = display_name.split(" ", 1)
            first_name = parts[0].strip()
            last_name = parts[1].strip() if len(parts) > 1 else ""
    normalized["first_name"] = first_name
    normalized["last_name"] = last_name
    normalized["display_name"] = _compose_display_name(first_name, last_name, normalized.get("email", ""))
    if not normalized.get("username"):
        normalized["username"] = normalized.get("email", "").split("@", 1)[0] or normalized.get("user_id", "")
    return normalized


def _save_user_record(user: dict):
    user = _ensure_user_shape(user)
    store.save(_user_record_key(user["user_id"]), user)
    store.save(_user_lookup_key("email", user["email"]), {"user_id": user["user_id"]})


def _replace_user_in_index(user: dict):
    user = _ensure_user_shape(user)
    users = _load_users()
    replaced = False
    for idx, row in enumerate(users):
        if row.get("user_id") == user["user_id"]:
            users[idx] = user
            replaced = True
            break
    if not replaced:
        users.append(user)
    _save_users(users)


def _password_hash(salt: str, password: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000).hex()


def _normalize_phone(value: str) -> str:
    digits = "".join(ch for ch in value if ch.isdigit() or ch == "+").strip()
    return digits


def _is_admin(user: dict) -> bool:
    return bool(user.get("is_admin")) or user.get("email", "").lower().strip() == "ptulin@gmail.com"


def _default_user_state(user: dict) -> dict:
    user = _ensure_user_shape(user)
    return {
        "profile": {
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "display_name": user["display_name"],
            "email": user["email"],
            "phone_number": user.get("phone_number", ""),
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
    user = _ensure_user_shape(user)
    defaults = _default_user_state(user)
    current = state or {}
    profile = current.get("profile", {})
    normalized = {
        "profile": {
            "first_name": profile.get("first_name", user["first_name"]),
            "last_name": profile.get("last_name", user["last_name"]),
            "display_name": user["display_name"],
            "email": user["email"],
            "phone_number": user.get("phone_number", ""),
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
    profile = state.get("profile", {})
    user = _ensure_user_shape(
        user
        or _find_user_by_id(user_id)
        or {
            "first_name": profile.get("first_name", "Friend"),
            "last_name": profile.get("last_name", ""),
            "display_name": profile.get("display_name", "Friend"),
            "email": profile.get("email", ""),
            "user_id": user_id,
        }
    )
    store.save(_user_state_key(user_id), _normalize_user_state(user, state))


def _find_user_by_id(user_id: str) -> dict | None:
    for _ in range(4):
        found = store.load(_user_record_key(user_id), None)
        if found:
            return _ensure_user_shape(found)
        found = next((user for user in _load_users() if user["user_id"] == user_id), None)
        if found:
            return _ensure_user_shape(found)
        time.sleep(0.2)
    return None


def _find_user(email: str) -> dict | None:
    lowered = email.lower().strip()
    for _ in range(4):
        lookup = store.load(_user_lookup_key("email", lowered), None)
        if lookup and lookup.get("user_id"):
            found = _find_user_by_id(lookup["user_id"])
            if found:
                return _ensure_user_shape(found)
        found = next(
            (
                user
                for user in _load_users()
                if user["email"].lower() == lowered
            ),
            None,
        )
        if found:
            if found.get("user_id") and "password_salt" not in found:
                hydrated = _find_user_by_id(found["user_id"])
                if hydrated:
                    return _ensure_user_shape(hydrated)
            return _ensure_user_shape(found)
        time.sleep(0.2)
    return None


def _create_session(user: dict) -> str:
    user = _ensure_user_shape(user)
    issued_at = utc_now()
    payload = "|".join(
        [
            user["user_id"],
            user["first_name"],
            user["last_name"],
            user["email"],
            user.get("phone_number", ""),
            "1" if _is_admin(user) else "0",
            issued_at,
        ]
    )
    signature = hmac.new(SESSION_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    token = base64.urlsafe_b64encode(f"{payload}|{signature}".encode("utf-8")).decode("utf-8")
    return token


def _decode_session(token: str) -> dict | None:
    try:
        decoded = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        user_id, first_name, last_name, email, phone_number, is_admin_flag, issued_at, signature = decoded.split("|", 7)
    except Exception:
        return None
    payload = "|".join([user_id, first_name, last_name, email, phone_number, is_admin_flag, issued_at])
    expected = hmac.new(SESSION_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return None
    return {
        "user_id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "display_name": _compose_display_name(first_name, last_name, email),
        "email": email,
        "phone_number": phone_number,
        "is_admin": is_admin_flag == "1",
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
        "first_name": session["first_name"],
        "last_name": session["last_name"],
        "display_name": session["display_name"],
        "email": session["email"],
        "phone_number": session.get("phone_number", ""),
        "is_admin": session.get("is_admin", False),
    }


def _assistant_response(prompt: str, interface_mode: str, user_state: dict) -> dict[str, Any]:
    lower = prompt.lower().strip()
    contacts = user_state.get("contacts", [])
    trusted_people = user_state.get("trusted_circle", [])
    prompt_digits = "".join(ch for ch in prompt if ch.isdigit() or ch == "+")

    def contact_score(contact: dict) -> int:
        name = str(contact.get("name", "")).strip().lower()
        if not name:
            return 0
        score = 0
        if name in lower:
            score += 100
        name_parts = [part for part in name.replace(",", " ").split() if len(part) > 1]
        for part in name_parts:
            if part in lower:
                score += 15
        phone = str(contact.get("phone", "")).strip()
        digits = "".join(ch for ch in phone if ch.isdigit() or ch == "+")
        if digits and digits in prompt_digits:
            score += 100
        return score

    ranked_contacts = sorted(contacts, key=contact_score, reverse=True)
    matched_contact = ranked_contacts[0] if ranked_contacts and contact_score(ranked_contacts[0]) > 0 else None

    if any(token in lower for token in ["who are my contacts", "show my contacts", "my contacts", "saved contacts"]):
        if not contacts:
            return {
                "text": "You do not have any saved contacts yet. Open Profile to find another Telefon user or import contacts from this device.",
                "mode": "cloud-prototype",
                "interface_mode": "talk",
                "reasoning": ["contacts_empty"],
                "action_url": "/app#profile",
                "action_label": "Add contacts",
            }
        top_contacts = ", ".join(contact["name"] for contact in contacts[:5])
        return {
            "text": f"You currently have {len(contacts)} saved contacts. Here are the first ones: {top_contacts}.",
            "mode": "cloud-prototype",
            "interface_mode": "talk",
            "reasoning": ["contacts_summary"],
            "action_url": "/app#profile",
            "action_label": "View contacts",
        }

    if any(token in lower for token in ["add someone to contacts", "add someone", "add contact", "contact list", "how do i add"]) and "call" not in lower:
        summary = (
            "Open Profile, then use Find on Telefon to search by name, email, or phone number. "
            "If the person already uses Telefon, tap Add to my contacts. "
            "You can also use Import from this device to pick people from your phone or laptop address book."
        )
        if contacts:
            summary += f" You already have {len(contacts)} saved contact" + ("" if len(contacts) == 1 else "s") + "."
        return {
            "text": summary,
            "mode": "cloud-prototype",
            "interface_mode": "talk",
            "reasoning": ["contact_help"],
            "action_url": "/app#profile",
            "action_label": "Open contacts",
        }

    if any(token in lower for token in ["find user", "find someone", "search user", "find on telefon", "look up"]) and "contact" in lower:
        return {
            "text": (
                "Use Find on Telefon inside Profile. Type a name, email, or phone number, then tap Add to my contacts. "
                "That is the fastest way to connect with another Telefon user."
            ),
            "mode": "cloud-prototype",
            "interface_mode": "talk",
            "reasoning": ["user_directory_help"],
            "action_url": "/app#profile",
            "action_label": "Find on Telefon",
        }

    if any(token in lower for token in ["import contacts", "import my contacts", "phone contacts", "device contacts", "address book"]):
        return {
            "text": (
                "Open Profile and choose Import from this device. "
                "If your browser supports contact access, you can pick specific people or import all of the selected ones without typing them by hand."
            ),
            "mode": "cloud-prototype",
            "interface_mode": "talk",
            "reasoning": ["contact_import_help"],
            "action_url": "/app#profile",
            "action_label": "Import contacts",
        }

    if any(token in lower for token in ["install", "download", "add to home screen", "phone link"]):
        return {
            "text": (
                "Open Install in the header, then choose Email me the app. "
                "I’ll send the phone link to the same email address on your account so you can open it on your phone."
            ),
            "mode": "cloud-prototype",
            "interface_mode": "talk",
            "reasoning": ["install_help"],
        }

    if (interface_mode == "call" or "call" in lower or "phone" in lower) and matched_contact:
        phone = matched_contact["phone"]
        tel_target = "".join(ch for ch in phone if ch.isdigit() or ch == "+")
        text = (
            f"I found {matched_contact['name']} at {matched_contact['phone']}. "
            "Tap the button below and I’ll hand this off to your phone dialer."
        )
        return {
            "text": text,
            "mode": "cloud-prototype",
            "interface_mode": "call",
            "reasoning": ["user_contact_match"],
            "action_url": f"tel:{tel_target}",
            "action_label": f"Call {matched_contact['name']}",
        }

    if interface_mode == "call" and prompt_digits:
        return {
            "text": "I found a phone number in your request. Tap below and I’ll open the dialer with it ready.",
            "mode": "cloud-prototype",
            "interface_mode": "call",
            "reasoning": ["phone_number_from_prompt"],
            "action_url": f"tel:{prompt_digits}",
            "action_label": "Call this number",
        }

    if interface_mode == "call":
        suggestions = ", ".join(contact["name"] for contact in contacts[:3])
        extra = f" Try one of these: {suggestions}." if suggestions else " Add a contact first in Profile so calling works."
        return {
            "text": "Tell me who to call by name or paste a phone number." + extra,
            "mode": "cloud-prototype",
            "interface_mode": "call",
            "reasoning": ["call_missing_target"],
        }

    if interface_mode == "calendar" and any(token in lower for token in ["schedule", "meeting", "appointment", "lunch"]):
        text = (
            "I can help schedule that. In this web-first version I’ll gather the details, save the intent to your "
            "assistant history, and prepare for future calendar and agent-to-agent scheduling."
        )
        return {"text": text, "mode": "cloud-prototype", "interface_mode": "calendar", "reasoning": ["calendar_intent"]}

    if any(token in lower for token in ["help me", "how do i", "what can i do", "what should i do"]):
        return {
            "text": (
                f"You can use me to call people, find Telefon users, import contacts from your device, save life details, and prepare scheduling tasks. "
                f"Right now you have {len(contacts)} contacts and {len(trusted_people)} trusted helper" + ("" if len(trusted_people) == 1 else "s") + "."
            ),
            "mode": "cloud-prototype",
            "interface_mode": "talk",
            "reasoning": ["guided_help"],
            "action_url": "/app#profile",
            "action_label": "Open profile tools",
        }

    if any(token in lower for token in ["buy", "order", "purchase"]):
        text = (
            "I can help with that purchase workflow. The safe next step is to confirm the item, budget, and delivery "
            "preferences before handing it off to a shopping agent."
        )
        return {"text": text, "mode": "cloud-prototype", "interface_mode": "talk", "reasoning": ["commerce_intent"]}

    context = _assistant_context(user_state)
    result = orchestrator.respond(prompt, interface_mode, context)
    return result.to_dict()


def _assistant_context(user_state: dict) -> dict[str, Any]:
    profile = user_state.get("profile", {})
    contacts = user_state.get("contacts", [])
    trusted = user_state.get("trusted_circle", [])
    assistant_history = user_state.get("assistant_history", [])

    def format_memory(bucket: str, label: str) -> list[str]:
        entries = user_state.get(bucket, [])[:3]
        return [f"{label}: {entry.get('summary', '')}" for entry in entries if entry.get("summary")]

    memory_lines = (
        format_memory("preferences", "Preference")
        + format_memory("habits", "Habit")
        + format_memory("relationships", "Relationship")
        + format_memory("life_details", "Life detail")
    )
    contacts_lines = [
        f"{contact.get('name', 'Unknown')} ({contact.get('phone') or contact.get('email') or 'no phone'})"
        for contact in contacts[:8]
    ]
    trusted_lines = [
        f"{person.get('name', 'Unknown')} ({person.get('role', 'trusted person')})"
        for person in trusted[:6]
    ]
    history_lines = [
        f"User: {entry.get('prompt', '')} | Assistant: {entry.get('response', '')}"
        for entry in assistant_history[-5:]
    ]
    relationship_names = [entry.get("summary", "") for entry in user_state.get("relationships", []) if entry.get("summary")]
    preference_names = [entry.get("summary", "") for entry in user_state.get("preferences", []) if entry.get("summary")]
    habit_names = [entry.get("summary", "") for entry in user_state.get("habits", []) if entry.get("summary")]
    life_detail_names = [entry.get("summary", "") for entry in user_state.get("life_details", []) if entry.get("summary")]
    contact_names = [contact.get("name", "") for contact in contacts if contact.get("name")]
    trusted_names = [person.get("name", "") for person in trusted if person.get("name")]

    personal_summary_parts = []
    if profile.get("first_name"):
        personal_summary_parts.append(f"The user is {profile.get('first_name')} {profile.get('last_name', '').strip()}.".strip())
    if preference_names:
        personal_summary_parts.append("Preferences: " + "; ".join(preference_names[:5]) + ".")
    if habit_names:
        personal_summary_parts.append("Habits and routines: " + "; ".join(habit_names[:5]) + ".")
    if relationship_names:
        personal_summary_parts.append("Important relationships: " + "; ".join(relationship_names[:5]) + ".")
    if life_detail_names:
        personal_summary_parts.append("Life details: " + "; ".join(life_detail_names[:5]) + ".")
    if contact_names:
        personal_summary_parts.append("Saved contacts include " + ", ".join(contact_names[:6]) + ".")
    if trusted_names:
        personal_summary_parts.append("Trusted helpers include " + ", ".join(trusted_names[:4]) + ".")

    recent_intents = []
    for entry in assistant_history[-6:]:
        prompt = str(entry.get("prompt", "")).strip()
        if prompt:
            recent_intents.append(prompt)

    return {
        "profile": {
            "first_name": profile.get("first_name", ""),
            "last_name": profile.get("last_name", ""),
            "email": profile.get("email", ""),
            "phone_number": profile.get("phone_number", ""),
            "display_name": profile.get("display_name", ""),
        },
        "memory_summary": " | ".join(memory_lines) if memory_lines else "No saved memory yet.",
        "contacts_summary": " | ".join(contacts_lines) if contacts_lines else "No contacts yet.",
        "trusted_summary": " | ".join(trusted_lines) if trusted_lines else "No trusted helpers yet.",
        "history_summary": " | ".join(history_lines) if history_lines else "No recent assistant history.",
        "personal_summary": " ".join(personal_summary_parts) if personal_summary_parts else "The assistant is still learning about this user.",
        "recent_intents": recent_intents,
        "contacts_count": len(contacts),
        "trusted_count": len(trusted),
        "tools": [
            "find Telefon users",
            "add contact",
            "import contacts from device",
            "open profile tools",
            "call saved contact",
            "email install link",
            "save memory",
        ],
    }


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


def _public_app_url(request: Request, path: str = "/app") -> str:
    return str(request.base_url).rstrip("/") + path


def _password_reset_token_key(token: str) -> str:
    return f"password-reset-{token}.json"


def _send_email_via_resend(to_email: str, subject: str, html: str) -> bool:
    api_key = os.environ.get("RESEND_API_KEY", "")
    from_email = os.environ.get("RESEND_FROM_EMAIL", "")
    if not api_key or not from_email:
        return False
    response = requests.post(
        "https://api.resend.com/emails",
        timeout=20,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={"from": from_email, "to": [to_email], "subject": subject, "html": html},
    )
    return response.ok


def _send_sms_via_twilio(to_phone: str, body: str) -> bool:
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    from_phone = os.environ.get("TWILIO_FROM_NUMBER", "")
    if not account_sid or not auth_token or not from_phone:
        return False
    response = requests.post(
        f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json",
        timeout=20,
        auth=(account_sid, auth_token),
        data={"From": from_phone, "To": to_phone, "Body": body},
    )
    return response.ok


def _deliver_install_link(user: dict, request: Request, channel: str) -> dict[str, Any]:
    if channel != "email":
        raise HTTPException(status_code=400, detail="email delivery is enabled for this beta")
    app_url = _public_app_url(request)
    message = (
        f"Open your Personal AI Phone here: {app_url} "
        f"and sign in as {user['email']}."
    )
    email = user["email"]
    subject = "Your Personal AI Phone link"
    html = (
        f"<p>Open your Personal AI Phone here:</p><p><a href=\"{app_url}\">{app_url}</a></p>"
        f"<p>Sign in with {email}.</p>"
    )
    if _send_email_via_resend(email, subject, html):
        return {"ok": True, "delivery": "email-sent", "message": f"Email sent to {email}."}
    mailto_url = f"mailto:{quote(email)}?subject={quote(subject)}&body={quote(message)}"
    return {
        "ok": True,
        "delivery": "email-compose",
        "message": f"Opening your mail app for {email}.",
        "action_url": mailto_url,
    }


def _create_password_reset(user: dict, request: Request, channel: str) -> dict[str, Any]:
    if channel != "email":
        raise HTTPException(status_code=400, detail="email password recovery is enabled for this beta")
    token = secrets.token_urlsafe(24)
    reset_url = _public_app_url(request, f"/reset-password?token={token}")
    store.save(
        _password_reset_token_key(token),
        {
            "user_id": user["user_id"],
            "expires_at": time.time() + 3600,
        },
    )
    message = (
        f"Reset your Personal AI Phone password here: {reset_url}"
    )
    if _send_email_via_resend(
        user["email"],
        "Reset your Personal AI Phone password",
        f"<p>Choose a new password here:</p><p><a href=\"{reset_url}\">{reset_url}</a></p>",
    ):
        return {"ok": True, "delivery": "email-sent", "message": f"Password reset sent to {user['email']}."}
    return {"ok": True, "delivery": "direct-link", "message": "Open the reset page to choose a new password.", "action_url": reset_url}


def _require_admin(user: dict):
    if not _is_admin(user):
        raise HTTPException(status_code=403, detail="admin only")


def _all_users() -> list[dict]:
    seen: dict[str, dict] = {}
    for user in _load_users():
        if user.get("user_id"):
            seen[user["user_id"]] = user
    return list(seen.values())


def _admin_user_summary(user: dict) -> dict[str, Any]:
    user = _ensure_user_shape(user)
    state = _load_user_state(user["user_id"], user)
    memory_count = sum(len(state.get(bucket, [])) for bucket in ("preferences", "habits", "relationships", "life_details"))
    return {
        "user_id": user["user_id"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "display_name": user["display_name"],
        "email": user["email"],
        "phone_number": user.get("phone_number", ""),
        "created_at": user.get("created_at", ""),
        "last_login_at": user.get("last_login_at", ""),
        "is_admin": _is_admin(user),
        "is_disabled": bool(user.get("is_disabled")),
        "contacts_count": len(state.get("contacts", [])),
        "trusted_count": len(state.get("trusted_circle", [])),
        "memory_count": memory_count,
    }


def _public_user_summary(user: dict) -> dict[str, Any]:
    user = _ensure_user_shape(user)
    return {
        "user_id": user["user_id"],
        "display_name": user["display_name"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "phone_number": user.get("phone_number", ""),
    }


def _contact_key(contact: dict) -> str:
    if contact.get("linked_user_id"):
        return f"user:{contact['linked_user_id']}"
    phone = _normalize_phone(str(contact.get("phone", "")))
    if phone:
        return f"phone:{phone}"
    email = str(contact.get("email", "")).strip().lower()
    if email:
        return f"email:{email}"
    return f"name:{str(contact.get('name', '')).strip().lower()}"


def _append_contact_if_new(state: dict, contact: dict) -> bool:
    seen = {_contact_key(existing) for existing in state.get("contacts", [])}
    key = _contact_key(contact)
    if key in seen:
        return False
    state["contacts"].append(contact)
    return True


def _analytics_snapshot() -> dict[str, Any]:
    users = sorted(_all_users(), key=lambda row: row.get("created_at", ""), reverse=True)
    summaries = [_admin_user_summary(user) for user in users]
    return {
        "totals": {
            "users": len(users),
            "admins": sum(1 for row in summaries if row["is_admin"]),
            "disabled": sum(1 for row in summaries if row["is_disabled"]),
            "contacts": sum(row["contacts_count"] for row in summaries),
            "trusted_people": sum(row["trusted_count"] for row in summaries),
            "memory_items": sum(row["memory_count"] for row in summaries),
        },
        "recent_users": summaries[:10],
    }


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    try:
        _current_user(request)
        return RedirectResponse("/app", status_code=302)
    except HTTPException:
        return _html_response(render_landing_page())


@app.get("/app", response_class=HTMLResponse)
def app_page(request: Request):
    try:
        _current_user(request)
        return _html_response(render_app_page())
    except HTTPException:
        return RedirectResponse("/", status_code=302)


@app.get("/download", response_class=HTMLResponse)
def download_page(request: Request):
    try:
        user = _current_user(request)
        return _html_response(render_download_page(user["first_name"] or user["display_name"]))
    except HTTPException:
        return RedirectResponse("/", status_code=302)


@app.get("/manifest.webmanifest")
def manifest():
    response = Response(content=manifest_payload(), media_type="application/manifest+json")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get("/sw.js")
def service_worker():
    response = Response(content=service_worker_payload(), media_type="application/javascript")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.post("/auth/register")
def register(payload: RegisterRequest):
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="password must be at least 8 characters")
    phone_number = _normalize_phone(payload.phone_number)
    if not phone_number:
        raise HTTPException(status_code=400, detail="phone number is required")
    first_name = payload.first_name.strip()
    last_name = payload.last_name.strip()
    if not first_name or not last_name:
        raise HTTPException(status_code=400, detail="first name and last name are required")
    if _find_user(payload.email):
        raise HTTPException(status_code=400, detail="email is already registered")

    users = _load_users()
    salt = secrets.token_hex(16)
    user = {
        "user_id": secrets.token_hex(12),
        "first_name": first_name,
        "last_name": last_name,
        "display_name": _compose_display_name(first_name, last_name, payload.email.strip()),
        "username": payload.email.strip().split("@", 1)[0],
        "email": payload.email.strip(),
        "phone_number": phone_number,
        "password_salt": salt,
        "password_hash": _password_hash(salt, payload.password),
        "created_at": utc_now(),
        "last_login_at": utc_now(),
        "is_admin": payload.email.strip().lower() == "ptulin@gmail.com",
        "is_disabled": False,
    }
    users.append(user)
    _save_users(users)
    _save_user_record(user)
    _save_user_state(user["user_id"], _default_user_state(user), user)

    token = _create_session(user)
    response = JSONResponse({"ok": True, "user": {"first_name": user["first_name"], "last_name": user["last_name"], "display_name": user["display_name"]}})
    response.set_cookie(SESSION_COOKIE, token, httponly=True, secure=True, samesite="lax", max_age=60 * 60 * 24 * 30)
    return response


@app.post("/auth/login")
def login(payload: LoginRequest):
    user = _find_user(payload.email)
    if not user:
        raise HTTPException(status_code=401, detail="account not found")
    if user.get("user_id") and "password_salt" not in user:
        user = _find_user_by_id(user["user_id"]) or user
    if "password_salt" not in user or "password_hash" not in user:
        raise HTTPException(status_code=401, detail="account not ready")
    if user.get("is_disabled"):
        raise HTTPException(status_code=403, detail="account disabled")
    expected = _password_hash(user["password_salt"], payload.password)
    if not hmac.compare_digest(expected, user["password_hash"]):
        raise HTTPException(status_code=401, detail="incorrect password")

    user["last_login_at"] = utc_now()
    _replace_user_in_index(user)
    _save_user_record(user)
    token = _create_session(user)
    response = JSONResponse({"ok": True, "user": {"first_name": user["first_name"], "last_name": user["last_name"], "display_name": user["display_name"]}})
    response.set_cookie(SESSION_COOKIE, token, httponly=True, secure=True, samesite="lax", max_age=60 * 60 * 24 * 30)
    return response


@app.post("/auth/logout")
def logout(request: Request):
    response = JSONResponse({"ok": True})
    response.delete_cookie(SESSION_COOKIE)
    return response


@app.post("/auth/password-help")
def password_help(payload: PasswordHelpRequest, request: Request):
    user = _find_user(payload.email)
    if not user:
        return {"ok": True, "message": "If that account exists, password help is ready."}
    return _create_password_reset(user, request, payload.channel)


@app.post("/auth/reset-password")
def reset_password(payload: PasswordResetRequest):
    if len(payload.new_password) < 8:
        raise HTTPException(status_code=400, detail="password must be at least 8 characters")
    token_data = store.load(_password_reset_token_key(payload.token), None)
    if not token_data or token_data.get("expires_at", 0) < time.time():
        raise HTTPException(status_code=400, detail="reset link has expired")
    user = _find_user_by_id(token_data["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    salt = secrets.token_hex(16)
    user["password_salt"] = salt
    user["password_hash"] = _password_hash(salt, payload.new_password)
    _replace_user_in_index(user)
    _save_user_record(user)
    store.save(_password_reset_token_key(payload.token), {"used": True, "used_at": utc_now()})
    return {"ok": True, "message": "Password updated. You can sign in now."}


@app.get("/auth/me")
def auth_me(request: Request):
    user = _current_user(request)
    full_user = _find_user_by_id(user["user_id"]) or user
    state = _load_user_state(user["user_id"], full_user)
    return {
        "user": {
            "first_name": full_user["first_name"],
            "last_name": full_user["last_name"],
            "display_name": full_user["display_name"],
            "email": full_user["email"],
            "phone_number": full_user.get("phone_number", ""),
            "is_admin": _is_admin(full_user),
        },
        "state": state,
        "daily_briefing": _build_daily_briefing(state),
    }


@app.get("/reset-password", response_class=HTMLResponse)
def reset_password_page():
    return _html_response(render_reset_password_page())


@app.get("/app/api/bootstrap")
def app_bootstrap(request: Request):
    user = _current_user(request)
    full_user = _find_user_by_id(user["user_id"]) or user
    state = _load_user_state(user["user_id"], full_user)
    return {
        "user": {
            "first_name": full_user["first_name"],
            "last_name": full_user["last_name"],
            "display_name": full_user["display_name"],
            "email": full_user["email"],
            "phone_number": full_user.get("phone_number", ""),
            "is_admin": _is_admin(full_user),
        },
        "state": state,
        "daily_briefing": _build_daily_briefing(state),
    }


@app.post("/app/api/install-link")
def send_install_link(payload: LinkDeliveryRequest, request: Request):
    user = _current_user(request)
    full_user = _find_user_by_id(user["user_id"]) or user
    return _deliver_install_link(full_user, request, payload.channel)


@app.post("/app/api/password-help")
def signed_in_password_help(payload: LinkDeliveryRequest, request: Request):
    user = _current_user(request)
    full_user = _find_user_by_id(user["user_id"]) or user
    return _create_password_reset(full_user, request, payload.channel)


@app.get("/app/api/admin/users")
def admin_users(request: Request):
    user = _current_user(request)
    full_user = _find_user_by_id(user["user_id"]) or user
    _require_admin(full_user)
    users = sorted(_all_users(), key=lambda row: row.get("created_at", ""), reverse=True)
    return {"users": [_admin_user_summary(row) for row in users]}


@app.post("/app/api/admin/users/update")
def admin_update_user(payload: AdminUserUpdateRequest, request: Request):
    user = _current_user(request)
    full_user = _find_user_by_id(user["user_id"]) or user
    _require_admin(full_user)
    target = _find_user_by_id(payload.user_id)
    if not target:
        raise HTTPException(status_code=404, detail="user not found")
    if payload.first_name.strip():
        target["first_name"] = payload.first_name.strip()
    if payload.last_name.strip():
        target["last_name"] = payload.last_name.strip()
    if payload.email.strip():
        target["email"] = payload.email.strip().lower()
    if payload.phone_number.strip():
        target["phone_number"] = _normalize_phone(payload.phone_number)
    target["display_name"] = _compose_display_name(target.get("first_name", ""), target.get("last_name", ""), target.get("email", ""))
    if payload.is_admin is not None:
        target["is_admin"] = payload.is_admin
    if payload.is_disabled is not None:
        target["is_disabled"] = payload.is_disabled
    _replace_user_in_index(target)
    _save_user_record(target)
    state = _load_user_state(target["user_id"], target)
    state["profile"]["first_name"] = target["first_name"]
    state["profile"]["last_name"] = target["last_name"]
    state["profile"]["display_name"] = target["display_name"]
    state["profile"]["email"] = target["email"]
    state["profile"]["phone_number"] = target.get("phone_number", "")
    _save_user_state(target["user_id"], state, target)
    return {"ok": True, "user": _admin_user_summary(target)}


@app.get("/app/api/admin/analytics")
def admin_analytics(request: Request):
    user = _current_user(request)
    full_user = _find_user_by_id(user["user_id"]) or user
    _require_admin(full_user)
    return _analytics_snapshot()


@app.post("/app/api/profile")
def update_profile(payload: ProfileUpdateRequest, request: Request):
    user = _current_user(request)
    users = _load_users()
    for row in users:
        if row["user_id"] == user["user_id"]:
            proposed_email = payload.email.strip().lower()
            if proposed_email != row["email"]:
                existing = _find_user(proposed_email)
                if existing and existing["user_id"] != row["user_id"]:
                    raise HTTPException(status_code=400, detail="email is already registered")
            row["first_name"] = payload.first_name.strip() or row.get("first_name", "")
            row["last_name"] = payload.last_name.strip() or row.get("last_name", "")
            row["email"] = proposed_email
            row["display_name"] = _compose_display_name(row["first_name"], row["last_name"], row["email"])
            row["phone_number"] = _normalize_phone(payload.phone_number) or row.get("phone_number", "")
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
    state["profile"]["first_name"] = user["first_name"]
    state["profile"]["last_name"] = user["last_name"]
    state["profile"]["display_name"] = user["display_name"]
    state["profile"]["email"] = user["email"]
    state["profile"]["phone_number"] = user.get("phone_number", "")
    _save_user_state(user["user_id"], state, user)
    return {
        "ok": True,
        "state": state,
        "user": {
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "display_name": user["display_name"],
            "email": user["email"],
            "phone_number": user.get("phone_number", ""),
        },
        "daily_briefing": _build_daily_briefing(state),
    }


@app.post("/app/api/contacts")
def add_app_contact(payload: AppContactRequest, request: Request):
    user = _current_user(request)
    state = _load_user_state(user["user_id"], user)
    contact = Contact.create(payload.name, payload.phone, payload.notes).__dict__
    contact["phone"] = _normalize_phone(contact["phone"])
    contact["email"] = ""
    contact["shared"] = payload.shared
    _append_contact_if_new(state, contact)
    _save_user_state(user["user_id"], state, user)
    return {"contact": contact, "state": state, "daily_briefing": _build_daily_briefing(state)}


@app.get("/app/api/user-search")
def user_search(q: str, request: Request):
    user = _current_user(request)
    query = q.strip().lower()
    if len(query) < 2:
        return {"users": []}
    normalized_phone = _normalize_phone(query)
    results: list[dict[str, Any]] = []
    for row in _all_users():
        if row.get("user_id") == user["user_id"] or row.get("is_disabled"):
            continue
        search_text = " ".join(
            [
                row.get("display_name", ""),
                row.get("first_name", ""),
                row.get("last_name", ""),
                row.get("email", ""),
                row.get("phone_number", ""),
            ]
        ).lower()
        phone = _normalize_phone(str(row.get("phone_number", "")))
        if query in search_text or (normalized_phone and normalized_phone in phone):
            results.append(_public_user_summary(row))
        if len(results) >= 12:
            break
    return {"users": results}


@app.post("/app/api/contacts/add-user")
def add_user_to_contacts(payload: DirectoryAddRequest, request: Request):
    user = _current_user(request)
    target = _find_user_by_id(payload.user_id)
    if not target or target.get("is_disabled"):
        raise HTTPException(status_code=404, detail="Telefon user not found")
    state = _load_user_state(user["user_id"], user)
    contact = {
        "contact_id": secrets.token_hex(8),
        "linked_user_id": target["user_id"],
        "name": _compose_display_name(target.get("first_name", ""), target.get("last_name", ""), target.get("email", "")),
        "phone": _normalize_phone(str(target.get("phone_number", ""))),
        "email": target.get("email", "").strip().lower(),
        "notes": "Telefon user",
        "shared": False,
    }
    added = _append_contact_if_new(state, contact)
    _save_user_state(user["user_id"], state, user)
    return {"ok": True, "added": added, "state": state, "daily_briefing": _build_daily_briefing(state)}


@app.post("/app/api/contacts/import")
def import_contacts(payload: ContactImportRequest, request: Request):
    user = _current_user(request)
    state = _load_user_state(user["user_id"], user)
    added_count = 0
    for row in payload.contacts:
        name = row.name.strip()
        phone = _normalize_phone(row.phone)
        email = row.email.strip().lower()
        if not name and not phone and not email:
            continue
        added = _append_contact_if_new(
            state,
            {
                "contact_id": secrets.token_hex(8),
                "name": name or email or phone,
                "phone": phone,
                "email": email,
                "notes": row.notes.strip(),
                "shared": row.shared,
            },
        )
        if added:
            added_count += 1
    _save_user_state(user["user_id"], state, user)
    return {"ok": True, "added_count": added_count, "state": state, "daily_briefing": _build_daily_briefing(state)}


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
    state["assistant_history"] = state["assistant_history"][-20:]
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
