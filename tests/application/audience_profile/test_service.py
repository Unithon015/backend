import unittest
from uuid import UUID

from src.application.audience_profile.dto import UpsertAudienceProfileRequest
from src.application.audience_profile.service import AudienceProfileService
from src.domain.audience_profile.entity import AudienceProfile
from src.domain.audience_profile.repository import AudienceProfileRepository
from src.domain.user.entity import User
from src.domain.user.repository import UserRepository


class InMemoryAudienceProfileRepository(AudienceProfileRepository):
    def __init__(self):
        self.items: dict[UUID, AudienceProfile] = {}

    async def upsert(self, profile: AudienceProfile) -> AudienceProfile:
        existing = self.items.get(profile.user_id)
        if existing:
            profile = AudienceProfile(
                id=existing.id,
                user_id=profile.user_id,
                content_categories=profile.content_categories,
                audience_contexts=profile.audience_contexts,
                account_purposes=profile.account_purposes,
                created_at=existing.created_at,
            )
        self.items[profile.user_id] = profile
        return profile

    async def find_by_user_id(self, user_id: UUID) -> AudienceProfile | None:
        return self.items.get(user_id)


class InMemoryUserRepository(UserRepository):
    def __init__(self, user: User):
        self.user = user

    async def save(self, user: User) -> User:
        self.user = user
        return user

    async def find_by_id(self, user_id: UUID) -> User | None:
        return self.user if self.user.id == user_id else None

    async def find_by_email(self, email: str) -> User | None:
        return self.user if self.user.email == email else None

    async def find_all(self) -> list[User]:
        return [self.user]


class AudienceProfileServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.user = User(email="creator@example.com", name="Creator", provider="local", provider_id="")
        self.service = AudienceProfileService(
            InMemoryAudienceProfileRepository(), InMemoryUserRepository(self.user)
        )

    async def test_saves_and_replaces_a_single_profile_for_one_user(self):
        first = await self.service.save(
            self.user.id,
            UpsertAudienceProfileRequest(
                content_categories=["diet"],
                audience_contexts=["twenties_thirties", "fitness_diet_interest"],
                account_purposes=["information"],
            ),
        )
        second = await self.service.save(
            self.user.id,
            UpsertAudienceProfileRequest(
                content_categories=["health_fitness", "diet"],
                audience_contexts=["women"],
                account_purposes=["information", "review"],
            ),
        )

        self.assertEqual(first.id, second.id)
        self.assertEqual(second.content_categories, ["health_fitness", "diet"])
        self.assertEqual((await self.service.get(self.user.id)).audience_contexts, ["women"])
