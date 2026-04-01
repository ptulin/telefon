from __future__ import annotations

import pyttsx3


class VoiceIO:
    def __init__(self):
        self.engine = pyttsx3.init()

    def transcribe_once(self) -> str:
        # Stub for prototype integration. Replace with streaming Vosk / Whisper path.
        return ""

    def speak(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()
