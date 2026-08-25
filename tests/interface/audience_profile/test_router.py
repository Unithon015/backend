from datetime import datetime, timezone
import unittest
from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.application.audience_profile.dto import AudienceProfileResponse
from src.interface.deps import get_current_user_id
from src.interface.audience_profile import router as router_module


class FakeAudienceProfileService:
    def __init__(self):
        self.user_id = uuid4()
        self.profile_id = uuid4()

    async def save(self, user_id: UUID, request):
        assert user_id == self.user_id
        return AudienceProfileResponse(
            id=self.profile_id,
            user_id=user_id,
            content_categories=request.content_categories,
            audience_contexts=request.audience_contexts,
            account_purposes=request.account_purposes,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    async def get(self, user_id: UUID):
        return await self.save(
            user_id,
            type(
                "Request",
                (),
                {
                    "content_categories": ["diet"],
                    "audience_contexts": ["fitness_diet_interest"],
                    "account_purposes": ["information"],
                },
            )(),
        )


class AudienceProfileRouterTest(unittest.TestCase):
    def setUp(self):
        self.service = FakeAudienceProfileService()
        app = FastAPI()
        app.include_router(router_module.router)
        app.dependency_overrides[router_module._service] = lambda: self.service
        app.dependency_overrides[get_current_user_id] = lambda: self.service.user_id
        self.client = TestClient(app)

    def test_saves_the_three_onboarding_selections(self):
        response = self.client.put(
            "/users/me/audience-profile",
            json={
                "content_categories": ["diet", "health_fitness"],
                "audience_contexts": ["twenties_thirties", "women"],
                "account_purposes": ["information", "review"],
            },
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["content_categories"], ["diet", "health_fitness"])
        self.assertEqual(response.json()["audience_contexts"], ["twenties_thirties", "women"])

    def test_rejects_more_than_the_allowed_number_of_content_categories(self):
        response = self.client.put(
            "/users/me/audience-profile",
            json={
                "content_categories": ["diet", "food", "gaming", "travel"],
                "audience_contexts": ["general_public"],
                "account_purposes": ["information"],
            },
        )

        self.assertEqual(response.status_code, 422)
