from __future__ import annotations

from datetime import UTC, datetime
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.incident_index.entity import IncidentIndexEntry, IncidentSyncSummary
from src.infrastructure.namu_wiki.incident_index import YEARLY_INCIDENT_CATEGORY_URLS

from .models import (
    NamuWikiIncidentIndexEntryModel,
    NamuWikiIncidentSourceModel,
    NamuWikiIncidentSyncRunModel,
)


class SqlAlchemyIncidentIndexRepository:
    def years_needing_initial_sync(
        self,
        session: Session,
        incident_years: list[int],
    ) -> list[int]:
        """Return years that do not yet have one completed index sync."""
        sources = session.scalars(
            select(NamuWikiIncidentSourceModel).where(
                NamuWikiIncidentSourceModel.incident_year.in_(incident_years)
            )
        )
        completed_years = {
            source.incident_year for source in sources if source.last_synced_at is not None
        }
        return [year for year in incident_years if year not in completed_years]

    def find_active_entries(
        self,
        session: Session,
        incident_year: int,
    ) -> list[IncidentIndexEntry]:
        models = session.scalars(
            select(NamuWikiIncidentIndexEntryModel)
            .where(
                NamuWikiIncidentIndexEntryModel.year == incident_year,
                NamuWikiIncidentIndexEntryModel.is_active.is_(True),
            )
            .order_by(NamuWikiIncidentIndexEntryModel.normalized_title)
        )
        return [
            IncidentIndexEntry(
                title=model.title,
                year=model.year,
                source_url=model.source_url,
                risk_categories=tuple(model.risk_categories),
                match_keywords=tuple(model.match_keywords),
                source_type=model.source_type,
            )
            for model in models
        ]

    def sync_year(
        self,
        session: Session,
        incident_year: int,
        entries: list[IncidentIndexEntry],
    ) -> IncidentSyncSummary:
        source = self._source_for_year(session, incident_year)
        run = NamuWikiIncidentSyncRunModel(source_id=source.id, status="PROCESSING")
        session.add(run)
        session.flush()

        existing_by_url = {
            entry.source_url: entry
            for entry in session.scalars(
                select(NamuWikiIncidentIndexEntryModel).where(
                    NamuWikiIncidentIndexEntryModel.source_id == source.id
                )
            )
        }
        now = datetime.now(UTC)
        inserted_count = 0
        updated_count = 0
        seen_urls = {entry.source_url for entry in entries}

        for entry in entries:
            existing = existing_by_url.get(entry.source_url)
            if existing is None:
                session.add(
                    NamuWikiIncidentIndexEntryModel(
                        source_id=source.id,
                        title=entry.title,
                        normalized_title=self._normalize_title(entry.title),
                        year=entry.year,
                        risk_categories=list(entry.risk_categories),
                        match_keywords=list(entry.match_keywords),
                        source_url=entry.source_url,
                        source_type=entry.source_type,
                        last_seen_at=now,
                    )
                )
                inserted_count += 1
                continue

            changed = (
                existing.title != entry.title
                or existing.normalized_title != self._normalize_title(entry.title)
                or existing.year != entry.year
                or existing.match_keywords != list(entry.match_keywords)
                or existing.source_type != entry.source_type
                or not existing.is_active
            )
            existing.title = entry.title
            existing.normalized_title = self._normalize_title(entry.title)
            existing.year = entry.year
            existing.match_keywords = list(entry.match_keywords)
            existing.source_type = entry.source_type
            if entry.risk_categories:
                existing.risk_categories = list(entry.risk_categories)
            existing.last_seen_at = now
            existing.is_active = True
            if changed:
                updated_count += 1

        for source_url, existing in existing_by_url.items():
            if source_url not in seen_urls:
                existing.is_active = False

        source.last_synced_at = now
        run.status = "COMPLETED"
        run.discovered_count = len(entries)
        run.inserted_count = inserted_count
        run.updated_count = updated_count
        run.finished_at = now
        session.flush()

        return IncidentSyncSummary(
            incident_year=incident_year,
            discovered_count=len(entries),
            inserted_count=inserted_count,
            updated_count=updated_count,
        )

    @staticmethod
    def _normalize_title(title: str) -> str:
        return re.sub(r"[^0-9a-z가-힣]+", "", title.lower())

    @staticmethod
    def _source_for_year(session: Session, incident_year: int) -> NamuWikiIncidentSourceModel:
        source = session.scalar(
            select(NamuWikiIncidentSourceModel).where(
                NamuWikiIncidentSourceModel.incident_year == incident_year
            )
        )
        if source is not None:
            return source

        source = NamuWikiIncidentSourceModel(
            incident_year=incident_year,
            category_url=YEARLY_INCIDENT_CATEGORY_URLS[incident_year],
        )
        session.add(source)
        session.flush()
        return source
