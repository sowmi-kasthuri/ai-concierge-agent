# AI Concierge Agent  
Google Agentic AI Capstone Project (Nov 2025)

This project implements a personal **Learning & Interview Preparation Concierge Agent** using **Google’s Agent Development Kit (ADK)** and **Gemini**.  
The goal is to showcase agentic capabilities learned from the 5-Day Google Agents Intensive Program.

The agent supports:
- Saving and retrieving study notes  
- Managing tasks through custom MCP tools  
- Keyword search through a local notes store  
- Session + persistent memory  
- A planner → worker multi-agent workflow (A2A)  
- A reproducible demo via Kaggle Notebook  

---

## 🔧 Tech Stack
- **Google ADK (Python)**
- **Gemini API (free tier)**
- **MCP Local Tools**
- **JSON-based Memory + Data Store**
- **Kaggle Notebook for final demo**

---

## 🎯 Features (Planned & Delivered)
### ✔ Delivered
- ADK setup with working Gemini agent  
- MCP Tools:
  - `notes_tool` – store and retrieve notes  
  - `tasks_tool` – manage TODO items  
  - `search_tool` – keyword search  
- Persistent memory (`memory_store.json`)  
- Session memory (ADK-native)  
- Multi-agent orchestration:
  - Planner Agent  
  - Worker Agent  
- Logs + simple evaluation checks  
- Architecture diagram (coming soon)  
- Kaggle notebook demo  

### ⏳ Planned Extensions (Post-capstone)
- CI/CD workflow  
- More advanced memory (embeddings, FAISS)  
- Tool authentication (GitHub, Calendar)  
- Web UI frontend  

---

## 📂 Project Structure
ai-concierge-agent/
│
├── agent/
│ ├── main_agent.py
│ ├── agents/
│ │ ├── planner.py
│ │ └── worker.py
│ ├── tools/
│ │ ├── notes_tool.py
│ │ ├── tasks_tool.py
│ │ └── search_tool.py
│ └── memory/
│ └── memory_store.py
│
├── data/
│ ├── notes.json
│ └── tasks.json
│
├── demo/
│ └── demo.gif
│
├── notebooks/
│ └── kaggle_demo.ipynb
│
├── capstone_plan.md
├── capstone_plan.pdf
├── README.md
└── .gitignore


---

## 🚀 How to Run Locally
1. Install Python 3.10+  
2. Create a virtual environment:
    python -m venv .venv
    source .venv/bin/activate # Windows: .venv\Scripts\activate
3. Install dependencies:
    pip install -r requirements.txt
4. Add your Gemini API key to `.env`:
    GEMINI_API_KEY=your_key_here
5. Run the demo agent:
    python agent/main_agent.py

---

## 📘 Kaggle Notebook
The `kaggle_demo.ipynb` notebook provides:
- Architecture summary  
- Lightweight mock demo  
- Tool examples  
- Multi-agent example  
- No secret keys required  

---

## 🏆 Capstone Alignment
This project demonstrates all 5 concepts required for the Google Agents Capstone:

1. **Agents**  
2. **Tools (MCP)**  
3. **Memory**  
4. **Quality & Evaluation**  
5. **Multi-Agent Orchestration (A2A)**  

---

## 👤 Author
Sowmi — AI & Software Professional  
Created as part of the Google Agentic AI Capstone (Nov 2025)

---

## 📄 License
MIT

