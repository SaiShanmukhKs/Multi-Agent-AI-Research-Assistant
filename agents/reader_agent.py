"""
Agent 2: Document Reader Agent (The Analyst) 📄

Deep-reads web pages, extracts detailed information, chunks content,
and stores it in the vector database for retrieval by the Synthesis Agent.
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

EXTRACTION_PROMPT = """You are a research content analyst. Given the following text
extracted from a web page, extract the most important information.

Source URL: {url}
Source Title: {title}

Text:
{text}

Extract and return a JSON object with these keys:
{{
    "key_facts": ["list of the most important factual claims"],
    "data_points": ["any quantitative data, statistics, or measurements mentioned"],
    "quotes": ["notable direct quotes with attribution"],
    "entities": ["key people, organizations, technologies mentioned"],
    "summary": "A 2-3 sentence summary of the main points"
}}

IMPORTANT: Return ONLY valid JSON, no other text.
"""


def run_reader_agent(state: ResearchState) -> dict:
    """
    Execute the Document Reader Agent.

    1. Scrapes content from search result URLs
    2. Extracts key information using Gemini
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

    # Step 1: Scrape web pages
    urls = [r["url"] for r in search_results if r.get("url")]
    scraped_docs = web_scraper.scrape_urls(urls)

    if not scraped_docs:
        return {
            "status": "reader_complete",
            "agent_logs": ["📄 Reader Agent: Failed to scrape any URLs"],
        }

    # Step 2: Create/reuse a vector store collection
    collection_name = state.get("vector_store_id") or vector_store.create_collection()

    # Step 3: Process each document
    extracted_content = []
    all_chunks = []
    all_metadatas = []

    for doc in scraped_docs:
        # Extract key information using Gemini
        extraction = _extract_information(doc)
        if extraction:
            extraction["url"] = doc["url"]
            extraction["title"] = doc.get("title", "")
            extraction["word_count"] = doc.get("word_count", 0)
            extracted_content.append(extraction)

        # Chunk the full text for vector storage
        chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadatas.append({
                "source_url": doc["url"],
                "title": doc.get("title", ""),
                "chunk_index": str(i),
                "total_chunks": str(len(chunks)),
            })

    # Step 4: Store chunks in ChromaDB
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


def _extract_information(doc: dict) -> dict | None:
    """Use Gemini to extract structured information from a document."""
    llm = get_llm(temperature=0.2)

    # Truncate very long texts to avoid token limits
    text = doc["text"][:6000]

    messages = [
        SystemMessage(content="You are a research content analyst. Return only valid JSON."),
        HumanMessage(content=EXTRACTION_PROMPT.format(
            url=doc["url"],
            title=doc.get("title", "Unknown"),
            text=text,
        )),
    ]

    try:
        response = llm.invoke(messages)
        content = response.content.strip()

        # Clean up potential markdown code block wrapping
        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        return json.loads(content)
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"Failed to extract info from {doc['url']}: {e}")
        # Return a basic extraction as fallback
        return {
            "key_facts": [],
            "data_points": [],
            "quotes": [],
            "entities": [],
            "summary": text[:300],
        }
