# 🔬 Multi-Agent Research Assistant

A system where **4 specialized AI agents** collaborate to research any topic end-to-end — from searching the web to delivering a polished, cited research report with visual elements.

> Give it a question like *"What are the latest advancements in quantum error correction?"* and it autonomously produces a comprehensive report.

## Architecture

```
User Query → 🔍 Search Agent → 📄 Reader Agent → 🧠 Synthesis Agent → ✍️ Writer Agent → Report
                     ↑                                    │
                     └──── Gap-Filling Loop ───────────────┘
```

### The 4 Agents

| Agent | Role | What It Does |
|-------|------|-------------|
| 🔍 **Scout** | Web Search | Decomposes query into sub-queries, searches web, ranks results |
| 📄 **Analyst** | Document Reader | Scrapes pages, extracts key info, chunks & embeds into vector DB |
| 🧠 **Thinker** | Synthesis | Cross-references sources, finds patterns, identifies gaps |
| ✍️ **Writer** | Report Writer | Generates polished Markdown/HTML report with citations & visuals |

### Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Framework | LangGraph |
| LLM | Google Gemini 2.0 Flash |
| Web Search | Tavily API / DuckDuckGo (fallback) |
| Web Scraping | Trafilatura |
| Embeddings | Gemini text-embedding-004 |
| Vector DB | ChromaDB (in-memory) |
| Visualizations | Plotly |
| Frontend | Streamlit |

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy the template
cp .env.example .env

# Edit .env and add your keys
# REQUIRED: GOOGLE_API_KEY (get at https://aistudio.google.com/app/apikey)
# OPTIONAL: TAVILY_API_KEY (get at https://app.tavily.com/)
```

### 3. Run

```bash
streamlit run app.py
```

## Features

- **Autonomous Research Pipeline**: 4 agents work in sequence with an optional gap-filling feedback loop
- **RAG Pipeline**: Documents are chunked, embedded, and stored in ChromaDB for semantic retrieval
- **Visual Reports**: Plotly charts (bar, pie, radar, timeline), word clouds, and key stat cards
- **Audience Adaptation**: Reports adapt tone for academic, business, or casual audiences
- **Dual Search**: Tavily API for enhanced search, DuckDuckGo as free fallback
- **Export**: Download reports as Markdown or styled HTML
- **Live Tracking**: Watch each agent's progress in real-time

## License

MIT
