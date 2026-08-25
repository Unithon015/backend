from fastapi import APIRouter, HTTPException, status

from src.application.namu_wiki.dto import (
    CrawlNamuWikiArticleRequest,
    NamuWikiArticleResponse,
)
from src.application.namu_wiki.service import CrawlNamuWikiArticleService
from src.domain.namu_wiki.exceptions import (
    InvalidNamuWikiUrl,
    NamuWikiArticleNotFound,
    NamuWikiUnavailable,
)
from src.infrastructure.namu_wiki.crawler import HttpNamuWikiArticleGateway

router = APIRouter(prefix="/namu-wiki", tags=["namu-wiki"])
_service = CrawlNamuWikiArticleService(HttpNamuWikiArticleGateway())


@router.post(
    "/articles/crawl",
    response_model=NamuWikiArticleResponse,
    status_code=status.HTTP_200_OK,
)
async def crawl_article(request: CrawlNamuWikiArticleRequest) -> NamuWikiArticleResponse:
    try:
        return await _service.crawl(request)
    except InvalidNamuWikiUrl as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except NamuWikiArticleNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except NamuWikiUnavailable as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
