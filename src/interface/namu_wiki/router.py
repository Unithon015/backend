from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from src.application.incident_index.dto import (
    NamuWikiIncidentIndexResponse,
    NamuWikiIncidentSyncResponse,
)
from src.application.incident_index.service import SyncNamuWikiIncidentIndexService

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
from src.infrastructure.persistence.database import build_session_factory

router = APIRouter(prefix="/namu-wiki", tags=["namu-wiki"])
_service = CrawlNamuWikiArticleService(HttpNamuWikiArticleGateway())


def _incident_index_service() -> SyncNamuWikiIncidentIndexService:
    return SyncNamuWikiIncidentIndexService(build_session_factory())


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


@router.get(
    "/incidents/{year}",
    response_model=NamuWikiIncidentIndexResponse,
    status_code=status.HTTP_200_OK,
)
async def get_incidents_for_year(
    year: Annotated[int, Path(ge=2024, le=2026)],
    service: SyncNamuWikiIncidentIndexService = Depends(_incident_index_service),
) -> NamuWikiIncidentIndexResponse:
    """Return the cached incident index for one year without crawling Namu Wiki again."""
    return NamuWikiIncidentIndexResponse.from_entries(year, service.list_active_entries(year))


@router.post(
    "/incidents/{year}/sync",
    response_model=NamuWikiIncidentSyncResponse,
    status_code=status.HTTP_200_OK,
)
async def sync_incidents_for_year(
    year: Annotated[int, Path(ge=2024, le=2026)],
    service: SyncNamuWikiIncidentIndexService = Depends(_incident_index_service),
) -> NamuWikiIncidentSyncResponse:
    """Crawl one configured Namu Wiki yearly category and upsert its index."""
    try:
        summary, entries = await service.sync_year_with_entries(year)
    except NamuWikiUnavailable as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return NamuWikiIncidentSyncResponse.from_sync(summary, entries)
