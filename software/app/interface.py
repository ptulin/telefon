from __future__ import annotations


class AdaptiveInterface:
    def resolve_mode(self, prompt: str) -> str:
        lowered = prompt.lower()
        if any(token in lowered for token in ["call", "dial", "phone", "contact"]):
            return "phone"
        if any(token in lowered for token in ["camera", "photo", "ocr", "image", "scan"]):
            return "camera"
        if any(token in lowered for token in ["document", "pdf", "file", "upload"]):
            return "documents"
        if any(token in lowered for token in ["remember", "memory", "preference", "habit", "relationship"]):
            return "memory"
        return "chat"
