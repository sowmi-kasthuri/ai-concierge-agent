from agent.main_agent import ConciergeAgent

def main():
    agent = ConciergeAgent()
    print("Concierge Agent v0.1 — type 'exit' to quit\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        reply = agent.ask(user_input)
        print(f"Agent: {reply}\n")

if __name__ == "__main__":
    main()
