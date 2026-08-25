from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from urllib.parse import unquote, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup, Tag

from src.domain.incident_index.entity import IncidentIndexEntry
from src.domain.namu_wiki.exceptions import NamuWikiUnavailable


NAMU_WIKI_ORIGIN = "https://namu.wiki"
YEARLY_INCIDENT_CATEGORY_URLS = {
    year: f"{NAMU_WIKI_ORIGIN}/w/%EB%B6%84%EB%A5%98:{year}%EB%85%84/%EC%82%AC%EA%B1%B4%EC%82%AC%EA%B3%A0"
    for year in (2024, 2025, 2026)
}


@dataclass(frozen=True)
class CategoryArticleLink:
    title: str
    article_url: str


class NamuWikiIncidentCategoryParser:
    """Extract only article titles and links from a yearly incident category page."""

    def parse(self, incident_year: int, category_url: str, html: str) -> list[IncidentIndexEntry]:
        soup = BeautifulSoup(html, "html.parser")
        content_root = (
            soup.select_one("article .wiki-content")
            or soup.select_one("article")
            or soup.select_one(".wiki-content")
            or soup.body
        )
        if content_root is None:
            raise NamuWikiUnavailable("The category page did not contain readable content.")

        entries: dict[str, IncidentIndexEntry] = {}
        for anchor in content_root.select("a[href]"):
            link = self._article_link(anchor, category_url)
            if link is None:
                continue
            entries[link.article_url] = IncidentIndexEntry(
                title=link.title,
                normalized_title=self._normalize_title(link.title),
                article_url=link.article_url,
                incident_year=incident_year,
            )

        if not entries:
            raise NamuWikiUnavailable("No article links were found in the category page.")
        return list(entries.values())

    @staticmethod
    def _article_link(anchor: Tag, category_url: str) -> CategoryArticleLink | None:
        href = anchor.get("href")
        title = re.sub(r"\s+", " ", anchor.get_text(" ", strip=True)).strip()
        if not href or not title:
            return None

        absolute_url = urljoin(category_url, href)
        parsed = urlparse(absolute_url)
        if parsed.scheme != "https" or parsed.netloc not in {"namu.wiki", "www.namu.wiki"}:
            return None
        if not parsed.path.startswith("/w/") or parsed.query or parsed.fragment:
            return None

        decoded_path = unquote(parsed.path[3:])
        # Category pages and category-navigation links are not incident records.
        if decoded_path.startswith("분류:") or title.startswith("분류:"):
            return None

        return CategoryArticleLink(title=title, article_url=f"{NAMU_WIKI_ORIGIN}{parsed.path}")

    @staticmethod
    def _normalize_title(title: str) -> str:
        normalized = re.sub(r"[^0-9a-z가-힣]+", "", title.lower())
        return normalized


class HttpNamuWikiIncidentCategoryGateway:
    _MAX_RESPONSE_BYTES = 2 * 1024 * 1024

    def __init__(
        self,
        parser: NamuWikiIncidentCategoryParser | None = None,
        timeout_seconds: float = 15.0,
    ):
        self._parser = parser or NamuWikiIncidentCategoryParser()
        self._timeout = httpx.Timeout(timeout_seconds)

    async def fetch_year(self, incident_year: int) -> list[IncidentIndexEntry]:
        category_url = YEARLY_INCIDENT_CATEGORY_URLS.get(incident_year)
        if category_url is None:
            raise ValueError("Only configured yearly incident category URLs can be crawled.")

        html = await self._fetch_html(category_url)
        return self._parser.parse(incident_year, category_url, html)

    async def _fetch_html(self, url: str) -> str:
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                follow_redirects=False,
                headers={
                    "Accept": "text/html,application/xhtml+xml",
                    "User-Agent": "Unithon015-NamuWikiConnector/1.0 (contact: team@unithon.local)",
                },
            ) as client:
                async with client.stream("GET", url) as response:
                    if response.is_redirect:
                        raise NamuWikiUnavailable("Unexpected redirect while retrieving a category page.")
                    response.raise_for_status()
                    if "text/html" not in response.headers.get("content-type", "").lower():
                        raise NamuWikiUnavailable("The category response was not HTML.")

                    payload = bytearray()
                    async for chunk in response.aiter_bytes():
                        payload.extend(chunk)
                        if len(payload) > self._MAX_RESPONSE_BYTES:
                            raise NamuWikiUnavailable("The category response exceeded the size limit.")
        except NamuWikiUnavailable:
            raise
        except httpx.HTTPError as exc:
            raise NamuWikiUnavailable("Unable to retrieve the Namu Wiki category page.") from exc

        return bytes(payload).decode(response.encoding or "utf-8", errors="replace")

    async def fetch_years(self, years: list[int], request_interval_seconds: float = 1.0) -> dict[int, list[IncidentIndexEntry]]:
        results: dict[int, list[IncidentIndexEntry]] = {}
        for index, year in enumerate(years):
            if index:
                await asyncio.sleep(request_interval_seconds)
            results[year] = await self.fetch_year(year)
        return results
