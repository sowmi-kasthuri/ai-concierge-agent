import os
import requests
from agent.config import config   # ensures env loaded


class OpenRouterClient:
    """
    Lightweight wrapper for OpenRouter's Chat Completions API.
    """

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL", "qwen2.5-72b-instruct")

        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY missing in .env")

        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def generate(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://yourproject.example",  # Optional
            "X-Title": "ConciergeAgent",                    # Optional
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(self.url, json=data, headers=headers)

        if response.status_code != 200:
            raise RuntimeError(f"OpenRouter API error: {response.text}")

        return response.json()["choices"][0]["message"]["content"]
