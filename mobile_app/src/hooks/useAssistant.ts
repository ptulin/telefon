import { useState } from "react";

import { backendClient } from "@/services/backendClient";

type PromptInput = {
  prompt: string;
  preferredMode: string;
};

export function useAssistant() {
  const [reply, setReply] = useState("");
  const [status, setStatus] = useState("Cloud-first assistant ready");

  async function sendPrompt({ prompt, preferredMode }: PromptInput) {
    if (!prompt.trim()) {
      return;
    }

    setStatus("Thinking...");
    try {
      const result = await backendClient.query(prompt, preferredMode);
      setReply(`[${result.mode}/${result.interface_mode}] ${result.text}`);
      setStatus(result.mode === "cloud" ? "Using cloud intelligence" : "Using local fallback");
    } catch (error) {
      setReply("I could not reach the backend just now. Offline queue and local fallback belong here next.");
      setStatus("Backend unavailable");
    }
  }

  return { reply, sendPrompt, status };
}
