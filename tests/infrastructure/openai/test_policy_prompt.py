import unittest

from src.domain.content.entity import EvidenceLayer, FindingEvidence, ReviewFinding, ReviewPriority
from src.infrastructure.openai.analyzer import _build_reference_system_prompt, _validate_reference_findings
from src.infrastructure.policy_catalog.context import IncidentPromptContext, PolicyPromptContext


class TestPolicyPrompt(unittest.TestCase):
    def test_includes_only_catalogued_policy_values_as_evidence_context(self) -> None:
        policy = PolicyPromptContext(
            policy_code="META_TEST",
            title="테스트 정책",
            review_category="TEST_CATEGORY",
            source_url="https://example.com/policy",
            policy_summary="테스트 요약",
            detection_hints=("테스트 신호",),
            applicable_media_types=("text",),
        )

        incident = IncidentPromptContext(
            title="테스트 사건",
            year=2026,
            source_url="https://namu.wiki/w/test",
            source_type="NAMU_WIKI",
            risk_categories=(),
        )

        prompt = _build_reference_system_prompt([policy], [incident])

        self.assertIn('"테스트 정책"', prompt)
        self.assertIn("https://example.com/policy", prompt)
        self.assertIn("META_COMMUNITY_STANDARDS", prompt)
        self.assertIn('"테스트 사건"', prompt)
        self.assertIn("https://namu.wiki/w/test", prompt)

    def test_rejects_hallucinated_evidence_not_present_in_db_candidates(self) -> None:
        policy = PolicyPromptContext(
            policy_code="META_TEST",
            title="테스트 정책",
            review_category="TEST_CATEGORY",
            source_url="https://example.com/policy",
            policy_summary="테스트 요약",
            detection_hints=("테스트 신호",),
            applicable_media_types=("text",),
        )
        valid = FindingEvidence(
            layer=EvidenceLayer.RULE,
            title="테스트 정책",
            source_url="https://example.com/policy",
            provider="META_COMMUNITY_STANDARDS",
        )
        hallucinated = FindingEvidence(
            layer=EvidenceLayer.RULE,
            title="없는 정책",
            source_url="https://example.com/fake",
            provider="META_COMMUNITY_STANDARDS",
        )
        finding = ReviewFinding(
            category_code="R-04",
            priority=ReviewPriority.MEDIUM,
            signal_type="테스트",
            reason="테스트",
            evidences=[valid, hallucinated],
        )

        validated = _validate_reference_findings([finding], [policy], [])

        self.assertEqual(len(validated), 1)
        self.assertEqual(validated[0].evidences, [valid])
