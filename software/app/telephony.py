from __future__ import annotations

import subprocess
from typing import Optional


class TelephonyManager:
    def __init__(self, backend: str, modem_tty: str):
        self.backend = backend
        self.modem_tty = modem_tty

    def dial(self, number: str) -> str:
        if self.backend == "modemmanager":
            cmd = ["mmcli", "-m", "0", f"--voice-create-call=number={number}"]
            completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if completed.returncode == 0:
                return completed.stdout.strip()
            return completed.stderr.strip()
        return self._send_at(f"ATD{number};")

    def hangup(self) -> str:
        return self._send_at("ATH")

    def answer(self) -> str:
        return self._send_at("ATA")

    def _send_at(self, command: str) -> str:
        try:
            completed = subprocess.run(
                ["bash", "-lc", f'printf "{command}\\r" > {self.modem_tty}'],
                capture_output=True,
                text=True,
                check=False,
            )
            return completed.stdout.strip() or completed.stderr.strip() or "AT command sent"
        except Exception as exc:
            return f"telephony error: {exc}"

    def last_call_status(self) -> Optional[str]:
        completed = subprocess.run(["mmcli", "-m", "0"], capture_output=True, text=True, check=False)
        if completed.returncode == 0:
            return completed.stdout
        return None
