"""
MainAgent (Clean and Final Version)

Coordinates:
- SmartPlanner → intent classification
- WorkerAgent → tools and answer generation
- NotesEngine → structured note capture (A, B, C)

Features:
- 4-turn compact context
- Stable topic tracking
- Safe note summarisation
- Strict separation of responsibilities
"""

import logging
from typing import Any, List

from agent.agents.smart_planner import SmartPlanner
from agent.agents.worker_agent import WorkerAgent
from agent.notes_engine import NotesEngine
from agent.llm.gemini_client import GeminiClient

logger = logging.getLogger(__name__)


class MainAgent:
    def __init__(self):
        # Try to create an LLM client (GeminiClient will fallback to OpenRouter if configured)
        try:
            self.llm = GeminiClient()
        except Exception as e:
            # Defensive fallback: logger + raise so user knows environment misconfig
            logger.warning("LLM init failed: %s. Planner may fallback where supported.", e)
            self.llm = None

        # Planner (expects an llm if available)
        # SmartPlanner should accept llm=None (if yours requires it, pass self.llm)
        try:
            self.planner = SmartPlanner(llm=self.llm) if self.llm is not None else SmartPlanner(llm=None)
        except TypeError:
            # older planner signature: SmartPlanner() with no args
            self.planner = SmartPlanner()

        # Worker (tools + LLM answering). WorkerAgent will create its own llm client internally.
        self.worker = WorkerAgent()

        # NotesEngine (deterministic summariser + persistent storage)
        self.notes = NotesEngine()

        # Conversation state
        self.context: List[str] = []
        self.last_answer: str = ""      # Last assistant answer ONLY
        self.last_topic: str = ""       # Tracks topic for follow-ups

    # ----------------------------------------------------
    # Helpers
    # ----------------------------------------------------
    def _update_context(self, role: str, text: str):
        text = (text or "").strip()
        if not text:
            return
        self.context.append(f"{role}: {text}")
        # keep it bounded
        if len(self.context) > 20:
            self.context = self.context[-20:]

    def _compact_context(self) -> str:
        # last 4 turns for Planner/Worker use
        return " | ".join(self.context[-4:]) if self.context else ""

    def _extract_topic(self, text: str) -> str:
        t = (text or "").lower()
        for p in ["what is", "what's", "define", "explain", "tell me about"]:
            if t.startswith(p):
                t = t.replace(p, "").strip()
        return t.strip(" ?.!") or text

    # ----------------------------------------------------
    # Main Handler
    # ----------------------------------------------------
    def handle(self, user_query: str) -> Any:
        user_query = (user_query or "").strip()
        if not user_query:
            return "Please type something."

        # Update context (user input)
        # For note commands we still keep the user input in context for traceability
        self._update_context("user", user_query)
        compact = self._compact_context()

        # ------------------------------------------------
        # DIRECT NOTE COMMANDS (handled *before* planner)
        # ------------------------------------------------
        # list notes (direct)
        if self.notes.is_list_notes_cmd(user_query):
            notes = self.notes.list_notes()
            if not notes:
                msg = "You have no notes."
            else:
                msg = "\n".join(f"{n['id']}. {n['text']}" for n in notes)
            # update assistant context and last_answer so note flows remain consistent
            self.last_answer = msg
            self._update_context("assistant", msg)
            return msg

        # NOTE ALL (C mode)
        if self.notes.is_note_all(user_query):
            summary = self.notes.note_all(self.context)
            if not summary:
                msg = "Nothing to summarise."
            else:
                msg = f"All previous noted.\n\n{summary}"
            self.last_answer = msg
            self._update_context("assistant", msg)
            return msg

        # NOTE PREVIOUS (A mode)
        if self.notes.is_note_previous(user_query):
            if not self.last_answer:
                msg = "Nothing above to note."
                self._update_context("assistant", msg)
                return msg
            summary = self.notes.note_previous(self.last_answer)
            if not summary:
                msg = "Nothing appropriate to save."
            else:
                msg = f"Previous noted:\n{summary}"
            self.last_answer = msg
            self._update_context("assistant", msg)
            return msg

        # NOTE CONFIRMATION ("did you note?" style)
        if self.notes.is_note_confirmation(user_query):
            if not self.last_answer:
                msg = "Nothing to confirm."
                self._update_context("assistant", msg)
                return msg
            summary = self.notes.note_previous(self.last_answer)
            if not summary:
                msg = "Nothing appropriate to save."
            else:
                msg = f"Note added:\n{summary}"
            self.last_answer = msg
            self._update_context("assistant", msg)
            return msg

        # NOTE CURRENT (B mode) — user intends to save the immediate Q+A; requires a Q+A interaction first
        if self.notes.is_note_current(user_query):
            # If they ask "note current" before we've answered, instruct them
            # We'll treat this as "must ask a question first" for clarity
            msg = "You must ask a question first to note the current Q+A."
            self._update_context("assistant", msg)
            return msg

        # ------------------------------------------------
        # NORMAL QUESTION FLOW → SmartPlanner → WorkerAgent
        # ------------------------------------------------
        # Plan (defensive: planner.decide may accept context arg or not)
        try:
            plan = self.planner.decide(user_query, compact)
        except TypeError:
            plan = self.planner.decide(user_query)

        # Ensure plan is a dict and contains keys we expect
        if not isinstance(plan, dict):
            plan = {"action": "answer_directly", "input": user_query, "context": compact}

        # Ensure input/context available for worker
        plan.setdefault("input", user_query)
        plan.setdefault("context", compact)

        result = self.worker.execute(plan)

        # Extract answer (worker returns structured dict)
        if result.get("status") == "ok":
            answer = (result.get("output") or "").strip()
        else:
            # propagate worker error as user-friendly text
            answer = result.get("error") or "An error occurred."

        # set last_answer ONLY to actual assistant replies (not planner clarifications)
        self.last_answer = answer
        self.last_topic = self._extract_topic(user_query)

        # Update context with assistant reply
        self._update_context("assistant", answer)

        # POST: if user immediately asked to "note current" in the same command (rare),
        # we handle that externally; typical flow: user will send another "note current" command.

        return answer
