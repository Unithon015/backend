import unittest

from src.infrastructure.policy_catalog.context import (
    _match_score,
    _prepare_query,
    search_relevant_reference_context,
)


class _EmptyResult:
    def scalars(self):
        return self

    def all(self):
        return []


class _CountingSession:
    def __init__(self):
        self.calls = 0

    async def execute(self, _statement):
        self.calls += 1
        return _EmptyResult()


class TestPolicyContextMatching(unittest.TestCase):
    def test_scores_specific_incident_and_policy_terms(self) -> None:
        normalized, tokens = _prepare_query("대전 오월드 늑대 탈출 사건과 개인정보 노출")

        incident_score = _match_score(normalized, tokens, ["대전 오월드 늑대 탈출 사건"])
        policy_score = _match_score(normalized, tokens, ["개인정보", "전화번호", "주소"])
        unrelated_score = _match_score(normalized, tokens, ["성매매", "조건 만남"])

        self.assertGreater(incident_score, 0)
        self.assertGreater(policy_score, 0)
        self.assertEqual(unrelated_score, 0)


class TestMetaOnlyReferenceSearch(unittest.IsolatedAsyncioTestCase):
    async def test_does_not_query_incidents_when_the_worker_disables_them(self):
        session = _CountingSession()

        policies, incidents = await search_relevant_reference_context(
            session,
            "diet review",
            incident_limit=0,
        )

        self.assertEqual(session.calls, 1)
        self.assertEqual(policies, [])
        self.assertEqual(incidents, [])
