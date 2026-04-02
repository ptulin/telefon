from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk

from desktop_app.client import BackendClient


class DesktopApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.client = BackendClient(os.environ.get("EDGE_BACKEND_URL", "https://telefon-phi.vercel.app"))
        self.mode = tk.StringVar(value="chat")
        self.prompt = tk.StringVar()

        self.root.title("Personal AI")
        self.root.geometry("980x720")

        toolbar = ttk.Frame(root, padding=12)
        toolbar.pack(fill="x")
        ttk.Label(toolbar, text="Mode").pack(side="left")
        ttk.Combobox(
            toolbar,
            textvariable=self.mode,
            values=["chat", "memory", "phone", "documents", "camera"],
            state="readonly",
            width=14,
        ).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Refresh Profile", command=self.refresh_profile).pack(side="left", padx=8)

        body = ttk.Panedwindow(root, orient="horizontal")
        body.pack(fill="both", expand=True)

        left = ttk.Frame(body, padding=12)
        right = ttk.Frame(body, padding=12)
        body.add(left, weight=3)
        body.add(right, weight=2)

        ttk.Label(left, text="Unified AI Interface").pack(anchor="w")
        ttk.Entry(left, textvariable=self.prompt).pack(fill="x", pady=8)
        ttk.Button(left, text="Send", command=self.send).pack(anchor="w")
        self.output = tk.Text(left, wrap="word")
        self.output.pack(fill="both", expand=True, pady=12)

        ttk.Label(right, text="Personal Memory Snapshot").pack(anchor="w")
        self.profile_box = tk.Text(right, wrap="word", width=36)
        self.profile_box.pack(fill="both", expand=True)

        self.refresh_profile()

    def send(self):
        result = self.client.query(self.prompt.get(), self.mode.get())
        self.output.insert("end", f"[{result['mode']}/{result['interface_mode']}] {result['text']}\n\n")
        self.output.see("end")

    def refresh_profile(self):
        profile = self.client.profile()
        contacts = self.client.contacts()
        self.profile_box.delete("1.0", "end")
        self.profile_box.insert("end", "Profile\n")
        for key, items in profile.items():
            self.profile_box.insert("end", f"\n{key}:\n")
            for item in items[-5:]:
                self.profile_box.insert("end", f"- {item.get('summary', '')}\n")
        self.profile_box.insert("end", "\nContacts:\n")
        for contact in contacts.get("contacts", [])[-10:]:
            self.profile_box.insert("end", f"- {contact.get('name')} {contact.get('phone')}\n")


def main():
    root = tk.Tk()
    DesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
