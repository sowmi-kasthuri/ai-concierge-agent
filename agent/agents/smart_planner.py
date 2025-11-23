# Path: agent/agents/smart_planner.py
"""
SmartPlanner (Clean + Stable)

Responsibilities:
- Classifies user intent into one of the following actions:
    - answer_directly
    - add_note
    - add_task
    - list_tasks
    - web_search
    - clarify

- Uses GeminiClient for reasoning (LLM-based) if available.
- Falls back to rule-based parsing if LLM fails.

Returns clean JSON dict with at least:
{
    "action": "...",
    "input": "...",
    "reasoning": "..."
}
"""

import json
import logging
from pathlib import Path
from agent.llm.gemini_client import GeminiClient

logger = logging.getLogger(__name__)


def load_planner_prompt() -> str:
    path = Path("agent/prompts/planner_prompt.txt")
    if path.exists():
        return path.read_text(encoding="utf-8")
    return (
        "You are a smart planner. Your job is to classify the user's intent and "
        "return a JSON dict with an action field.\n"
        "Your options: answer_directly, add_note, add_task, list_tasks, web_search, clarify.\n"
        "If unclear → return {\"action\": \"clarify\", \"input\": \"...\"}.\n"
    )


class SmartPlanner:
    def __init__(self, llm=None):
        self.llm = llm or GeminiClient()
        self.prompt_template = load_planner_prompt()

    # -------------------------------------------------------------
    # Main planner call
    # -------------------------------------------------------------
    def decide(self, user_input: str, context: str = "") -> dict:
        """
        Returns a dict:
        { "action": "...", "input": "...", "reasoning": "..." }
        """

        prompt = (
            f"{self.prompt_template}\n\n"
            f"Context: {context or 'None'}\n"
            f"User: {user_input}\n"
            f"Return ONLY VALID JSON.\n"
        )

        try:
            raw = self.llm.generate(prompt)
            clean = raw.strip()

            # Strip code fences if LLM wrapped JSON
            if clean.startswith("```"):
                clean = clean.replace("```json", "").replace("```", "").strip()

            parsed = json.loads(clean)

            if "action" not in parsed:
                raise ValueError("Planner JSON missing 'action'.")

            return parsed

        except Exception as e:
            logger.warning(f"SmartPlanner failed, falling back to rule-based: {e}")
            return self._fallback(user_input)

    # -------------------------------------------------------------
    # Rule-based fallback
    # -------------------------------------------------------------
    def _fallback(self, text: str) -> dict:
        t = text.lower().strip()

        if t.startswith("add note:"):
            return {
                "action": "add_note",
                "input": text.split(":", 1)[1].strip(),
                "reasoning": "Rule-based fallback"
            }

        if t.startswith("add task:"):
            return {
                "action": "add_task",
                "input": text.split(":", 1)[1].strip(),
                "reasoning": "Rule-based fallback"
            }

        if "list tasks" in t or "show tasks" in t:
            return {
                "action": "list_tasks",
                "input": "",
                "reasoning": "Rule-based fallback"
            }

        if t.startswith("search ") or t.startswith("find "):
            return {
                "action": "web_search",
                "input": t.replace("search", "").replace("find", "").strip(),
                "reasoning": "Rule-based fallback"
            }

        # Default
        return {
            "action": "answer_directly",
            "input": text,
            "reasoning": "Fallback: unclear intent"
        }
