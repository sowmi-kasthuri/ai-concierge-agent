# Path: agent/llm/gemini_client.py
"""
Unified Gemini/OpenRouter LLM wrapper.

Uses config.py to decide:
- provider = "gemini" → use google genai
- provider = "openrouter" → use OpenRouter
- provider = "dual" → try Gemini first, fallback to OpenRouter

Exposes:
    generate(prompt: str) -> str
"""

import logging
from agent.config import config

logger = logging.getLogger(__name__)

# Try importing google.genai
try:
    import google.genai as genai
    GENAI_AVAILABLE = True
except Exception:
    GENAI_AVAILABLE = False


from agent.llm.openrouter_client import OpenRouterClient


class GeminiClient:
    def __init__(self):
        self.provider = config.provider  # gemini / openrouter / dual
        self.gemini_key = config.gemini_key
        self.gemini_model = config.gemini_model
        self.or_key = config.openrouter_key
        self.or_model = config.openrouter_model

        self.client = None
        self.mode = None

        # ----------------------------
        # Decide which engine to activate
        # ----------------------------

        if self.provider == "gemini":
            self._init_gemini(require_key=True)

        elif self.provider == "openrouter":
            self._init_openrouter(require_key=True)

        elif self.provider == "dual":
            # try Gemini first → fallback to OpenRouter
            if self._init_gemini(require_key=False):
                pass
            else:
                self._init_openrouter(require_key=True)

        else:
            raise RuntimeError(f"Unknown provider: {self.provider}")

    # ----------------------------------------------------
    # INIT HELPERS
    # ----------------------------------------------------
    def _init_gemini(self, require_key: bool):
        if not GENAI_AVAILABLE:
            if require_key:
                raise RuntimeError("google.genai not installed")
            return False

        if not self.gemini_key:
            if require_key:
                raise RuntimeError("GEMINI_API_KEY missing in .env")
            return False

        try:
            self.client = genai.Client(api_key=self.gemini_key)
            self.mode = "gemini"
            return True
        except Exception as e:
            logger.warning(f"Gemini init failed: {e}")
            if require_key:
                raise
            return False

    def _init_openrouter(self, require_key: bool):
        if not self.or_key:
            if require_key:
                raise RuntimeError("OPENROUTER_API_KEY missing in .env")
            return False

        try:
            self.client = OpenRouterClient()
            self.mode = "openrouter"
            return True
        except Exception as e:
            logger.error(f"OpenRouter init failed: {e}")
            if require_key:
                raise
            return False

    # ----------------------------------------------------
    # GENERATE
    # ----------------------------------------------------
    def generate(self, prompt: str) -> str:
        prompt = prompt or ""

        # ------------------
        # GEMINI MODE
        # ------------------
        if self.mode == "gemini":
            try:
                response = self.client.models.generate_content(
                    model=self.gemini_model,
                    contents=[{"parts": [{"text": prompt}]}]
                )
                return response.text
            except Exception as e:
                logger.error(f"Gemini generate failed: {e}")

                # fallback if dual
                if self.provider == "dual" and self.or_key:
                    self._init_openrouter(require_key=True)
                    return self.client.generate(prompt)

                raise

        # ------------------
        # OPENROUTER MODE
        # ------------------
        elif self.mode == "openrouter":
            return self.client.generate(prompt)

        else:
            raise RuntimeError("GeminiClient: no active mode")
