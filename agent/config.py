from dotenv import load_dotenv
import os

# Load environment variables from the project root .env file
load_dotenv()

class Config:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY not found in .env")

        # Stable free-tier model for conversational agents
        self.model = "models/gemini-2.0-flash"

config = Config()
