from uuid import UUID

from src.domain.audience_profile.entity import AudienceProfile
from src.domain.audience_profile.repository import AudienceProfileRepository
from src.domain.user.repository import UserRepository

from .dto import AudienceProfileResponse, UpsertAudienceProfileRequest


class AudienceProfileNotFoundError(LookupError):
    pass


class AudienceProfileUserNotFoundError(LookupError):
    pass


class AudienceProfileService:
    def __init__(self, repository: AudienceProfileRepository, user_repository: UserRepository):
        self._repository = repository
        self._user_repository = user_repository

    async def save(
        self, user_id: UUID, request: UpsertAudienceProfileRequest
    ) -> AudienceProfileResponse:
        if not await self._user_repository.find_by_id(user_id):
            raise AudienceProfileUserNotFoundError
        profile = await self._repository.upsert(
            AudienceProfile(
                user_id=user_id,
                content_categories=request.content_categories,
                audience_contexts=request.audience_contexts,
                account_purposes=request.account_purposes,
            )
        )
        return self._response(profile)

    async def get(self, user_id: UUID) -> AudienceProfileResponse:
        profile = await self._repository.find_by_user_id(user_id)
        if not profile:
            raise AudienceProfileNotFoundError
        return self._response(profile)

    @staticmethod
    def _response(profile: AudienceProfile) -> AudienceProfileResponse:
        return AudienceProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            content_categories=profile.content_categories,
            audience_contexts=profile.audience_contexts,
            account_purposes=profile.account_purposes,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )
