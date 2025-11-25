import pytest
from agent.main_agent import MainAgent

@pytest.fixture
def agent():
    return MainAgent()

def test_full_e2e_flow(agent):
    # 1. Ask a simple question
    response = agent.handle("What is 2+2?")
    assert response is not None
    assert isinstance(response, str)

    # 2. Note previous
    note_resp = agent.handle("note previous")
    assert "noted" in note_resp.lower() or "saved" in note_resp.lower()

    # 3. List notes
    notes = agent.handle("list notes")
    assert isinstance(notes, str)
    assert len(notes.strip()) > 0

    # 4. Add a task
    task_resp = agent.handle("add task buy groceries")
    assert "added" in task_resp.lower() or "task" in task_resp.lower()

    # 5. List tasks
    tasks = agent.handle("list tasks")
    assert isinstance(tasks, str)

    # 6. Note current (should politely refuse because "current" requires Q+A flow)
    note_current = agent.handle("note current")
    assert "ask a question first" in note_current.lower()

    # 7. Follow-up query
    follow = agent.handle("Tell me a joke")
    assert isinstance(follow, str)
    assert len(follow.strip()) > 0
