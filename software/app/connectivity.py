from __future__ import annotations

import requests
import time


class ConnectivityMonitor:
    def __init__(self, check_url: str, failure_threshold: int = 3, timeout: float = 3.0):
        self.check_url = check_url
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self._failures = 0
        self.online = False

    def probe(self) -> bool:
        try:
            response = requests.get(self.check_url, timeout=self.timeout)
            self.online = response.status_code < 500
            self._failures = 0
        except requests.RequestException:
            self._failures += 1
            if self._failures >= self.failure_threshold:
                self.online = False
        return self.online

    def loop(self, interval: float = 10.0):
        while True:
            self.probe()
            time.sleep(interval)
