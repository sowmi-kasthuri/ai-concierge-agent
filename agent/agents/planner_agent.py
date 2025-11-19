"""
PlannerAgent for Day 4.
- Default: LocalFallbackClient (rule-based, offline, fast)
- Optional: GeminiClient (real LLM planning)
Produces: {action, input, reasoning}
"""

import json
import re
from typing import Any, Dict, Optional

ALLOWED_ACTIONS = {"add_note", "add_task", "list_tasks", "web_search", "clarify"}


# ---------------------------
# Client Interfaces
# ---------------------------

class GeminiClientInterface:
    def generate_text(self, prompt: str) -> str:
        raise NotImplementedError


class LocalFallbackClient(GeminiClientInterface):
    """Simple offline rule-based planner."""

    def generate_text(self, prompt: str) -> str:
        m = re.search(r"USER_QUERY:\s*(.*)$", prompt, re.IGNORECASE)
        q = (m.group(1).strip() if m else prompt).strip()
        low = q.lower()

        # Add note
        if re.match(r"^(add\s+(a\s+)??note\b|note\b)", low):
            content = re.sub(r'^(add\s+(a\s+)?note:?\s*|note:?\s*)', '', q, flags=re.I).strip()
            return json.dumps({
                "action": "add_note",
                "input": content or "Untitled note",
                "reasoning": "Add note detected."
            })

        # Add task
        if re.match(r"^(add\s+(a\s+)?task\b|task\b)", low):
            content = re.sub(r'^(add\s+(a\s+)?task:?\s*|task:?\s*)', '', q, flags=re.I).strip()
            return json.dumps({
                "action": "add_task",
                "input": content or "Untitled task",
                "reasoning": "Add task detected."
            })

        # List tasks
        if re.search(r'\b(show my tasks|list tasks|list my tasks|show tasks)\b', low):
            return json.dumps({
                "action": "list_tasks",
                "input": "",
                "reasoning": "User asked to see tasks."
            })

        # Web search
        if re.match(r"^(search|find|look up)", low) or "search for" in low:
            content = re.sub(r'^(search\s+for|search|find|look up)\s*', '', q, flags=re.I).strip()
            return json.dumps({
                "action": "web_search",
                "input": content or q,
                "reasoning": "Search requested."
            })

        # Clarify
        return json.dumps({
            "action": "clarify",
            "input": q,
            "reasoning": "Ambiguous — ask for clarification."
        })


class GeminiClient(GeminiClientInterface):
    """
    Minimal Gemini wrapper (optional).
    Requires:
      pip install google-genai
      export GOOGLE_API_KEY=your_key
    """
    def __init__(self, model: str = "gemini-1.5-pro"):
        try:
            from google import genai
        except ImportError as e:
            raise ImportError("Install google-genai: pip install google-genai") from e

        import os
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing GOOGLE_API_KEY environment variable")

        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate_text(self, prompt: str) -> str:
        resp = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        # Most SDK versions expose resp.text
        return getattr(resp, "text", str(resp))


# ---------------------------
# Planner Agent
# ---------------------------

class PlannerAgent:
    def __init__(self, client: Optional[GeminiClientInterface] = None, enable_gemini: bool = False):
        if enable_gemini:
            self.client = GeminiClient()
        else:
            self.client = client or LocalFallbackClient()

        self.system_prompt = (
            "You are a planner. Output ONLY a JSON object with keys: action, input, reasoning.\n"
            "Allowed actions: add_note, add_task, list_tasks, web_search, clarify\n\n"
            "USER_QUERY: {query}\n"
        )

    # ---------------------------

    def _parse(self, raw: str) -> Dict[str, Any]:
        try:
            return json.loads(raw.strip())
        except Exception:
            m = re.search(r"(\{.*\})", raw, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group(1))
                except Exception:
                    pass
        return {"action": "clarify", "input": raw[:300], "reasoning": "Could not parse planner output."}

    def _validate(self, plan: Dict[str, Any]) -> bool:
        if not {"action", "input", "reasoning"} <= plan.keys():
            return False
        if plan["action"] not in ALLOWED_ACTIONS:
            return False
        return isinstance(plan["input"], str) and isinstance(plan["reasoning"], str)

    # ---------------------------

    def plan(self, user_query: str, use_model: bool = False):
        prompt = self.system_prompt.format(query=user_query)
        raw = self.client.generate_text(prompt)
        plan = self._parse(raw)

        if not self._validate(plan):
            return {"action": "clarify", "input": user_query, "reasoning": "Planner returned invalid plan."}

        return plan


# ---------------------------
# Manual test
# ---------------------------

if __name__ == "__main__":
    p = PlannerAgent()
    tests = [
        "Add a note: Buy milk and eggs",
        "Add task: Prepare slides",
        "Show my tasks",
        "Search for cheapest milk near me",
        "Remind me to call Mom tomorrow at 6pm"
    ]
    for t in tests:
        print("QUERY:", t)
        print("PLAN:", json.dumps(p.plan(t), indent=2))
        print("---")
