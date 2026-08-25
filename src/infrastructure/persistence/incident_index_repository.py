from __future__ import annotations

from datetime import UTC, datetime

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
            entry.article_url: entry
            for entry in session.scalars(
                select(NamuWikiIncidentIndexEntryModel).where(
                    NamuWikiIncidentIndexEntryModel.source_id == source.id
                )
            )
        }
        now = datetime.now(UTC)
        inserted_count = 0
        updated_count = 0
        seen_urls = {entry.article_url for entry in entries}

        for entry in entries:
            existing = existing_by_url.get(entry.article_url)
            if existing is None:
                session.add(
                    NamuWikiIncidentIndexEntryModel(
                        source_id=source.id,
                        title=entry.title,
                        normalized_title=entry.normalized_title,
                        article_url=entry.article_url,
                        incident_year=incident_year,
                        last_seen_at=now,
                    )
                )
                inserted_count += 1
                continue

            changed = (
                existing.title != entry.title
                or existing.normalized_title != entry.normalized_title
                or not existing.is_active
            )
            existing.title = entry.title
            existing.normalized_title = entry.normalized_title
            existing.last_seen_at = now
            existing.is_active = True
            if changed:
                updated_count += 1

        for article_url, existing in existing_by_url.items():
            if article_url not in seen_urls:
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
