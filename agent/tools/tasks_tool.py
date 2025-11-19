import json
import os
from datetime import datetime

TASKS_FILE = "data/tasks.json"


def _load_tasks():
    """
    Internal helper.
    Loads the tasks list from JSON.
    Returns an empty list if the file doesn't exist yet.
    """
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as f:
        return json.load(f)


def _save_tasks(tasks):
    """
    Internal helper.
    Writes the full tasks list back to JSON.
    """
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def add_task(title: str):
    """
    Public function.
    Creates a new task with structured fields.

    Fields:
    - id: incremental integer
    - title: task description
    - status: "pending" or "done"
    - created_at: timestamp in ISO format
    - completed_at: null initially
    """
    tasks = _load_tasks()

    new_task = {
        "id": len(tasks) + 1,
        "title": title,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": None
    }

    tasks.append(new_task)
    _save_tasks(tasks)

    return new_task

def list_tasks():
    """
    Public function.
    Returns the full list of tasks.
    """
    return _load_tasks()

def complete_task(task_id: int):
    """
    Marks a task as completed.

    - Finds the task by ID
    - Sets status to 'done'
    - Adds a completion timestamp
    """
    tasks = _load_tasks()

    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "done"
            task["completed_at"] = datetime.utcnow().isoformat()
            _save_tasks(tasks)
            return task

    return None  # task not found
