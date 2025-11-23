# Path: test_full_manual.py
from agent.main_agent import MainAgent

agent = MainAgent()

def run(q):
    print("\nUSER:", q)
    print("AGENT:", agent.handle(q))

# --- BASIC QA ---
run("What is RAG in AI?")
run("How does RAG retrieve information?")

# --- NOTE PREVIOUS ---
run("note above")

# --- ANOTHER QA ---
run("What is a retriever model?")

# --- NOTE ALL ---
run("note all previous")

# --- LIST NOTES ---
run("list notes")
