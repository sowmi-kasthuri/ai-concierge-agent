from agent.agents.main_agent import MainAgent

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
        print("Agent:", result)
        print()

if __name__ == "__main__":
    main()
