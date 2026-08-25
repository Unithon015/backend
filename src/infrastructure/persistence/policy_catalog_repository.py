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
                        last_checked_at=now,
                    )
                )
                changed += 1
                continue

            if (
                existing.policy_code != entry.policy_code
                or existing.title != entry.title
                or existing.review_category != entry.review_category
            ):
                existing.policy_code = entry.policy_code
                existing.title = entry.title
                existing.review_category = entry.review_category
                changed += 1
            existing.last_checked_at = now
        session.flush()
        return changed
