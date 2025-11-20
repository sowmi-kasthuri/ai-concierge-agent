import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_planner_prompt():
    path = Path("agent/prompts/planner_prompt.txt")
    return path.read_text(encoding="utf-8")


class SmartPlanner:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = load_planner_prompt()

    def decide(self, user_input: str, context: str = "") -> dict:

        final_prompt = (
            self.prompt
            + "\n\nRecent Conversation Context:\n"
            + (context or "None")
            + "\n\nUser: " + user_input
            + "\n\nReturn ONLY valid JSON."
        )

        try:
            response = self.llm.generate(final_prompt)
            clean = response.strip()

            if clean.startswith("```"):
                clean = clean.replace("```json", "").replace("```", "").strip()

            return json.loads(clean)

        except Exception:
            return {
                "action": "clarify",
                "reason": "Planner error — need clarification"
            }
