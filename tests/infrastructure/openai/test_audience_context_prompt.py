import unittest
from uuid import uuid4

from src.application.content.review_context import ReviewContext
from src.domain.audience_profile.entity import AudienceProfile
from src.infrastructure.openai.analyzer import (
    _GENERAL_SYSTEM_PROMPT,
    _audience_context_prompt,
    _with_audience_context,
)


class AudienceContextPromptTest(unittest.TestCase):
    def test_adds_configured_context_without_changing_the_no_profile_prompt(self):
        profile = AudienceProfile(
            user_id=uuid4(),
            content_categories=["diet"],
            audience_contexts=["twenties_thirties", "women"],
            account_purposes=["information"],
        )

        context = _audience_context_prompt(profile)
        self.assertIn("diet", context)
        self.assertIn("twenties_thirties", context)
        self.assertIn("age or gender alone", context)
        self.assertNotIn(
            "Account review context",
            _with_audience_context(_GENERAL_SYSTEM_PROMPT, None, None),
        )
        self.assertIn(
            "Account review context",
            _with_audience_context(_GENERAL_SYSTEM_PROMPT, profile, ReviewContext()),
        )

    def test_adds_priority_topics_without_historical_incident_context(self):
        context = ReviewContext(
            focus_topics=["eating-disorder related expressions"],
        )

        prompt = _with_audience_context(_GENERAL_SYSTEM_PROMPT, None, context)
        self.assertIn("eating-disorder related expressions", prompt)
        self.assertNotIn("Historical incident candidates", prompt)
