# test_agent.py
from agent.main_agent import MainAgent

agent = MainAgent()

def run(q):
    print("\nUSER:", q)
    print("AGENT:", agent.handle(q))

# 1. Normal Q&A
run("What is RAG in AI?")
run("How does RAG retrieve information?")

# 2. A-mode: note previous
run("note above")

# 3. Ask a new question
run("What is a retriever model?")

# 4. C-mode: note all previous
run("note all previous")

# 5. List all notes
run("list notes")
