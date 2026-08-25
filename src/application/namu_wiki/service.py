from src.domain.namu_wiki.repository import NamuWikiArticleGateway
from src.domain.namu_wiki.url import NamuWikiArticleUrl

from .dto import CrawlNamuWikiArticleRequest, NamuWikiArticleResponse


class CrawlNamuWikiArticleService:
    def __init__(self, gateway: NamuWikiArticleGateway):
        self._gateway = gateway

    async def crawl(self, request: CrawlNamuWikiArticleRequest) -> NamuWikiArticleResponse:
        article_url = NamuWikiArticleUrl.from_value(str(request.url))
        article = await self._gateway.fetch(article_url.value)
        return NamuWikiArticleResponse.from_domain(article)
