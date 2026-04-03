from __future__ import annotations

import json
import os
import re
import requests

from shared.models import QueryResult


class CloudOrchestrator:
    def __init__(self, xai_base_url: str, xai_api_key_env: str, model: str):
        self.xai_base_url = xai_base_url
        self.xai_api_key_env = xai_api_key_env
        self.model = model
        self.openrouter_base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.openrouter_model = os.environ.get("OPENROUTER_MODEL", "openrouter/free")
        self.openrouter_api_key_env = os.environ.get("OPENROUTER_API_ENV", "OPENROUTER_API_KEY")
        self.site_url = os.environ.get("EDGE_SITE_URL", "https://telefon-phi.vercel.app")
        self.site_name = os.environ.get("EDGE_SITE_NAME", "Telefon")

    def respond(self, prompt: str, interface_mode: str, context: dict | None = None) -> QueryResult:
        provider = self._active_provider()
        if not provider:
            return self._prototype_fallback(prompt, interface_mode, context)

        try:
            system_prompt = self._system_prompt(context or {})
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]
            if provider == "openrouter":
                response = requests.post(
                    f"{self.openrouter_base_url}/chat/completions",
                    timeout=45,
                    headers={
                        "Authorization": f"Bearer {os.environ.get(self.openrouter_api_key_env, '')}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": self.site_url,
                        "X-Title": self.site_name,
                    },
                    json={
                        "model": self.openrouter_model,
                        "messages": messages,
                        "temperature": 0.4,
                        "response_format": {"type": "json_object"},
                    },
                )
                response.raise_for_status()
                payload = response.json()
                text = payload["choices"][0]["message"]["content"]
                return self._parse_model_payload(text, interface_mode, ["openrouter", self.openrouter_model])

            response = requests.post(
                f"{self.xai_base_url}/chat/completions",
                timeout=45,
                headers={"Authorization": f"Bearer {os.environ.get(self.xai_api_key_env, '')}"},
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.4,
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
            payload = response.json()
            text = payload["choices"][0]["message"]["content"]
            return self._parse_model_payload(text, interface_mode, ["cloud_backend", "strong_model", self.model])
        except Exception:
            result = self._prototype_fallback(prompt, interface_mode, context)
            result.reasoning.append("cloud_error_fallback")
            return result

    def _active_provider(self) -> str | None:
        if os.environ.get(self.openrouter_api_key_env, ""):
            return "openrouter"
        if os.environ.get(self.xai_api_key_env, ""):
            return "xai"
        return None

    def _system_prompt(self, context: dict) -> str:
        profile = context.get("profile", {})
        tools = context.get("tools", [])
        memory_summary = context.get("memory_summary", "No saved memory yet.")
        contacts_summary = context.get("contacts_summary", "No contacts yet.")
        trusted_summary = context.get("trusted_summary", "No trusted helpers yet.")
        history_summary = context.get("history_summary", "No recent assistant history.")
        return (
            "You are Telefon, a personal AI assistant for simplifying digital life. "
            "Be concrete, short, and genuinely useful. "
            "When the user asks how to do something in the app, answer with the exact next steps in the current web app. "
            "When the user asks a general question, answer it directly like a normal assistant. "
            "Use the user's saved profile, memory, contacts, trusted people, and recent assistant history to personalize the answer. "
            "Do not mention internal implementation details. "
            "If a helpful in-app action exists, include it. "
            "Return JSON with keys: text, optional action_label, optional action_url.\n\n"
            f"User profile: {profile}\n"
            f"Saved memory: {memory_summary}\n"
            f"Contacts: {contacts_summary}\n"
            f"Trusted people: {trusted_summary}\n"
            f"Recent history: {history_summary}\n"
            f"Available tools: {', '.join(tools) if tools else 'none'}\n"
            "Known app routes: /app#profile for contacts/profile tools, /download for install flow."
        )

    def _parse_model_payload(self, content: str, interface_mode: str, reasoning: list[str]) -> QueryResult:
        try:
            payload = json.loads(content)
            if isinstance(payload, dict) and payload.get("text"):
                return QueryResult(
                    text=str(payload.get("text", "")).strip(),
                    mode="cloud",
                    interface_mode=interface_mode,
                    reasoning=reasoning,
                    action_url=str(payload.get("action_url")).strip() if payload.get("action_url") else None,
                    action_label=str(payload.get("action_label")).strip() if payload.get("action_label") else None,
                )
        except Exception:
            pass
        return QueryResult(
            text=content.strip(),
            mode="cloud",
            interface_mode=interface_mode,
            reasoning=reasoning + ["unstructured_response"],
        )

    def _prototype_fallback(self, prompt: str, interface_mode: str, context: dict | None = None) -> QueryResult:
        lowered = prompt.lower()
        context = context or {}
        contacts_count = context.get("contacts_count", 0)
        trusted_count = context.get("trusted_count", 0)
        words = set(re.findall(r"[a-z0-9']+", lowered))

        def has_word(*targets: str) -> bool:
            return any(target in words for target in targets)

        if any(token in lowered for token in ["install", "download", "add to home screen", "phone link"]):
            text = (
                "Open the Install section in your account and choose Email me the app. "
                "That sends the phone-friendly link to the same email address you used to sign in."
            )
            reasoning = ["prototype_fallback", "install_help"]
        elif interface_mode == "call" or has_word("call", "phone"):
            text = (
                "I can help place that call. I’ll look up the contact, confirm the right number if needed, "
                "and then hand off to the phone dialer."
            )
            reasoning = ["prototype_fallback", "call_intent"]
        elif interface_mode == "calendar" or has_word("schedule", "meeting", "calendar", "appointment"):
            text = (
                "I can help schedule that. I’ll gather the time, people, and preferences, then create the event "
                "and later this can expand into assistant-to-assistant coordination."
            )
            reasoning = ["prototype_fallback", "calendar_intent"]
        elif interface_mode == "camera" or has_word("camera", "photo", "scan", "image", "document", "picture"):
            text = "I can help analyze a photo or document and explain it in simple language."
            reasoning = ["prototype_fallback", "camera_intent"]
        elif interface_mode == "memory" or has_word("remember", "memory"):
            text = "I can store that in your personal memory so it helps with future suggestions and actions."
            reasoning = ["prototype_fallback", "memory_intent"]
        else:
            web_answer = self._free_web_answer(prompt)
            if web_answer:
                return QueryResult(
                    text=web_answer,
                    mode="cloud-free-web",
                    interface_mode=interface_mode,
                    reasoning=["prototype_fallback", "free_web_answer"],
                )
            text = (
                f"I can help with general questions, calls, contacts, planning, and memory. "
                f"Right now you have {contacts_count} contacts and {trusted_count} trusted helpers saved."
            )
            reasoning = ["prototype_fallback", "general_assistant"]

        return QueryResult(
            text=text,
            mode="cloud-prototype",
            interface_mode=interface_mode,
            reasoning=reasoning + ["missing_xai_api_key"],
        )

    def _free_web_answer(self, prompt: str) -> str | None:
        try:
            ddg = requests.get(
                "https://api.duckduckgo.com/",
                timeout=12,
                params={"q": prompt, "format": "json", "no_html": 1, "no_redirect": 1},
                headers={"User-Agent": "Telefon/1.0"},
            )
            ddg.raise_for_status()
            payload = ddg.json()
            abstract = (payload.get("AbstractText") or payload.get("Answer") or "").strip()
            if abstract:
                return abstract
            related = payload.get("RelatedTopics") or []
            for item in related:
                if isinstance(item, dict) and item.get("Text"):
                    return str(item["Text"]).strip()
        except Exception:
            pass

        try:
            search = requests.get(
                "https://en.wikipedia.org/w/api.php",
                timeout=12,
                params={
                    "action": "opensearch",
                    "search": prompt,
                    "limit": 1,
                    "namespace": 0,
                    "format": "json",
                },
                headers={"User-Agent": "Telefon/1.0"},
            )
            search.raise_for_status()
            payload = search.json()
            titles = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
            if not titles:
                return None
            title = titles[0]
            summary = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(title)}",
                timeout=12,
                headers={"User-Agent": "Telefon/1.0"},
            )
            summary.raise_for_status()
            page = summary.json()
            extract = (page.get("extract") or "").strip()
            if extract:
                return extract
        except Exception:
            return None
        return None
