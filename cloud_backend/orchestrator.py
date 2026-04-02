from __future__ import annotations

import os
import requests

from shared.models import QueryResult


class CloudOrchestrator:
    def __init__(self, xai_base_url: str, xai_api_key_env: str, model: str):
        self.xai_base_url = xai_base_url
        self.xai_api_key_env = xai_api_key_env
        self.model = model

    def respond(self, prompt: str, interface_mode: str) -> QueryResult:
        api_key = os.environ.get(self.xai_api_key_env, "")
        if not api_key:
            return self._prototype_fallback(prompt, interface_mode)

        response = requests.post(
            f"{self.xai_base_url}/chat/completions",
            timeout=45,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are the canonical personal AI for a user across an edge device and desktop app. "
                            "Adapt to phone, camera, memory, or document contexts and answer naturally."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            },
        )
        response.raise_for_status()
        payload = response.json()
        text = payload["choices"][0]["message"]["content"]
        return QueryResult(
            text=text,
            mode="cloud",
            interface_mode=interface_mode,
            reasoning=["cloud_backend", "strong_model"],
        )

    def _prototype_fallback(self, prompt: str, interface_mode: str) -> QueryResult:
        lowered = prompt.lower()
        if interface_mode == "call" or "call" in lowered or "phone" in lowered:
            text = (
                "I can help place that call. I’ll look up the contact, confirm the right number if needed, "
                "and then hand off to the phone dialer."
            )
            reasoning = ["prototype_fallback", "call_intent"]
        elif interface_mode == "calendar" or any(token in lowered for token in ["schedule", "meeting", "calendar", "appointment"]):
            text = (
                "I can help schedule that. I’ll gather the time, people, and preferences, then create the event "
                "and later this can expand into assistant-to-assistant coordination."
            )
            reasoning = ["prototype_fallback", "calendar_intent"]
        elif interface_mode == "camera" or any(token in lowered for token in ["camera", "photo", "scan", "image"]):
            text = "I can help analyze a photo or document and explain it in simple language."
            reasoning = ["prototype_fallback", "camera_intent"]
        elif interface_mode == "memory" or "remember" in lowered:
            text = "I can store that in your personal memory so it helps with future suggestions and actions."
            reasoning = ["prototype_fallback", "memory_intent"]
        else:
            text = (
                "I’m your personal AI assistant. I can help with calls, calendar events, reminders, "
                "documents, camera help, and memory."
            )
            reasoning = ["prototype_fallback", "general_assistant"]

        return QueryResult(
            text=text,
            mode="cloud-prototype",
            interface_mode=interface_mode,
            reasoning=reasoning + ["missing_xai_api_key"],
        )
