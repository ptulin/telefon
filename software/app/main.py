from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, render_template, request

from .config import load_settings
from .connectivity import ConnectivityMonitor
from .llm_router import HybridRouter
from .memory import MemoryVault
from .telephony import TelephonyManager
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


@app.route("/")
def index():
    connectivity.probe()
    return render_template("index.html", online=connectivity.online)


@app.route("/api/chat", methods=["POST"])
def chat():
    prompt = request.json["prompt"]
    response = router.generate(prompt, tools=["web", "memory", "telephony"])
    memory.add(f"Q: {prompt}\nA: {response['text']}")
    return jsonify(response)


@app.route("/api/memory", methods=["POST"])
def add_memory():
    item = memory.add(request.json["text"])
    return jsonify(item.__dict__)


@app.route("/api/status")
def status():
    connectivity.probe()
    return jsonify({"online": connectivity.online})


@app.route("/api/call", methods=["POST"])
def place_call():
    result = telephony.dial(request.json["number"])
    return jsonify({"result": result})


@app.route("/api/speak", methods=["POST"])
def speak():
    voice.speak(request.json["text"])
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=settings.ui_port, debug=False)
