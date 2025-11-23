# AI Concierge Agent (Clean Notes Engine Edition)

A lightweight multi-LLM agent designed for learning, note-taking, and interview preparation.  
This version includes a **stable Notes Engine**, **clean separation of concerns**, and **reliable conversational behaviour**.

---

## 🚀 Features

### 1) Dual-LLM Support
- **Gemini** (Google) for planning and routing (SmartPlanner)
- **OpenRouter** for high-quality answers (fallback and direct answering)

### 2) Notes Engine (Final Design)
Supports three deterministic note operations:
- **A: note previous** — saves a summary of the last assistant answer  
- **B: note current** — saves a summary of the current Q+A  
- **C: note all previous** — saves a summary of the full recent conversation  

Plus:
- `list notes` — view all saved notes  
- Fully offline summariser (no LLM calls)  
- Strict filters prevent saving clarifications or meta-text  

### 3) Clean Architecture
```
MainAgent
 ├── SmartPlanner (intent routing)
 ├── WorkerAgent  (tools + answering)
 └── NotesEngine  (storage + summarisation)
```

### 4) Persistence
All notes stored in:
```
agent/memory/memory_store.json
```

---

## 📦 Setup

Create `.env` in project root:

```
GEMINI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
GEMINI_MODEL=models/gemini-2.0-flash
OPENROUTER_MODEL=meta-llama/llama-3.1-70b-instruct
LLM_PROVIDER=dual
```

Install dependencies:

```
pip install python-dotenv requests
pip install google-genai  # optional but recommended
```

Run the agent:

```
python run.py
```

Run tests:

```
python test_notes.py
python test_env.py
python test_agent.py
```

---

## 📝 Notes Engine Commands

| User Command Example                | Behaviour                                    |
|------------------------------------|-----------------------------------------------|
| `note above`                       | Save summary of previous answer               |
| `note current response`            | Save summary of Q + current answer            |
| `note all previous`                | Save summary of entire recent conversation    |
| `did you note the above?`          | Confirmation → re-save previous summary       |
| `list notes`                       | Display all notes                             |

---

## ✔ Current Status (23 Nov 2025)

- All flows tested  
- No Q+note confusion  
- No planner/worker conflict  
- Notes Engine stable  

This version is safe to push to GitHub.

feat: stabilize NotesEngine and clean multi-LLM agent architecture

- Rebuilt NotesEngine (A/B/C modes: previous, current, all)
- Added offline deterministic summariser
- Clean separation: SmartPlanner → WorkerAgent → NotesEngine
- Fixed context window and topic tracking
- Simplified logic (removed broken Q+note flow)
- Implemented stable dual-LLM fallback (Gemini → OpenRouter)
- Updated tests (test_agent, test_notes, test_env)
- Improved run.py input loop
- Finalised folder structure under agent/

This is the first fully stable release of the agent.
