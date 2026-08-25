import unittest

from src.application.incident_index.scheduler import (
    INITIAL_SYNC_YEARS,
    sync_initial_years_if_needed,
)


class FakeInitialSyncService:
    def __init__(self, summaries):
        self.summaries = summaries
        self.received_years = None

    async def sync_initial_years_if_needed(self, years):
        self.received_years = years
        return self.summaries


class TestInitialIncidentSync(unittest.IsolatedAsyncioTestCase):
    async def test_syncs_all_supported_years_through_the_service(self):
        service = FakeInitialSyncService(summaries=[])

        summaries = await sync_initial_years_if_needed(lambda: service)

        self.assertEqual(summaries, [])
        self.assertEqual(service.received_years, list(INITIAL_SYNC_YEARS))
