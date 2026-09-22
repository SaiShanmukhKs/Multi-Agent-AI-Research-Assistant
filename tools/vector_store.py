"""
Vector Store Tool — ChromaDB with Gemini embeddings.

Manages document chunk storage and semantic retrieval for the RAG pipeline.
Each research session gets its own ChromaDB collection.
"""

from __future__ import annotations

import hashlib
import logging
import uuid

import chromadb
from google import genai

import config

logger = logging.getLogger(__name__)

# Initialize the new Gemini GenAI client
_genai_client = genai.Client(api_key=config.GOOGLE_API_KEY)

# Persistent ChromaDB client (shared across the session)
_client = chromadb.Client()  # In-memory for session-based use


def _embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts using Gemini's embedding model.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors.
    """
    embeddings = []
    # Process in batches of 20 to stay within API limits
    batch_size = 20
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        result = _genai_client.models.embed_content(
            model=config.EMBEDDING_MODEL,
            contents=batch,
        )
        for emb in result.embeddings:
            embeddings.append(emb.values)
    return embeddings


def _embed_query(query: str) -> list[float]:
    """Generate an embedding for a single query string."""
    result = _genai_client.models.embed_content(
        model=config.EMBEDDING_MODEL,
        contents=query,
    )
    return result.embeddings[0].values


def create_collection(name: str | None = None) -> str:
    """
    Create a new ChromaDB collection for a research session.

    Args:
        name: Optional collection name. Auto-generated if not provided.

    Returns:
        The collection name.
    """
    collection_name = name or f"research_{uuid.uuid4().hex[:8]}"
    _client.get_or_create_collection(name=collection_name)
    logger.info(f"Created ChromaDB collection: {collection_name}")
    return collection_name


def add_documents(
    collection_name: str,
    chunks: list[str],
    metadatas: list[dict],
) -> int:
    """
    Embed and store document chunks in a ChromaDB collection.

    Args:
        collection_name: Name of the target collection.
        chunks: List of text chunks to store.
        metadatas: List of metadata dicts (one per chunk), with keys like
                   'source_url', 'chunk_index', 'title'.

    Returns:
        Number of chunks successfully stored.
    """
    if not chunks:
        return 0

    collection = _client.get_or_create_collection(name=collection_name)

    # Generate unique IDs based on content hash
    ids = []
    for i, chunk in enumerate(chunks):
        content_hash = hashlib.md5(chunk.encode()).hexdigest()[:12]
        ids.append(f"chunk_{content_hash}_{i}")

    # Generate embeddings
    embeddings = _embed_texts(chunks)

    # Upsert into ChromaDB
    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    logger.info(f"Stored {len(chunks)} chunks in collection '{collection_name}'")
    return len(chunks)


def query_collection(
    collection_name: str,
    query: str,
    n_results: int = 10,
) -> list[dict]:
    """
    Query the vector store for chunks relevant to a query.

    Args:
        collection_name: Name of the collection to search.
        query: The search query.
        n_results: Number of results to return.

    Returns:
        List of dicts with keys: text, metadata, distance
    """
    collection = _client.get_or_create_collection(name=collection_name)

    if collection.count() == 0:
        logger.warning(f"Collection '{collection_name}' is empty")
        return []

    query_embedding = _embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count()),
    )

    output = []
    for i in range(len(results["documents"][0])):
        output.append({
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
            "distance": results["distances"][0][i] if results["distances"] else 0,
        })

    logger.info(f"Retrieved {len(output)} chunks for query: {query[:50]}...")
    return output


def delete_collection(collection_name: str) -> None:
    """Delete a ChromaDB collection to free memory."""
    try:
        _client.delete_collection(name=collection_name)
        logger.info(f"Deleted collection: {collection_name}")
    except Exception as e:
        logger.warning(f"Failed to delete collection '{collection_name}': {e}")
