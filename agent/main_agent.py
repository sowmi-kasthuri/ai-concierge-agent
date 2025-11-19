from google import genai
from agent.config import config


class ConciergeAgent:
    def __init__(self):
        # Initialize Gemini client
        self.client = genai.Client(api_key=config.api_key)

        # Session memory (lives only during this run)
        self.session_memory = []

    def ask(self, message: str) -> str:
        """Send a message to Gemini and return the response."""

        from agent.memory.memory_tool import get_facts, add_fact


        # Save user message to session memory
        self.session_memory.append({"user": message})

        # Load persistent memory
        facts = get_facts()
        
        try:
            response = self.client.models.generate_content(
                model=config.model,
                contents=[
                    {
                        "role": "user",
                        "parts": [{"text": f"Persistent facts: {facts}"}]
                    },
                    {
                        "role": "user",
                        "parts": [{"text": message}]
                    }
                ]
            )
            # Ask Gemini if the user's message contains a fact we should store
            memory_query = f"""
            User said: "{message}"
            Extract only if this message contains a stable user preference, habit, personal detail, or long-term information.

            If yes, return the fact clearly.
            If no, return "NO_FACT".
            """

            memory_response = self.client.models.generate_content(
                model=config.model,
                contents=[
                    {
                        "role": "user",
                        "parts": [{"text": memory_query}]
                    }
                ]
            )

            memory_text = memory_response.text.strip()

            if memory_text != "NO_FACT" and len(memory_text) > 0:
                add_fact(memory_text)

            # Save agent reply to session memory
            self.session_memory.append({"agent": response.text})

            return response.text

        except Exception as e:
            return f"[Agent Error] {e}"
