import re

import httpx
from bs4 import BeautifulSoup, Tag

from src.domain.namu_wiki.entity import NamuWikiArticle, NamuWikiSection
from src.domain.namu_wiki.exceptions import (
    NamuWikiArticleNotFound,
    NamuWikiUnavailable,
)
from src.domain.namu_wiki.repository import NamuWikiArticleGateway


class NamuWikiHtmlParser:
    """Keeps HTML-specific extraction details outside the domain layer."""

    _HEADING_NAMES = {"h2", "h3", "h4", "h5", "h6"}

    def parse(self, source_url: str, html: str) -> NamuWikiArticle:
        soup = BeautifulSoup(html, "html.parser")
        content_root = (
            soup.select_one("article .wiki-content")
            or soup.select_one("article")
            or soup.select_one(".wiki-content")
            or soup.body
        )
        if content_root is None:
            raise NamuWikiUnavailable("The article HTML did not contain readable content.")

        for node in content_root.select("script, style, noscript, nav, footer"):
            node.decompose()

        title_node = soup.select_one("h1, .wiki-title, title")
        title = self._text(title_node) if title_node else ""
        title = re.sub(r"\s*-\s*나무위키\s*$", "", title).strip()
        content = self._text(content_root)
        if not title or not content:
            raise NamuWikiUnavailable("The article did not contain a title and body.")

        return NamuWikiArticle(
            source_url=source_url,
            title=title,
            content=content,
            sections=tuple(self._sections(content_root)),
        )

    def _sections(self, content_root: Tag) -> list[NamuWikiSection]:
        sections: list[NamuWikiSection] = []
        for heading in content_root.find_all(self._HEADING_NAMES):
            title = self._text(heading)
            if not title:
                continue

            chunks: list[str] = []
            for sibling in heading.next_siblings:
                if isinstance(sibling, Tag) and sibling.name in self._HEADING_NAMES:
                    break
                if isinstance(sibling, Tag):
                    text = self._text(sibling)
                    if text:
                        chunks.append(text)

            sections.append(
                NamuWikiSection(
                    title=title,
                    level=int(heading.name[1]),
                    content=" ".join(chunks),
                )
            )
        return sections

    @staticmethod
    def _text(node: Tag | None) -> str:
        if node is None:
            return ""
        return re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()


class HttpNamuWikiArticleGateway(NamuWikiArticleGateway):
    _MAX_RESPONSE_BYTES = 2 * 1024 * 1024

    def __init__(
        self,
        parser: NamuWikiHtmlParser | None = None,
        timeout_seconds: float = 10.0,
    ):
        self._parser = parser or NamuWikiHtmlParser()
        self._timeout = httpx.Timeout(timeout_seconds)

    async def fetch(self, article_url: str) -> NamuWikiArticle:
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                follow_redirects=False,
                headers={
                    "Accept": "text/html,application/xhtml+xml",
                    "User-Agent": "Unithon015-NamuWikiConnector/1.0",
                },
            ) as client:
                async with client.stream("GET", article_url) as response:
                    if response.status_code == 404:
                        raise NamuWikiArticleNotFound("The requested Namu Wiki article was not found.")
                    if response.is_redirect:
                        raise NamuWikiUnavailable("Unexpected redirect while retrieving the article.")
                    response.raise_for_status()

                    content_type = response.headers.get("content-type", "").lower()
                    if "text/html" not in content_type:
                        raise NamuWikiUnavailable("The article response was not HTML.")

                    payload = bytearray()
                    async for chunk in response.aiter_bytes():
                        payload.extend(chunk)
                        if len(payload) > self._MAX_RESPONSE_BYTES:
                            raise NamuWikiUnavailable("The article response exceeded the size limit.")
        except (NamuWikiArticleNotFound, NamuWikiUnavailable):
            raise
        except httpx.HTTPStatusError as exc:
            raise NamuWikiUnavailable(
                f"Namu Wiki returned HTTP {exc.response.status_code}."
            ) from exc
        except httpx.HTTPError as exc:
            raise NamuWikiUnavailable("Unable to retrieve the Namu Wiki article.") from exc

        # See the yearly incident crawler: do not accept the HTTP client's
        # ISO-8859-1 fallback for Namu Wiki pages without a charset header.
        html = bytes(payload).decode("utf-8", errors="replace")
        return self._parser.parse(article_url, html)
