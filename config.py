"""
Central configuration for the Multi-Agent Research Assistant.
Loads environment variables and provides project-wide settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
# API Keys
# ──────────────────────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# ──────────────────────────────────────────────
# LLM Configuration
# ──────────────────────────────────────────────
GEMINI_MODEL = "gemini-3.6-flash"
GEMINI_TEMPERATURE = 0.3          # Lower = more factual
GEMINI_MAX_TOKENS = 8192

# ──────────────────────────────────────────────
# Embedding Configuration
# ──────────────────────────────────────────────
EMBEDDING_MODEL = "gemini-embedding-001"

# ──────────────────────────────────────────────
# Search Configuration
# ──────────────────────────────────────────────
USE_TAVILY = bool(TAVILY_API_KEY)   # Auto-detect: Tavily if key exists, else DuckDuckGo
MAX_SEARCH_RESULTS = 5              # Results per sub-query
MAX_SUB_QUERIES = 5                 # Sub-queries generated per research topic

# ──────────────────────────────────────────────
# Document Processing
# ──────────────────────────────────────────────
CHUNK_SIZE = 800           # Tokens per chunk
CHUNK_OVERLAP = 100        # Overlap between chunks
MAX_URLS_TO_SCRAPE = 8     # Max URLs to fetch per research cycle
SCRAPE_TIMEOUT = 15        # Seconds before a URL fetch times out

# ──────────────────────────────────────────────
# Vector Store
# ──────────────────────────────────────────────
CHROMA_PERSIST_DIR = "./chroma_data"

# ──────────────────────────────────────────────
# Orchestrator
# ──────────────────────────────────────────────
MAX_RESEARCH_ITERATIONS = 2   # Max gap-filling loops
REPORT_AUDIENCE_OPTIONS = ["academic", "business", "casual"]
DEFAULT_AUDIENCE = "business"
