import unittest

from src.infrastructure.namu_wiki.crawler import NamuWikiHtmlParser


class TestNamuWikiHtmlParser(unittest.TestCase):
    def test_extracts_title_body_and_sections(self):
        article = NamuWikiHtmlParser().parse(
            "https://namu.wiki/w/example",
            """
            <html>
              <head><title>예시 문서 - 나무위키</title></head>
              <body>
                <article>
                  <p>문서 소개입니다.</p>
                  <h2>개요</h2><p>첫 번째 섹션입니다.</p>
                  <h2>역사</h2><p>두 번째 섹션입니다.</p>
                  <script>ignore()</script>
                </article>
              </body>
            </html>
            """,
        )

        self.assertEqual(article.title, "예시 문서")
        self.assertIn("문서 소개입니다.", article.content)
        self.assertEqual(len(article.sections), 2)
        self.assertEqual(article.sections[0].title, "개요")
        self.assertEqual(article.sections[0].content, "첫 번째 섹션입니다.")
