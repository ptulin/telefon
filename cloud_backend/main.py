from __future__ import annotations

from pathlib import Path
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
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


@app.get("/", response_class=HTMLResponse)
def root():
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Personal AI Phone</title>
  <style>
    :root {
      --bg: #0b1114;
      --panel: #142027;
      --panel-2: #1a2932;
      --text: #eef6f7;
      --muted: #9db0b7;
      --accent: #6cd7ab;
      --accent-2: #57a8ff;
      --border: rgba(255,255,255,0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, sans-serif;
      background:
        radial-gradient(circle at top, rgba(72,136,190,0.20), transparent 32%),
        radial-gradient(circle at 80% 20%, rgba(108,215,171,0.14), transparent 24%),
        var(--bg);
      color: var(--text);
    }
    .shell {
      max-width: 1120px;
      margin: 0 auto;
      padding: 28px 18px 44px;
      display: grid;
      gap: 18px;
    }
    .hero, .panel {
      background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
      border: 1px solid var(--border);
      border-radius: 24px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.28);
    }
    .hero {
      padding: 26px;
      display: grid;
      gap: 12px;
    }
    h1 {
      margin: 0;
      font-size: clamp(2rem, 4vw, 3.2rem);
      line-height: 1;
    }
    .sub {
      color: var(--muted);
      max-width: 760px;
      line-height: 1.5;
      font-size: 1.03rem;
    }
    .badge-row, .chip-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }
    .badge, .chip {
      border-radius: 999px;
      padding: 10px 14px;
      font-size: 0.94rem;
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.03);
    }
    .badge strong { color: var(--accent); }
    .layout {
      display: grid;
      grid-template-columns: 1.35fr 0.85fr;
      gap: 18px;
    }
    .panel {
      padding: 18px;
      display: grid;
      gap: 14px;
    }
    .panel h2 {
      margin: 0;
      font-size: 1.15rem;
    }
    .muted { color: var(--muted); }
    .input, textarea, button {
      width: 100%;
      border-radius: 16px;
      border: 1px solid var(--border);
      font: inherit;
    }
    .input, textarea {
      background: rgba(0,0,0,0.28);
      color: var(--text);
      padding: 14px;
    }
    textarea {
      min-height: 132px;
      resize: vertical;
    }
    button {
      background: linear-gradient(135deg, var(--accent), var(--accent-2));
      color: #071317;
      font-weight: 700;
      padding: 14px 16px;
      cursor: pointer;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }
    .card {
      background: var(--panel-2);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 14px;
      min-height: 120px;
    }
    .card h3 {
      margin: 0 0 8px;
      font-size: 1rem;
    }
    pre {
      white-space: pre-wrap;
      margin: 0;
      color: var(--muted);
      line-height: 1.5;
    }
    .contact {
      padding: 10px 0;
      border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .contact:last-child { border-bottom: 0; }
    @media (max-width: 860px) {
      .layout { grid-template-columns: 1fr; }
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div class="badge-row">
        <div class="badge"><strong>Live prototype</strong> smartphone-first AI operating layer</div>
        <div class="badge">Cloud backend on Vercel</div>
        <div class="badge">Hosted state on Supabase</div>
      </div>
      <h1>Personal AI Phone</h1>
      <div class="sub">
        A simplified AI interface for calling people, planning the day, remembering important details,
        understanding documents and photos, and evolving toward future assistant-to-assistant workflows.
      </div>
      <div class="chip-row">
        <div class="chip">Talk</div>
        <div class="chip">Call</div>
        <div class="chip">Calendar</div>
        <div class="chip">Camera</div>
        <div class="chip">Documents</div>
        <div class="chip">Memory</div>
      </div>
    </section>

    <section class="layout">
      <div class="panel">
        <h2>Ask the Assistant</h2>
        <div class="muted">Try: “Call my daughter”, “Schedule lunch with Alex next Tuesday”, or “Remember that I prefer large text and voice guidance.”</div>
        <select id="mode" class="input">
          <option value="talk">Talk</option>
          <option value="call">Call</option>
          <option value="calendar">Calendar</option>
          <option value="camera">Camera</option>
          <option value="documents">Documents</option>
          <option value="memory">Memory</option>
        </select>
        <textarea id="prompt" placeholder="How can I help you today?"></textarea>
        <button onclick="askAssistant()">Ask AI</button>
        <div class="card">
          <h3>Reply</h3>
          <pre id="reply">Nothing yet.</pre>
        </div>
      </div>

      <div class="panel">
        <h2>Live Profile Snapshot</h2>
        <div class="grid">
          <div class="card">
            <h3>Preferences</h3>
            <pre id="preferences">Loading...</pre>
          </div>
          <div class="card">
            <h3>Contacts</h3>
            <div id="contacts" class="muted">Loading...</div>
          </div>
          <div class="card">
            <h3>What This Demo Shows</h3>
            <pre>Hosted AI backend
Persistent memory facts
Address book state
Sync-ready data model
Prototype assistant responses</pre>
          </div>
          <div class="card">
            <h3>Next Device Step</h3>
            <pre>Connect the same backend to the mobile app for contacts, calls, calendar, camera, and memory flows.</pre>
          </div>
        </div>
      </div>
    </section>
  </main>

  <script>
    async function loadSidebar() {
      const profile = await fetch('/v1/profile').then(r => r.json());
      const contacts = await fetch('/v1/address-book').then(r => r.json());
      const pref = (profile.preferences || []).map(p => '- ' + p.summary).join('\\n') || 'No stored preferences yet.';
      document.getElementById('preferences').textContent = pref;
      const contactsEl = document.getElementById('contacts');
      contactsEl.innerHTML = '';
      const list = contacts.contacts || [];
      if (!list.length) {
        contactsEl.textContent = 'No contacts saved yet.';
        return;
      }
      for (const contact of list) {
        const div = document.createElement('div');
        div.className = 'contact';
        div.innerHTML = '<strong>' + contact.name + '</strong><br><span class="muted">' + contact.phone + '</span>';
        contactsEl.appendChild(div);
      }
    }

    async function askAssistant() {
      const prompt = document.getElementById('prompt').value;
      const interface_mode = document.getElementById('mode').value;
      const reply = document.getElementById('reply');
      reply.textContent = 'Thinking...';
      const res = await fetch('/v1/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, interface_mode, source: 'web-demo' })
      });
      const data = await res.json();
      reply.textContent = '[' + data.mode + '/' + data.interface_mode + '] ' + data.text;
      loadSidebar();
    }

    loadSidebar();
  </script>
</body>
</html>
    """


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
