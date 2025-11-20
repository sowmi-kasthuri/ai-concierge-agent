# agent/tools/config.py
from dotenv import load_dotenv
import os

# Load environment variables from the project root .env file
load_dotenv()

class Config:
    def __init__(self):
        # required
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY not found in .env")

        # model pulled from env, with a sensible default
        self.model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

config = Config()
