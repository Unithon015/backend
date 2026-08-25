import unittest

from src.domain.namu_wiki.exceptions import InvalidNamuWikiUrl
from src.domain.namu_wiki.url import NamuWikiArticleUrl


class TestNamuWikiArticleUrl(unittest.TestCase):
    def test_accepts_a_https_article_url_and_removes_fragments(self):
        article_url = NamuWikiArticleUrl.from_value(
            "https://namu.wiki/w/%EB%82%98%EB%AC%B4%EC%9C%84%ED%82%A4#section"
        )

        self.assertEqual(
            article_url.value,
            "https://namu.wiki/w/%EB%82%98%EB%AC%B4%EC%9C%84%ED%82%A4",
        )

    def test_rejects_non_namu_wiki_urls(self):
        with self.assertRaises(InvalidNamuWikiUrl):
            NamuWikiArticleUrl.from_value("https://example.com/w/article")

    def test_rejects_non_article_paths(self):
        with self.assertRaises(InvalidNamuWikiUrl):
            NamuWikiArticleUrl.from_value("https://namu.wiki/RecentChanges")
