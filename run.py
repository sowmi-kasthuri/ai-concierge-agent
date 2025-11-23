from agent.logging_config import configure_logging
configure_logging(level="WARNING")

import logging
logger = logging.getLogger(__name__)
logger.info("Logging test: run.py started")

from agent.main_agent import MainAgent

def main():
    agent = MainAgent()

    print("AI Concierge Agent (Day 4 Multi-Agent Version)")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        result = agent.handle(user_input)

        # --- CLEAN HUMAN OUTPUT ONLY ---
        if isinstance(result, str):
            print("Agent:", result)
        elif isinstance(result, dict):
            print("Agent:", result.get("output", ""))
        else:
            print("Agent:", str(result))
        # --------------------------------

        print()

if __name__ == "__main__":
    main()
