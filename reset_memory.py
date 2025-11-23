import json
import os

# Resolve the memory store path regardless of where script is run
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_PATH = os.path.join(BASE_DIR, "agent", "memory", "memory_store.json")

def reset_memory():
    data = {"notes": [], "tasks": []}

    # Ensure directory exists
    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)

    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("✔ memory_store.json has been reset.")
    print(f"Path: {MEMORY_PATH}")

if __name__ == "__main__":
    reset_memory()
