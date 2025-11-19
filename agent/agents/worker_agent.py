import json
import os
from typing import Any, Dict, Callable

# Build absolute path to memory_store.json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE_PATH = os.path.join(BASE_DIR, "memory", "memory_store.json")


def load_store():
    if not os.path.exists(STORE_PATH):
        return {"notes": [], "tasks": []}

    try:
        with open(STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"notes": [], "tasks": []}


def save_store(data):
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


class WorkerAgent:
    def __init__(self):
        self.store = load_store()

        self.tools: Dict[str, Callable[[str], Dict[str, Any]]] = {
            "add_note": self._add_note,
            "add_task": self._add_task,
            "list_tasks": self._list_tasks,
            "web_search": self._web_search,
            "clarify": self._clarify,
        }

    # -------------------------
    # Persistence helpers
    # -------------------------
    @property
    def notes(self):
        return self.store["notes"]

    @property
    def tasks(self):
        return self.store["tasks"]

    def _persist(self):
        save_store(self.store)

    # -------------------------
    # Tool implementations
    # -------------------------
    def _add_note(self, text: str):
        note = {"id": len(self.notes) + 1, "text": text}
        self.notes.append(note)
        self._persist()
        return {"status": "ok", "action": "add_note", "output": note}

    def _add_task(self, text: str):
        task = {"id": len(self.tasks) + 1, "text": text, "done": False}
        self.tasks.append(task)
        self._persist()
        return {"status": "ok", "action": "add_task", "output": task}

    def _list_tasks(self, _: str):
        return {"status": "ok", "action": "list_tasks", "output": self.tasks}

    def _web_search(self, query: str):
        return {
            "status": "ok",
            "action": "web_search",
            "output": [{
                "title": f"Dummy search result for '{query}'",
                "snippet": "This is a placeholder search result.",
                "link": "https://example.com"
            }]
        }

    def _clarify(self, text: str):
        return {
            "status": "ok",
            "action": "clarify",
            "output": f"Could you clarify: {text}?"
        }

    # -------------------------
    # Dispatcher
    # -------------------------
    def execute(self, plan: Dict[str, Any]):
        action = plan.get("action")
        text = plan.get("input", "")

        if action not in self.tools:
            return {"status": "error", "error": f"Unknown action: {action}"}

        try:
            return self.tools[action](text)
        except Exception as e:
            return {"status": "error", "error": str(e)}
