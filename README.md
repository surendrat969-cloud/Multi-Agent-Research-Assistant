# 🧠 ResearchMind AI — Multi-Agent Research Assistant

A production-quality, AI-native research assistant powered by **10 collaborating AI agents** orchestrated with **LangGraph**, built on **Google Gemini 2.5 Flash**.

ResearchMind decomposes any research topic into sub-tasks, gathers and verifies information, retrieves knowledge from your uploaded documents (RAG with FAISS), writes a professional report, critiques and improves it, generates citations, slides, interview questions, and quizzes — all autonomously.

---

## ✨ Features

### Multi-Agent Pipeline (LangGraph)
1. **Planner Agent** — breaks the query into research sub-tasks
2. **Search Agent** — collects relevant synthesized information per task
3. **RAG Agent** — retrieves knowledge from uploaded documents via FAISS vector search
4. **Fact Verification Agent** — deduplicates, estimates confidence, flags uncertain statements
5. **Writer Agent** — generates a structured professional research report
6. **Critic Agent** — reviews and improves clarity, coherence, and quality
7. **Citation Agent** — generates references in APA, MLA, and IEEE formats
8. **Presentation Agent** — creates a slide deck outline
9. **Interview Agent** — generates interview questions and answers
10. **Quiz Agent** — generates MCQs with answers

Plus an **Enrichment Agent** that adds: Executive Summary, Abstract, Keywords, FAQ, Glossary, SWOT Analysis, Formulas, Learning/GitHub/YouTube/Books/Papers resources, Future Scope, Limitations, Advantages, Disadvantages, Applications, Timeline, and Tech Stack.

### User Features
- Research any topic
- Upload **PDF / DOCX / TXT** documents for RAG
- Ask follow-up questions with **persistent conversation memory**
- View previous chats & research history
- Save projects, download reports

### Dashboard
- Research history, total reports, most researched topics, average research time
- Plotly charts, dark mode, animations, responsive UI

### Authentication
- Login, Signup, Forgot Password, Profile page, session management

### Database (SQLite)
Users, Reports, Chats, Research Sessions, Uploaded Files, Feedback, Bookmarks

### Export Options
PDF, DOCX, Markdown, TXT, JSON

### Productivity
Bookmark, favorite, share, print, auto-save, search, delete, rename reports

### Visualizations
Mermaid mind map, flowchart, timeline; Plotly SWOT radar, charts, confidence gauge

### Logging
Every agent execution logs timing, status, and errors to console + rotating file.

---

## 🏗️ Architecture

```
researchmind-ai/
├── agents/         # 10 AI agents + LangGraph orchestrator + LLM client
├── services/       # Auth, Research, File processing, Visualization
├── database/       # SQLite schema + repositories (DAOs)
├── models/         # Pydantic data models (ResearchState, User, Report…)
├── memory/         # Conversation memory
├── rag/            # Document loader, chunking, embeddings, FAISS store
├── exports/        # PDF/DOCX/MD/TXT/JSON exporters
├── ui/             # Streamlit pages (auth, dashboard, chat, research, reports)
├── utils/          # Logger, helpers, timing decorators
├── config/         # Settings from .env
├── tests/          # Unit + integration tests (pytest)
├── docs/           # Architecture & sequence diagrams
├── assets/         # Static assets
├── app.py          # Streamlit entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .github/workflows/ci.yml
```

### Agent Flow
```
User Query
   └─► Planner ─► Search ─► RAG ─► Fact Verification
                                          └─► Writer ─► Critic ─► Enrichment
                                                                    ├─► Citation
                                                                    ├─► Presentation
                                                                    ├─► Interview
                                                                    └─► Quiz
```
See `docs/architecture.md` for full diagrams.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- A Google Gemini API key (free at https://aistudio.google.com/apikey)

### Install & Run (local)
```bash
# 1. Clone
git clone <your-repo-url>
cd researchmind-ai

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your_key_here

# 5. Run
streamlit run app.py
```
The app opens at http://localhost:8501. Sign up, then go to **Research**.

### Run with Docker
```bash
docker compose up --build
```
Open http://localhost:8501.

---

## ⚙️ Configuration

All settings live in `.env` (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key (required) | — |
| `GEMINI_MODEL` | Gemini model name | `gemini-2.5-flash` |
| `EMBEDDING_MODEL` | Embedding model | `models/embedding-001` |
| `DB_PATH` | SQLite database path | `database/researchmind.db` |
| `FAISS_PATH` | FAISS index directory | `faiss_index` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

---

## 🧪 Testing
```bash
pip install pytest
pytest tests/ -q
```

---

## 📦 Deployment

### Streamlit Cloud
1. Push to GitHub.
2. Go to https://share.streamlit.io, connect the repo.
3. Set `GEMINI_API_KEY` in Streamlit Cloud secrets.
4. Main file: `app.py`.

### Render
- Web Service, build command `pip install -r requirements.txt`, start command `streamlit run app.py`.

### Docker
- `docker compose up --build` (see `docker-compose.yml`).

---

## 🛠️ Tech Stack
Python 3.12 · LangGraph · LangChain · Google Gemini 2.5 Flash · Streamlit · FAISS · SQLite · PyPDF2 · python-docx · Pandas · NumPy · Plotly · ReportLab

---

## 📄 License
MIT — use freely for learning and interviews.
