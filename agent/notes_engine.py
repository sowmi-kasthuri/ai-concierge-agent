# Path: agent/notes_engine.py
"""
NotesEngine — deterministic, clean note-management backend.

Responsibilities:
-----------------
• Boolean detectors (is_note_previous, is_note_current, is_note_all, etc.)
• CRUD operations for notes:
      list_notes()
      note_previous(previous_answer)
      note_current(qa_text)
      note_all(context)
• Safe summarisation (no LLM)
• Persistence via agent/memory/memory_store.json

Rules:
------
• Never save clarifications or meta text
• Always compact long answers
• Deterministic summarisation (offline-safe)
"""

import json
import os
from typing import List, Dict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEM_PATH = os.path.join(BASE_DIR, "memory", "memory_store.json")


# ======================================================
# Storage helpers
# ======================================================
def _ensure_store():
    os.makedirs(os.path.dirname(MEM_PATH), exist_ok=True)
    if not os.path.exists(MEM_PATH):
        with open(MEM_PATH, "w", encoding="utf-8") as f:
            json.dump({"notes": [], "tasks": []}, f, indent=2)


def _load_store() -> Dict:
    _ensure_store()
    try:
        with open(MEM_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"notes": [], "tasks": []}


def _save_store(data: Dict):
    _ensure_store()
    with open(MEM_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ======================================================
# Summariser (offline-safe)
# ======================================================
def _naive_summarize(text: str, max_words: int = 30) -> str:
    """Simple deterministic summarizer."""
    if not text:
        return ""
    words = text.strip().split()
    if len(words) <= max_words:
        return " ".join(words).strip()
    return " ".join(words[:max_words]).strip() + "..."


def _is_meta_text(text: str) -> bool:
    """Avoid saving short clarifications, meta, or useless content."""
    if not text or not text.strip():
        return True

    t = text.strip()
    l = t.lower()

    bad_prefixes = (
        "can you", "could you",
        "please clarify", "please specify",
        "i'm not sure", "i'm not fully sure",
        "error", "note added",
        "no fact", "no_fact",
        "please"
    )
    if any(l.startswith(bp) for bp in bad_prefixes):
        return True

    # Short questions → often clarifications
    if t.endswith("?") and len(t.split()) <= 8:
        return True

    return False


# ======================================================
# NotesEngine
# ======================================================
class NotesEngine:
    def __init__(self):
        _ensure_store()
        self._store = _load_store()

    # --------------------------------------------
    # Boolean command detectors
    # --------------------------------------------
    def is_list_notes_cmd(self, text: str) -> bool:
        t = (text or "").lower().strip()
        return t in {
            "list notes", "show notes", "show my notes",
            "notes", "list my notes", "list note"
        }

    def is_note_all(self, text: str) -> bool:
        t = (text or "").lower()
        markers = [
            "note all", "note everything", "note all previous",
            "save all previous", "summarise all",
            "save entire conversation", "note entire", "note entire conversation"
        ]
        return any(m in t for m in markers)

    def is_note_previous(self, text: str) -> bool:
        t = (text or "").lower()
        markers = [
            "note the above", "note above", "save the above", "save above",
            "remember the above", "note previous", "save previous",
            "note previous answer", "add previous to notes"
        ]
        return any(m in t for m in markers)

    def is_note_current(self, text: str) -> bool:
        t = (text or "").lower()
        markers = [
            "note this", "note current", "note this response",
            "note q and a", "note q+a",
            "save current", "save this", "add this to notes",
            "save this response", "save current response",
            "note this answer"
        ]
        return any(m in t for m in markers)

    def is_note_confirmation(self, text: str) -> bool:
        t = (text or "").lower()
        checks = [
            "did you note", "did u note", "have you saved",
            "did you save", "have you noted"
        ]
        return any(c in t for c in checks)

    # --------------------------------------------
    # Internal helpers
    # --------------------------------------------
    def _reload(self):
        self._store = _load_store()

    def _persist(self):
        _save_store(self._store)

    def _next_id(self) -> int:
        notes = self._store.get("notes", [])
        return max((n.get("id", 0) for n in notes), default=0) + 1

    # --------------------------------------------
    # Public API
    # --------------------------------------------
    def list_notes(self) -> List[Dict]:
        self._reload()
        return list(self._store.get("notes", []))

    def add_note_raw(self, text: str) -> Dict:
        """Direct add — no summarisation."""
        self._reload()
        n = {"id": self._next_id(), "text": text}
        self._store.setdefault("notes", []).append(n)
        self._persist()
        return n

    # -------- A. note previous --------
    def note_previous(self, previous_answer: str) -> str:
        if not previous_answer or _is_meta_text(previous_answer):
            return ""
        summary = _naive_summarize(previous_answer, max_words=30)
        self.add_note_raw(summary)
        return summary

    # -------- B. note current Q+A --------
    def note_current(self, qa_text: str) -> str:
        if not qa_text or _is_meta_text(qa_text):
            return ""
        summary = _naive_summarize(qa_text, max_words=35)
        self.add_note_raw(summary)
        return summary

    # -------- C. note all previous --------
    def note_all(self, context: List[str]) -> str:
        if not context:
            return ""

        # Prefer assistant messages for summarisation
        assistant_lines = [
            line.split("assistant:", 1)[-1].strip()
            for line in context
            if line.lower().startswith("assistant:")
        ]
        if assistant_lines:
            text_to_sum = "\n".join(assistant_lines[-8:])
        else:
            text_to_sum = "\n".join(context[-30:])

        summary = _naive_summarize(text_to_sum, max_words=60)
        self.add_note_raw(summary)
        return summary
