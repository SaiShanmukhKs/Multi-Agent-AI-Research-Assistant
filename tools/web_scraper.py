"""
Web Scraper Tool — Trafilatura-based content extraction.

Fetches full-page content from URLs, strips boilerplate, and returns
clean text along with metadata (title, author, date).
"""

from __future__ import annotations

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import trafilatura

import config

logger = logging.getLogger(__name__)


def scrape_url(url: str) -> dict | None:
    """
    Fetch and extract clean content from a single URL.

    Args:
        url: The web page URL to scrape.

    Returns:
        Dict with keys: url, title, author, date, text, word_count
        Returns None if extraction fails.
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            logger.warning(f"Failed to download: {url}")
            return None

        # Extract main text content
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            favor_precision=True,
        )

        if not text or len(text.strip()) < 50:
            logger.warning(f"Insufficient content extracted from: {url}")
            return None

        # Extract metadata separately
        metadata_json = trafilatura.extract(
            downloaded,
            output_format="json",
            include_comments=False,
        )

        metadata = {}
        if metadata_json:
            try:
                metadata = json.loads(metadata_json)
            except json.JSONDecodeError:
                pass

        result = {
            "url": url,
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "date": metadata.get("date", ""),
            "text": text.strip(),
            "word_count": len(text.split()),
        }
        logger.info(f"Extracted {result['word_count']} words from: {url}")
        return result

    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return None


def scrape_urls(urls: list[str], max_urls: int | None = None) -> list[dict]:
    """
    Scrape multiple URLs in parallel using a thread pool.

    Args:
        urls: List of URLs to scrape.
        max_urls: Maximum number of URLs to process.

    Returns:
        List of successfully extracted content dicts.
    """
    limit = max_urls or config.MAX_URLS_TO_SCRAPE
    urls_to_process = urls[:limit]

    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(scrape_url, url): url for url in urls_to_process}
        for future in as_completed(future_to_url):
            result = future.result()
            if result:
                results.append(result)

    logger.info(f"Successfully scraped {len(results)}/{len(urls_to_process)} URLs")
    return results
