# AI Concierge Agent

A lightweight multi-agent personal assistant built using Gemini + OpenRouter. Handles learning, note-taking, task tracking, and simple conversation flows with deterministic summarisation.

---

## Badges

> *(Replace with real badges later if you want)*

* ![Status](https://img.shields.io/badge/Status-Active-brightgreen)
* ![Python](https://img.shields.io/badge/Python-3.11-blue)
* ![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## Features

### Multi-agent architecture

* SmartPlanner (intent classification)
* WorkerAgent (tools + LLM answering)
* NotesEngine (A/B/C deterministic notes)

### Dual-LLM setup

* Gemini for planning
* OpenRouter/Gemini fallback for answers

### Deterministic Notes System

* `note previous` — saves last assistant reply
* `note current` — saves user-provided Q+A
* `note all` — summarises entire recent context
* `list notes` — clean enumeration

### Tasks Engine

* Add tasks
* List tasks

### Shared JSON Memory Store

* Stored in `agent/memory/memory_store.json`

### Stable, offline-safe behaviour

* No hallucination in notes
* Planner rule-based fallback
* End-to-end tested

---

## Architecture Diagram (Mermaid)

```mermaid
digraph Architecture {
    rankdir=LR;
    User [shape=oval, label="User"];
    MainAgent [shape=box, label="MainAgent"];
    SmartPlanner [shape=box, label="SmartPlanner"];
    WorkerAgent [shape=box, label="WorkerAgent"];
    NotesEngine [shape=box, label="NotesEngine"];

    User -> MainAgent;
    MainAgent -> SmartPlanner;
    MainAgent -> WorkerAgent;
    MainAgent -> NotesEngine;
    WorkerAgent -> NotesEngine;
}
```

---

## Project Structure

```
ai-concierge-agent/
│
├── agent/
│   ├── main_agent.py
│   ├── notes_engine.py
│   ├── agents/
│   │   ├── smart_planner.py
│   │   └── worker_agent.py
│   ├── llm/
│   │   ├── gemini_client.py
│   │   └── openrouter_client.py
│   └── memory/
│       └── memory_store.json
│
├── run.py
├── test_agent.py
├── test_env.py
├── test_notes.py
├── test_e2e.py
├── requirements.txt
└── README.md
```

---

## Setup

1. Create a virtual environment.
2. Install dependencies:

```
pip install -r requirements.txt
```

3. Add your API keys in `.env`:

```
GEMINI_API_KEY=...
OPENROUTER_API_KEY=...
```

---

## Running the Agent

```
python run.py
```

Sample:

```
You: What is an LLM?
Agent: An LLM is a Large Language Model...
```

---

## Notes Commands

```
note previous
note current
note all
list notes
```

Stored safely in JSON under `agent/memory/memory_store.json`.

---

## Tasks Commands

```
add task <text>
list tasks
```

---

## Tests

Run all tests:

```
pytest -q
```

The E2E test validates:

* Q&A flow
* Notes system
* Tasks system
* JSON persistence
* Planner → Worker routing

---

## Kaggle Notebook Demo

Include a simple notebook under `/notebooks` showing:

* Architecture overview
* Running the agent
* Notes flow
* Tasks flow

---

## Demo GIF Placeholder

Add a 10–15 sec CLI demonstration under `/demo`:

```
Ask → Answer → note previous → list notes → add task → list tasks
```

*(GIF to be added later)*

---

## Status

The project is fully functional, end-to-end tested, and ready for capstone submission.
Optional improvements can be added later: task deletion, tagging, embeddings, UI, WhatsApp/n8n integration.
