import unittest
from uuid import uuid4

from src.domain.audience_profile.entity import AudienceProfile
from src.infrastructure.persistence.models import PolicyCatalogEntryModel
from src.infrastructure.review_context.resolver import DatabaseReviewContextResolver


class FakeResult:
    def __init__(self, values):
        self._values = values

    def scalars(self):
        return self._values


class FakeAsyncSession:
    def __init__(self, values):
        self._values = values
        self.calls = 0

    async def execute(self, _statement):
        self.calls += 1
        return FakeResult(self._values)


class DatabaseReviewContextResolverTest(unittest.IsolatedAsyncioTestCase):
    async def test_resolves_only_profile_relevant_meta_policy_candidates(self):
        policy = PolicyCatalogEntryModel(
            provider="META_COMMUNITY_STANDARDS",
            policy_code="META_SUICIDE_SELF_INJURY",
            title="Self-harm and eating disorders",
            review_category="SUICIDE_SELF_INJURY",
            source_url="https://meta.example/self-injury",
        )
        session = FakeAsyncSession([policy])
        profile = AudienceProfile(
            user_id=uuid4(),
            content_categories=["diet"],
            audience_contexts=["fitness_diet_interest"],
            account_purposes=["information"],
        )

        context = await DatabaseReviewContextResolver(session).resolve(profile)

        self.assertEqual(session.calls, 1)
        self.assertEqual(context.policy_candidates[0].policy_code, "META_SUICIDE_SELF_INJURY")
        self.assertIn("섭식 관련 표현", context.focus_topics)
        self.assertFalse(hasattr(context, "incident_candidates"))

    async def test_skips_database_queries_when_the_user_has_no_profile(self):
        session = FakeAsyncSession([])

        context = await DatabaseReviewContextResolver(session).resolve(None)

        self.assertTrue(context.is_empty)
        self.assertEqual(session.calls, 0)
