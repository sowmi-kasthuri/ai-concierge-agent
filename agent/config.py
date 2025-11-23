from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    def __init__(self):
        # --- Planner LLM (Gemini) ---
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash")
        if not self.gemini_key:
            raise RuntimeError("GEMINI_API_KEY missing in .env (required for SmartPlanner)")

        # --- Answer Engine (OpenRouter) ---
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-70b-instruct")
        if not self.openrouter_key:
            raise RuntimeError("OPENROUTER_API_KEY missing in .env (required for answer_directly)")

        # --- Explicit provider settings ---
        self.provider = "dual"            # planner=gemini, answer=openrouter

config = Config()
