import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.domain.incident_index.entity import IncidentIndexEntry, IncidentSyncSummary
from src.interface.namu_wiki import router as router_module


class FakeIncidentIndexService:
    def __init__(self):
        self.entry = IncidentIndexEntry(
            "2025년 예시 사건", "2025년예시사건", "https://namu.wiki/w/example", 2025
        )

    def list_active_entries(self, year):
        return [self.entry] if year == 2025 else []

    async def sync_year_with_entries(self, year):
        return (
            IncidentSyncSummary(year, discovered_count=1, inserted_count=1, updated_count=0),
            [self.entry],
        )


class NamuWikiIncidentIndexRouterTest(unittest.TestCase):
    def setUp(self):
        app = FastAPI()
        app.include_router(router_module.router)
        self.service = FakeIncidentIndexService()
        app.dependency_overrides[router_module._incident_index_service] = lambda: self.service
        self.client = TestClient(app)

    def test_returns_cached_incidents_for_the_requested_year(self):
        response = self.client.get("/namu-wiki/incidents/2025")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["entries"][0]["title"], "2025년 예시 사건")

    def test_syncs_the_requested_year(self):
        response = self.client.post("/namu-wiki/incidents/2025/sync")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["inserted_count"], 1)

    def test_rejects_an_unsupported_year(self):
        response = self.client.get("/namu-wiki/incidents/2023")

        self.assertEqual(response.status_code, 422)
