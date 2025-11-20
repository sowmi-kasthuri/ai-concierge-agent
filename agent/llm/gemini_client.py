# agent/llm/gemini_client.py
import google.generativeai as genai
from agent.config import config  # <-- correct import path

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=config.api_key)
        self.model = genai.GenerativeModel(config.model)

    def generate(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text
