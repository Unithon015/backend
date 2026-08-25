import unittest

from src.infrastructure.policy_catalog.meta_community_standards import META_COMMUNITY_STANDARDS


class TestMetaCommunityStandards(unittest.TestCase):
    def test_keeps_all_requested_policy_links_as_unique_https_entries(self) -> None:
        self.assertEqual(len(META_COMMUNITY_STANDARDS), 27)
        self.assertEqual(len({entry.policy_code for entry in META_COMMUNITY_STANDARDS}), 27)
        self.assertTrue(all(entry.source_url.startswith("https://") for entry in META_COMMUNITY_STANDARDS))
