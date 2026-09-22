# Multi-Agent AI Research Assistant

A state-of-the-art, autonomous multi-agent research platform where **4 specialized AI agents** collaborate using **LangGraph** and **Google Gemini 2.5** to conduct end-to-end web research, extract facts, store vector chunks, synthesize insights, and generate polished, cited research reports with interactive visual analytics.

---

## 🏗️ Architecture: Decoupled FastAPI + React (Vite)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              REACT FRONTEND                                 │
│                   (Vite + React.js + Recharts + Lucide)                     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ REST API + Server-Sent Events (SSE)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FASTAPI BACKEND                                │
│                                (Python 3.14)                                │
│                                      │                                      │
│                  ┌───────────────────┴───────────────────┐                  │
│                  │           LangGraph Pipeline           │                  │
│                  └───────────────────┬───────────────────┘                  │
│                                      │                                      │
│    🔍 Scout Agent    📄 Analyst Agent   🧠 Thinker Agent   ✍️ Writer Agent │
│   (Search & Queries)  (RAG & ChromaDB)    (Synthesis)       (Drafting)      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start

### 1. Backend Setup (FastAPI)

```bash
# Clone the repository
git clone https://github.com/SaiShanmukhKs/Multi-Agent-AI-Research-Assistant.git
cd Multi-Agent-AI-Research-Assistant

# Create & activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY (from https://aistudio.google.com/app/apikey)

# Start FastAPI server (runs on http://localhost:8000)
uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend Setup (React.js + Vite)

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server (runs on http://localhost:5173)
npm run dev
```

---

## 🤖 The 4 Specialized Agents

1. **🔍 Agent 1: Scout Agent (Web Search)**
   - Decomposes the research topic into 3–5 targeted sub-queries.
   - Searches the web using Tavily API / DuckDuckGo search fallback.
   - Filters and ranks search hits.

2. **📄 Agent 2: Analyst Agent (Document Reader & RAG)**
   - Scrapes text using `trafilatura`.
   - Chunks documents (500–1000 tokens) with token overlap.
   - Generates vector embeddings via `gemini-embedding-001` and stores them in **ChromaDB**.

3. **🧠 Agent 3: Thinker Agent (Synthesis & Analysis)**
   - Performs RAG retrieval from ChromaDB.
   - Identifies key consensus, conflicting viewpoints, and knowledge gaps.
   - Generates structured chart data (Bar charts, sentiment metrics).

4. **✍️ Agent 4: Writer Agent (Report Generation)**
   - Produces structured research reports tailored for Business, Academic, or Casual audiences.
   - Includes executive summaries, formatted citations, and bibliographies.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.14, FastAPI, Uvicorn, LangGraph, LangChain, Google GenAI SDK (`gemini-2.5-flash`), ChromaDB, Trafilatura, Tavily / DuckDuckGo.
- **Frontend**: React.js (JavaScript), Vite, Recharts, Lucide-React, React-Markdown, Remark-GFM, Vanilla CSS (Glassmorphism design system).

---

## 📄 License

MIT License. Free for commercial and non-commercial use.
