"""
OpenRouter minimal client wrapper.

Expects OPENROUTER_API_KEY in env (or .env loaded by your config)
"""

import os
import requests
import json

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        # pick a reasonable default model; user can override via env
        self.model = os.getenv("OPENROUTER_MODEL", "gpt-4o-mini")  # set a safe default name; change as needed
        self.url = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")

        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY missing in environment")

    def generate(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            # keep default params lightweight
            "max_tokens": 512,
            "temperature": 0.2
        }
        resp = requests.post(self.url, headers=headers, json=data, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"OpenRouter API error: {resp.text}")
        j = resp.json()
        # Expect "choices"[0]["message"]["content"] or choices[0].get("message",{}).get("content")
        try:
            text = j["choices"][0]["message"]["content"]
        except Exception:
            # fallback to other possible shapes
            text = j["choices"][0].get("text") if j.get("choices") else ""
        return text or ""
