import json
import os

MEMORY_FILE = "agent/memory/memory_store.json"


def _load_memory():
    """
    Loads persistent memory (facts) from JSON file.
    Returns a dict: { "facts": [...] }
    """
    if not os.path.exists(MEMORY_FILE):
        return {"facts": []}

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def _save_memory(memory):
    """
    Saves the full memory dict back to the JSON file.
    """
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def add_fact(fact: str):
    """
    Adds a new fact to persistent memory.
    Example fact: "User prefers short answers."
    """
    memory = _load_memory()
    memory["facts"].append(fact)
    _save_memory(memory)
    return fact

def get_facts():
    """
    Returns all stored persistent facts as a list of strings.
    """
    memory = _load_memory()
    return memory.get("facts", [])

