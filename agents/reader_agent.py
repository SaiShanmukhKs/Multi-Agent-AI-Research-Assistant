"""
Agent 2: Document Reader Agent (The Analyst) 📄

Deep-reads web pages, extracts detailed information in a SINGLE batch pass to avoid API rate limits,
chunks content, and stores it in the vector database for retrieval by the Synthesis Agent.
"""

from __future__ import annotations

import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm import get_llm
from core.state import ResearchState
from tools import web_scraper, vector_store
from utils.chunker import chunk_text

logger = logging.getLogger(__name__)

BATCH_EXTRACTION_PROMPT = """You are a research content analyst. Given the following text
from multiple scraped web pages, analyze and extract key information from EACH source.

Scraped Sources:
{sources_text}

Return a JSON array of objects, one for each source:
[
  {{
    "url": "source_url",
    "key_facts": ["most important factual claims"],
    "data_points": ["quantitative statistics or measurements"],
    "quotes": ["notable direct quotes"],
    "entities": ["key organizations, technologies, or people"],
    "summary": "2-3 sentence summary of main points"
  }}
]

IMPORTANT: Return ONLY valid JSON array, no other text.
"""


def run_reader_agent(state: ResearchState) -> dict:
    """
    Execute the Document Reader Agent.

    1. Scrapes content from search result URLs
    2. Batch-extracts key information using Gemini in 1 efficient API call
    3. Chunks and embeds content in ChromaDB

    Args:
        state: Current LangGraph state.

    Returns:
        State update dict with extracted_content, vector_store_id, and agent_logs.
    """
    search_results = state.get("search_results", [])
    if not search_results:
        return {
            "status": "reader_complete",
            "agent_logs": ["📄 Reader Agent: No search results to process"],
        }

    logger.info(f"📄 Reader Agent: Processing {len(search_results)} URLs")

    # Step 1: Scrape web pages in parallel
    urls = [r["url"] for r in search_results if r.get("url")]
    scraped_docs = web_scraper.scrape_urls(urls, max_urls=5)

    if not scraped_docs:
        return {
            "status": "reader_complete",
            "agent_logs": ["📄 Reader Agent: Failed to scrape any URLs"],
        }

    # Step 2: Create/reuse a vector store collection
    collection_name = state.get("vector_store_id") or vector_store.create_collection()

    # Step 3: Batch process documents in 1 single LLM call to prevent 429 rate limit backoffs
    extracted_content = _batch_extract_information(scraped_docs)

    # Step 4: Chunk text for vector store
    all_chunks = []
    all_metadatas = []
    for doc in scraped_docs:
        chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadatas.append({
                "source_url": doc["url"],
                "title": doc.get("title", ""),
                "chunk_index": str(i),
                "total_chunks": str(len(chunks)),
            })

    # Step 5: Store chunks in ChromaDB
    stored_count = 0
    if all_chunks:
        stored_count = vector_store.add_documents(
            collection_name=collection_name,
            chunks=all_chunks,
            metadatas=all_metadatas,
        )

    log_msg = (
        f"📄 Reader Agent: Scraped {len(scraped_docs)} pages, "
        f"extracted info from {len(extracted_content)} docs, "
        f"stored {stored_count} chunks in vector DB"
    )
    logger.info(log_msg)

    return {
        "extracted_content": extracted_content,
        "vector_store_id": collection_name,
        "status": "reader_complete",
        "agent_logs": [log_msg],
    }


def _batch_extract_information(docs: list[dict]) -> list[dict]:
    """Combine documents and run 1 single LLM batch call to stay well below 5 RPM limits."""
    llm = get_llm(temperature=0.2)

    formatted_sources = []
    for i, d in enumerate(docs):
        truncated_text = d["text"][:2500]
        formatted_sources.append(
            f"--- SOURCE {i+1} ---\nURL: {d['url']}\nTitle: {d.get('title', '')}\nText:\n{truncated_text}\n"
        )

    sources_text = "\n".join(formatted_sources)

    messages = [
        SystemMessage(content="You are a research content analyst. Return only valid JSON."),
        HumanMessage(content=BATCH_EXTRACTION_PROMPT.format(sources_text=sources_text)),
    ]

    try:
        response = llm.invoke(messages)
        content = response.content.strip()

        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        parsed = json.loads(content)
        if isinstance(parsed, list):
            return parsed
    except Exception as e:
        logger.warning(f"Batch extraction fallback: {e}")

    # Fallback to simple summaries if batch fails
    return [
        {
            "url": d["url"],
            "title": d.get("title", ""),
            "key_facts": [],
            "data_points": [],
            "summary": d["text"][:300],
        }
        for d in docs
    ]
