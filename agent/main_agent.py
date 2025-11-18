from google import genai
from agent.config import config

class ConciergeAgent:
    def __init__(self):
        # Initialize Gemini client
        self.client = genai.Client(api_key=config.api_key)

    def ask(self, message: str) -> str:
        """Send a message to Gemini and return the response."""
        try:
            response = self.client.models.generate_content(
                model=config.model,
                contents=message
            )
            return response.text
        except Exception as e:
            return f"[Agent Error] {e}"
