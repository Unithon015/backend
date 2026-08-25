from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from src.domain.incident_index.entity import IncidentSyncSummary
from src.infrastructure.namu_wiki.incident_index import HttpNamuWikiIncidentCategoryGateway
from src.infrastructure.persistence.incident_index_repository import SqlAlchemyIncidentIndexRepository


class SyncNamuWikiIncidentIndexService:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        gateway: HttpNamuWikiIncidentCategoryGateway | None = None,
        repository: SqlAlchemyIncidentIndexRepository | None = None,
    ):
        self._session_factory = session_factory
        self._gateway = gateway or HttpNamuWikiIncidentCategoryGateway()
        self._repository = repository or SqlAlchemyIncidentIndexRepository()

    async def sync_years(self, years: list[int]) -> list[IncidentSyncSummary]:
        entries_by_year = await self._gateway.fetch_years(years)
        summaries: list[IncidentSyncSummary] = []
        with self._session_factory() as session:
            try:
                for year in years:
                    summaries.append(self._repository.sync_year(session, year, entries_by_year[year]))
                session.commit()
            except Exception:
                session.rollback()
                raise
        return summaries
