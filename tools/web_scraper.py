"""
Web Scraper Tool — High-performance Trafilatura-based content extraction.

Fetches full-page content from URLs, strips boilerplate in a single pass,
and returns clean text along with metadata (title, author, date).
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
    Fetch and extract clean content from a single URL in a single fast pass.

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

        # Extract content & metadata in a SINGLE pass using JSON output format
        data_json = trafilatura.extract(
            downloaded,
            output_format="json",
            include_comments=False,
            include_tables=True,
            favor_precision=True,
        )

        if not data_json:
            return None

        try:
            parsed = json.loads(data_json)
        except json.JSONDecodeError:
            return None

        text = (parsed.get("text") or "").strip()
        if not text or len(text) < 50:
            return None

        result = {
            "url": url,
            "title": parsed.get("title", ""),
            "author": parsed.get("author", ""),
            "date": parsed.get("date", ""),
            "text": text,
            "word_count": len(text.split()),
        }
        logger.info(f"Extracted {result['word_count']} words from: {url}")
        return result

    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return None


def scrape_urls(urls: list[str], max_urls: int | None = None) -> list[dict]:
    """
    Scrape multiple URLs in parallel using a thread pool with high concurrency.

    Args:
        urls: List of URLs to scrape.
        max_urls: Maximum number of URLs to process.

    Returns:
        List of successfully extracted content dicts.
    """
    limit = max_urls or config.MAX_URLS_TO_SCRAPE
    urls_to_process = urls[:limit]

    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_url = {executor.submit(scrape_url, url): url for url in urls_to_process}
        for future in as_completed(future_to_url):
            try:
                res = future.result()
                if res:
                    results.append(res)
            except Exception as e:
                logger.warning(f"Failed url scraping: {e}")

    logger.info(f"Successfully scraped {len(results)}/{len(urls_to_process)} URLs")
    return results
