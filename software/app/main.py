from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, render_template, request

from .address_book import AddressBook
from .camera import CameraManager
from .config import load_settings
from .connectivity import ConnectivityMonitor
from .llm_router import HybridRouter
from .memory import MemoryVault
from .telephony import TelephonyManager
from .uploads import UploadManager
from .voice import VoiceIO


settings = load_settings()
app = Flask(__name__, template_folder="../ui/templates", static_folder="../ui/static")
connectivity = ConnectivityMonitor(
    settings.raw["network"]["connectivity_check_url"],
    settings.raw["network"]["offline_after_failures"],
)
memory = MemoryVault(Path(settings.storage_root) / "memory")
router = HybridRouter(settings.raw, connectivity)
telephony = TelephonyManager(
    settings.raw["telephony"]["dialer_backend"],
    settings.raw["telephony"]["modem_tty"],
)
voice = VoiceIO()
uploads = UploadManager(Path(settings.raw["uploads"]["root"]))
camera = CameraManager(Path(settings.raw["uploads"]["root"]))
address_book = AddressBook(Path(settings.storage_root) / "contacts")


@app.route("/")
def index():
    connectivity.probe()
    return render_template("index.html", online=connectivity.online)


@app.route("/api/chat", methods=["POST"])
def chat():
    prompt = request.json["prompt"]
    response = router.generate(
        prompt,
        tools=["web", "memory", "telephony", "vision", "documents"],
        preferred_mode=request.json.get("preferred_mode"),
    )
    mode = response.get("interface_mode", "chat")
    memory.add_conversation("user", prompt, mode)
    memory.add_conversation("assistant", response["text"], mode)
    return jsonify(response)


@app.route("/api/memory/facts", methods=["POST"])
def add_memory():
    payload = request.json
    item = memory.add_fact(
        payload["category"],
        payload["summary"],
        payload.get("detail", payload["summary"]),
        payload.get("source", "device"),
    )
    return jsonify(item)


@app.route("/api/memory/profile")
def profile():
    return jsonify(memory.profile())


@app.route("/api/status")
def status():
    connectivity.probe()
    return jsonify({"online": connectivity.online, "routing_mode": settings.raw["models"]["routing_mode"]})


@app.route("/api/call", methods=["POST"])
def place_call():
    number = request.json.get("number", "")
    if not number and request.json.get("contact_query"):
        contact = address_book.match(request.json["contact_query"])
        if contact:
            number = contact["phone"]
    result = telephony.dial(number)
    return jsonify({"result": result, "number": number})


@app.route("/api/contacts", methods=["GET", "POST"])
def contacts():
    if request.method == "POST":
        contact = address_book.add(request.json["name"], request.json["phone"], request.json.get("notes", ""))
        return jsonify(contact)
    return jsonify({"contacts": address_book.all()})


@app.route("/api/interface-state")
def interface_state():
    return jsonify(
        {
            "available_modes": ["chat", "phone", "camera", "documents", "memory"],
            "voice_control": True,
            "touch_control": True,
        }
    )


@app.route("/api/camera/analyze", methods=["POST"])
def analyze_camera():
    prompt = request.json.get("prompt", "Describe the current scene")
    return jsonify(camera.analyze_stub(prompt))


@app.route("/api/uploads/document", methods=["POST"])
def upload_document():
    source_path = Path(request.json["path"])
    record = uploads.add_document(source_path, request.json.get("summary", "Queued document for AI understanding"))
    return jsonify(record)


@app.route("/api/uploads/photo", methods=["POST"])
def upload_photo():
    source_path = Path(request.json["path"])
    record = camera.import_photo(source_path, request.json.get("summary", "Queued photo for AI understanding"))
    uploads.add_photo_record(record)
    return jsonify(record)


@app.route("/api/speak", methods=["POST"])
def speak():
    voice.speak(request.json["text"])
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=settings.ui_port, debug=False)
