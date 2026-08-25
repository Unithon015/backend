import unittest

from src.infrastructure.policy_catalog.context import _match_score, _prepare_query


class TestPolicyContextMatching(unittest.TestCase):
    def test_scores_specific_incident_and_policy_terms(self) -> None:
        normalized, tokens = _prepare_query("대전 오월드 늑대 탈출 사건과 개인정보 노출")

        incident_score = _match_score(normalized, tokens, ["대전 오월드 늑대 탈출 사건"])
        policy_score = _match_score(normalized, tokens, ["개인정보", "전화번호", "주소"])
        unrelated_score = _match_score(normalized, tokens, ["성매매", "조건 만남"])

        self.assertGreater(incident_score, 0)
        self.assertGreater(policy_score, 0)
        self.assertEqual(unrelated_score, 0)
