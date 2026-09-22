"""
Citation Manager.

Tracks sources throughout the research pipeline and generates
inline citations [1], [2] and a formatted bibliography section.
"""

from __future__ import annotations

import re


class CitationManager:
    """Manages source tracking and citation formatting across the report."""

    def __init__(self):
        self._sources: dict[str, dict] = {}   # url -> source_info
        self._citation_map: dict[str, int] = {}  # url -> citation_number

    def register_source(self, url: str, title: str = "", author: str = "", date: str = "") -> int:
        """
        Register a source and return its citation number.

        Args:
            url: The source URL.
            title: The document/page title.
            author: The author name (if available).
            date: The publication date (if available).

        Returns:
            The citation number assigned to this source.
        """
        if url in self._citation_map:
            return self._citation_map[url]

        citation_num = len(self._citation_map) + 1
        self._citation_map[url] = citation_num
        self._sources[url] = {
            "number": citation_num,
            "url": url,
            "title": title or self._extract_domain(url),
            "author": author,
            "date": date,
        }
        return citation_num

    def get_citation(self, url: str) -> str:
        """Return the inline citation string for a URL, e.g. '[1]'."""
        if url in self._citation_map:
            return f"[{self._citation_map[url]}]"
        num = self.register_source(url)
        return f"[{num}]"

    def format_bibliography(self) -> str:
        """
        Generate a formatted bibliography/references section in Markdown.

        Returns:
            Markdown string with numbered sources.
        """
        if not self._sources:
            return ""

        lines = ["## 📚 References\n"]
        sorted_sources = sorted(self._sources.values(), key=lambda s: s["number"])

        for src in sorted_sources:
            entry = f"**[{src['number']}]** "
            if src["author"]:
                entry += f"{src['author']}. "
            if src["title"]:
                entry += f"*{src['title']}*. "
            if src["date"]:
                entry += f"({src['date']}). "
            entry += f"[Link]({src['url']})"
            lines.append(entry)

        return "\n\n".join(lines)

    def inject_citations(self, text: str, source_urls: list[str]) -> str:
        """
        Replace source references in text with proper citation numbers.

        If the text mentions a URL directly, replace it with [N].
        Also adds citations at the end of paragraphs that reference sources.

        Args:
            text: The report text to process.
            source_urls: List of source URLs referenced in this text.

        Returns:
            Text with inline citations inserted.
        """
        for url in source_urls:
            citation = self.get_citation(url)
            # Replace full URLs with citations
            text = text.replace(url, citation)

        return text

    def get_all_sources(self) -> list[dict]:
        """Return all registered sources as a list of dicts."""
        return sorted(self._sources.values(), key=lambda s: s["number"])

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract a readable domain name from a URL."""
        match = re.search(r"https?://(?:www\.)?([^/]+)", url)
        return match.group(1) if match else url
