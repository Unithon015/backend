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
        return self._persist_entries(entries_by_year)

    async def sync_year_with_entries(
        self,
        year: int,
    ) -> tuple[IncidentSyncSummary, list[IncidentIndexEntry]]:
        """Fetch one configured yearly category and return the saved index entries."""
        entries = await self._gateway.fetch_year(year)
        summaries = self._persist_entries({year: entries})
        return summaries[0], entries

    def list_active_entries(self, year: int) -> list[IncidentIndexEntry]:
        with self._session_factory() as session:
            return self._repository.find_active_entries(session, year)

    def _persist_entries(
        self,
        entries_by_year: dict[int, list[IncidentIndexEntry]],
    ) -> list[IncidentSyncSummary]:
        summaries: list[IncidentSyncSummary] = []
        with self._session_factory() as session:
            try:
                for year, entries in entries_by_year.items():
                    summaries.append(self._repository.sync_year(session, year, entries))
                session.commit()
            except Exception:
                session.rollback()
                raise
        return summaries

    async def sync_initial_years_if_needed(
        self,
        years: list[int],
    ) -> list[IncidentSyncSummary]:
        """Populate only the years that have never completed a sync.

        This is safe to call on every application start: completed years are
        read from the database and skipped instead of being crawled again.
        """
        with self._session_factory() as session:
            missing_years = self._repository.years_needing_initial_sync(session, years)

        if not missing_years:
            return []
        return await self.sync_years(missing_years)
