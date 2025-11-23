# Path: agent/agents/worker_agent.py
"""
WorkerAgent — executes actions decided by the SmartPlanner.

Supported actions:
- answer_directly  (uses GeminiClient which may fallback to OpenRouter)
- add_note         (delegates to NotesEngine.add_note_raw)
- add_task
- list_tasks
- list_notes       (delegates to NotesEngine.list_notes)
- web_search       (placeholder)
- clarify

Return format (successful):
    {"status": "ok", "action": "<action>", "output": <value>}

Return format (error):
    {"status": "error", "error": "<message>"}
"""

import json
import os
import logging
from typing import Any, Dict, Callable

from agent.notes_engine import NotesEngine
from agent.llm.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

# memory file base (used by tasks; notes handled by NotesEngine)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASK_STORE = os.path.join(BASE_DIR, "memory", "memory_store.json")


def _load_task_store() -> Dict[str, Any]:
    # Ensure file exists and has tasks list
    if not os.path.exists(os.path.dirname(TASK_STORE)):
        os.makedirs(os.path.dirname(TASK_STORE), exist_ok=True)
    if not os.path.exists(TASK_STORE):
        with open(TASK_STORE, "w", encoding="utf-8") as f:
            json.dump({"notes": [], "tasks": []}, f, indent=2, ensure_ascii=False)
    try:
        with open(TASK_STORE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.exception("Failed to load task store: %s", e)
        return {"notes": [], "tasks": []}


def _save_task_store(data: Dict[str, Any]):
    try:
        with open(TASK_STORE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.exception("Failed to save task store: %s", e)


class WorkerAgent:
    def __init__(self):
        # Notes engine (centralised note API)
        self.notes = NotesEngine()

        # Tasks live in the shared memory file (alongside notes)
        self._store = _load_task_store()

        # LLM client for generating direct answers
        self.llm = GeminiClient()

        # tool map
        self.tools: Dict[str, Callable[[Any], Dict[str, Any]]] = {
            "add_note": self._add_note,
            "add_task": self._add_task,
            "list_tasks": self._list_tasks,
            "list_notes": self._list_notes,
            "web_search": self._web_search,
            "answer_directly": self._answer_directly,
            "clarify": self._clarify,
        }

    # -------------------------
    # Task helpers (persist to same file)
    # -------------------------
    @property
    def tasks(self):
        return self._store.get("tasks", [])

    def _persist_tasks(self):
        # keep notes untouched — NotesEngine handles notes persistence
        # load current store to avoid stomping notes
        store = _load_task_store()
        store["tasks"] = self.tasks
        _save_task_store(store)
        # reload local copy
        self._store = _load_task_store()

    # -------------------------
    # Tool implementations
    # -------------------------
    def _add_note(self, text: Any) -> Dict[str, Any]:
        """
        text can be string or dict; normalize to string.
        Delegates to NotesEngine.add_note_raw for direct adds.
        """
        txt = ""
        if isinstance(text, dict):
            txt = text.get("input") or text.get("text") or ""
        else:
            txt = str(text or "")

        if not txt.strip():
            return {"status": "error", "error": "Empty note text."}

        try:
            saved = self.notes.add_note_raw(txt.strip())
            return {"status": "ok", "action": "add_note", "output": saved}
        except Exception as e:
            logger.exception("Failed to add note: %s", e)
            return {"status": "error", "error": str(e)}

    def _list_notes(self, _: Any) -> Dict[str, Any]:
        try:
            notes = self.notes.list_notes()
            return {"status": "ok", "action": "list_notes", "output": notes}
        except Exception as e:
            logger.exception("Failed to list notes: %s", e)
            return {"status": "error", "error": str(e)}

    def _add_task(self, text: Any) -> Dict[str, Any]:
        txt = ""
        if isinstance(text, dict):
            txt = text.get("input") or text.get("text") or ""
        else:
            txt = str(text or "")

        if not txt.strip():
            return {"status": "error", "error": "Empty task text."}

        try:
            tasks = self._store.setdefault("tasks", [])
            new = {"id": (max((t.get("id", 0) for t in tasks), default=0) + 1), "text": txt.strip(), "done": False}
            tasks.append(new)
            self._persist_tasks()
            return {"status": "ok", "action": "add_task", "output": new}
        except Exception as e:
            logger.exception("Failed to add task: %s", e)
            return {"status": "error", "error": str(e)}

    def _list_tasks(self, _: Any) -> Dict[str, Any]:
        try:
            tasks = self._store.get("tasks", [])
            return {"status": "ok", "action": "list_tasks", "output": tasks}
        except Exception as e:
            logger.exception("Failed to list tasks: %s", e)
            return {"status": "error", "error": str(e)}

    def _web_search(self, query: Any) -> Dict[str, Any]:
        # Placeholder; keep signature compatible for planner tests
        q = query.get("input") if isinstance(query, dict) else str(query or "")
        return {
            "status": "ok",
            "action": "web_search",
            "output": [{
                "title": f"Dummy search result for '{q}'",
                "snippet": "This is a placeholder search result.",
                "link": "https://example.com"
            }]
        }

    def _answer_directly(self, plan: Any) -> Dict[str, Any]:
        """
        plan can be a dict (preferred) with keys: input, context
        or a plain string.
        Uses GeminiClient.generate(...) which will fallback to OpenRouter if configured.
        """
        try:
            if isinstance(plan, dict):
                user_text = plan.get("input", "") or ""
                context = plan.get("context", "") or ""
            else:
                user_text = str(plan or "")
                context = ""

            user_text = user_text.strip()
            if not user_text:
                return {"status": "ok", "action": "answer_directly", "output": "I didn't receive a clear question. Please repeat."}

            # Build minimal prompt that avoids tool/meta leak and asks for clean answer
            prompt = (
                "You are a helpful, concise assistant. Answer directly and briefly.\n\n"
                f"Context:\n{context}\n\n"
                f"Question:\n{user_text}\n\n"
                "Return ONLY the answer text (no JSON, no tags)."
            )

            resp = self.llm.generate(prompt)
            answer = (resp or "").strip()

            if not answer:
                answer = "(No response generated — check LLM settings.)"

            return {"status": "ok", "action": "answer_directly", "output": answer}

        except Exception as e:
            logger.exception("Answer generation failed: %s", e)
            return {"status": "error", "error": f"LLM error: {e}"}

    def _clarify(self, text: Any) -> Dict[str, Any]:
        txt = text.get("input") if isinstance(text, dict) else str(text or "")
        return {"status": "ok", "action": "clarify", "output": f"Could you clarify: {txt}?"}

    # -------------------------
    # Dispatcher
    # -------------------------
    def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        plan: expected dict with keys:
            - action: str
            - input: optional (str)
            - context: optional (str)

        Returns dict described at top of file.
        """
        if not isinstance(plan, dict):
            return {"status": "error", "error": "Plan must be a dict."}

        action = plan.get("action")
        if not action:
            return {"status": "error", "error": "Plan missing 'action'."}

        fn = self.tools.get(action)
        if not fn:
            return {"status": "error", "error": f"Unknown action: {action}"}

        try:
            # For answer_directly we pass the whole plan so fn can use context
            if action == "answer_directly":
                return fn(plan)
            # For list_notes we don't need an input argument
            if action == "list_notes":
                return fn(None)
            # For other actions, pass the input
            return fn(plan.get("input", ""))
        except Exception as e:
            logger.exception("Worker execution error for action %s: %s", action, e)
            return {"status": "error", "error": str(e)}
