import json
import os

# Path to the notes storage file.
# Keeping it simple: one JSON file that stores a list of notes.
NOTES_FILE = "data/notes.json"


def _load_notes():
    """
    Internal helper.
    Safely load notes from the JSON file.
    
    - If the file doesn't exist yet, return an empty list.
    - Keeps the rest of the tool code clean and avoids repeated checks.
    """
    if not os.path.exists(NOTES_FILE):
        return []
    with open(NOTES_FILE, "r") as f:
        return json.load(f)


def _save_notes(notes):
    """
    Internal helper.
    Writes the notes list back to the JSON file.

    - Overwrites the file on each save (fine for small local data).
    - Ensures notes always stay consistent and readable.
    """
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=2)


def add_note(content: str):
    """
    Public function used by the agent.
    Adds a new note with a simple incremental ID.

    - Loads existing notes
    - Appends a new note
    - Saves everything back
    """
    notes = _load_notes()

    new_note = {
        "id": len(notes) + 1,
        "content": content
    }

    notes.append(new_note)
    _save_notes(notes)

    return new_note


def list_notes():
    """
    Public function.
    Returns all notes stored in the JSON file.
    """
    return _load_notes()


def search_notes(keyword: str):
    """
    Public function.
    Case-insensitive search for notes containing the keyword.

    - Converts both content and keyword to lowercase
    - Returns only matching notes
    """
    notes = _load_notes()
    keyword_lower = keyword.lower()

    results = [
        n for n in notes
        if keyword_lower in n["content"].lower()
    ]

    return results
