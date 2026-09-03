from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.audience_profile.entity import AudienceProfile
from src.domain.audience_profile.repository import AudienceProfileRepository
from src.infrastructure.db.models import AudienceProfileModel


class PostgresAudienceProfileRepository(AudienceProfileRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def upsert(self, profile: AudienceProfile) -> AudienceProfile:
        now = datetime.now(timezone.utc)
        statement = (
            insert(AudienceProfileModel)
            .values(
                id=profile.id,
                user_id=profile.user_id,
                content_categories=profile.content_categories,
                audience_contexts=profile.audience_contexts,
                account_purposes=profile.account_purposes,
                created_at=profile.created_at,
                updated_at=now,
            )
            .on_conflict_do_update(
                index_elements=[AudienceProfileModel.user_id],
                set_={
                    "content_categories": profile.content_categories,
                    "audience_contexts": profile.audience_contexts,
                    "account_purposes": profile.account_purposes,
                    "updated_at": now,
                },
            )
            .returning(AudienceProfileModel)
        )
        model = (await self._session.execute(statement)).scalar_one()
        await self._session.commit()
        return self._to_entity(model)

    async def find_by_user_id(self, user_id: UUID) -> AudienceProfile | None:
        model = await self._session.scalar(
            select(AudienceProfileModel).where(AudienceProfileModel.user_id == user_id)
        )
        return self._to_entity(model) if model else None

    @staticmethod
    def _to_entity(model: AudienceProfileModel) -> AudienceProfile:
        return AudienceProfile(
            id=model.id,
            user_id=model.user_id,
            content_categories=list(model.content_categories or []),
            audience_contexts=list(model.audience_contexts or []),
            account_purposes=list(model.account_purposes or []),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
