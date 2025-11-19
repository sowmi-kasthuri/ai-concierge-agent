"""
MainAgent: Coordinates PlannerAgent → WorkerAgent

Usage:
    from agent.agents.main_agent import MainAgent
    agent = MainAgent()
    agent.handle("Add a note: Buy apples")
"""

import json
from typing import Dict, Any

from agent.agents.planner_agent import PlannerAgent
from agent.agents.worker_agent import WorkerAgent


class MainAgent:
    def __init__(self, enable_gemini=False):
        self.planner = PlannerAgent(enable_gemini=enable_gemini)
        self.worker = WorkerAgent()


    def handle(self, user_query: str) -> Dict[str, Any]:
        # 1. Get plan from planner
        plan = self.planner.plan(user_query)

        # If planner can’t determine the intent
        if plan["action"] == "clarify":
            return {
                "status": "clarify",
                "message": plan["input"],
                "reason": plan["reasoning"]
            }

        # 2. Execute plan
        result = self.worker.execute(plan)

        return {
            "status": result.get("status"),
            "action": plan["action"],
            "output": result.get("output", result.get("error"))
        }


# Quick test when run directly
if __name__ == "__main__":
    agent = MainAgent()
    tests = [
        "Add a note: Buy apples",
        "Add task: Finish slides",
        "Show my tasks",
        "Search for almond milk",
        "Remind me to call Mom tomorrow"
    ]

    for t in tests:
        print("Query:", t)
        print(json.dumps(agent.handle(t), indent=2))
        print("---")
