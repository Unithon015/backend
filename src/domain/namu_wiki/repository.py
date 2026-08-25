from abc import ABC, abstractmethod

from .entity import NamuWikiArticle


class NamuWikiArticleGateway(ABC):
    @abstractmethod
    async def fetch(self, article_url: str) -> NamuWikiArticle:
        """Retrieve and normalize one Namu Wiki article."""
