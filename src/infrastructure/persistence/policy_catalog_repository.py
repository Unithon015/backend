from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.policy_catalog.meta_community_standards import PolicyCatalogSeed

from .models import PolicyCatalogEntryModel


class SqlAlchemyPolicyCatalogRepository:
    def upsert_many(self, session: Session, provider: str, entries: tuple[PolicyCatalogSeed, ...]) -> int:
        changed = 0
        now = datetime.now(UTC)
        for entry in entries:
            existing = session.scalar(
                select(PolicyCatalogEntryModel).where(
                    PolicyCatalogEntryModel.provider == provider,
                    PolicyCatalogEntryModel.source_url == entry.source_url,
                )
            )
            if existing is None:
                session.add(
                    PolicyCatalogEntryModel(
                        provider=provider,
                        policy_code=entry.policy_code,
                        title=entry.title,
                        review_category=entry.review_category,
                        source_url=entry.source_url,
                        policy_summary=entry.policy_summary,
                        detection_hints=list(entry.detection_hints),
                        match_keywords=list(entry.match_keywords),
                        applicable_media_types=list(entry.applicable_media_types),
                        is_active=entry.is_active,
                        last_checked_at=now,
                    )
                )
                changed += 1
                continue

            if (
                existing.policy_code != entry.policy_code
                or existing.title != entry.title
                or existing.review_category != entry.review_category
                or existing.policy_summary != entry.policy_summary
                or existing.detection_hints != list(entry.detection_hints)
                or existing.match_keywords != list(entry.match_keywords)
                or existing.applicable_media_types != list(entry.applicable_media_types)
                or existing.is_active != entry.is_active
            ):
                existing.policy_code = entry.policy_code
                existing.title = entry.title
                existing.review_category = entry.review_category
                existing.policy_summary = entry.policy_summary
                existing.detection_hints = list(entry.detection_hints)
                existing.match_keywords = list(entry.match_keywords)
                existing.applicable_media_types = list(entry.applicable_media_types)
                existing.is_active = entry.is_active
                changed += 1
            existing.last_checked_at = now
        session.flush()
        return changed
