from __future__ import annotations

from software.app.config import load_settings
from software.app.connectivity import ConnectivityMonitor


def main():
    settings = load_settings()
    monitor = ConnectivityMonitor(
        settings.raw["network"]["connectivity_check_url"],
        settings.raw["network"]["offline_after_failures"],
    )
    monitor.loop(interval=10.0)


if __name__ == "__main__":
    main()
