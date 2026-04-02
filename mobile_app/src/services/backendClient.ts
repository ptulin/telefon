const BASE_URL =
  process.env.EXPO_PUBLIC_BACKEND_URL ||
  "https://telefon-phi.vercel.app";

export const backendClient = {
  async query(prompt: string, preferredMode: string) {
    const response = await fetch(`${BASE_URL}/v1/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        prompt,
        interface_mode: preferredMode,
        source: "mobile"
      })
    });

    if (!response.ok) {
      throw new Error(`Backend query failed: ${response.status}`);
    }

    return response.json();
  }
};
