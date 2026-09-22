"""
Semantic Text Chunker.

Splits long documents into overlapping chunks that respect sentence
boundaries, ensuring no chunk ends in the middle of a sentence.
"""

from __future__ import annotations

import re

import config


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[str]:
    """
    Split text into overlapping chunks at sentence boundaries.

    Args:
        text: The full document text to chunk.
        chunk_size: Target number of words per chunk (default from config).
        chunk_overlap: Number of overlapping words between chunks.

    Returns:
        List of text chunks.
    """
    size = chunk_size or config.CHUNK_SIZE
    overlap = chunk_overlap or config.CHUNK_OVERLAP

    if not text or not text.strip():
        return []

    # Split into sentences using regex (handles common abbreviations)
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return [text]

    chunks = []
    current_chunk_sentences: list[str] = []
    current_word_count = 0

    for sentence in sentences:
        sentence_words = len(sentence.split())

        # If adding this sentence exceeds chunk_size, finalize current chunk
        if current_word_count + sentence_words > size and current_chunk_sentences:
            chunk_text_str = " ".join(current_chunk_sentences)
            chunks.append(chunk_text_str)

            # Keep overlap: walk backwards to find sentences that fill the overlap window
            overlap_sentences: list[str] = []
            overlap_count = 0
            for prev_sentence in reversed(current_chunk_sentences):
                prev_words = len(prev_sentence.split())
                if overlap_count + prev_words > overlap:
                    break
                overlap_sentences.insert(0, prev_sentence)
                overlap_count += prev_words

            current_chunk_sentences = overlap_sentences
            current_word_count = overlap_count

        current_chunk_sentences.append(sentence)
        current_word_count += sentence_words

    # Don't forget the last chunk
    if current_chunk_sentences:
        chunks.append(" ".join(current_chunk_sentences))

    return chunks
