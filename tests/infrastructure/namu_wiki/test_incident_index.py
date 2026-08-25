import unittest

from src.infrastructure.namu_wiki.incident_index import NamuWikiIncidentCategoryParser


class TestNamuWikiIncidentCategoryParser(unittest.TestCase):
    def test_extracts_article_links_and_ignores_category_navigation(self) -> None:
        html = """
        <html>
          <body>
            <article class="wiki-content">
              <a href="/w/%EB%B6%84%EB%A5%98:2025%EB%85%84">분류:2025년</a>
              <a href="/w/2025%EB%85%84%20%EC%82%AC%EA%B1%B4">2025년 사건</a>
              <a href="/w/%EB%8C%80%EC%A0%84%20%EC%98%A4%EC%9B%94%EB%93%9C%20%EB%8A%91%EB%8C%80%20%ED%83%88%EC%B6%9C%20%EC%82%AC%EA%B1%B4">대전 오월드 늑대 탈출 사건</a>
              <a href="https://example.com/not-an-article">외부 링크</a>
              <a href="/w/%EC%98%A4%EB%A5%98?namespace=%EB%AC%B8%EC%84%9C">검색 링크</a>
            </article>
          </body>
        </html>
        """

        entries = NamuWikiIncidentCategoryParser().parse(
            incident_year=2025,
            category_url="https://namu.wiki/w/%EB%B6%84%EB%A5%98:2025%EB%85%84/%EC%82%AC%EA%B1%B4%EC%82%AC%EA%B3%A0",
            html=html,
        )

        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].year, 2025)
        self.assertEqual(entries[1].match_keywords[-1], "대전오월드늑대탈출사건")
        self.assertTrue(all(entry.source_url.startswith("https://namu.wiki/w/") for entry in entries))
        self.assertTrue(all(entry.source_type == "NAMU_WIKI" for entry in entries))
