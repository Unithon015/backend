import tempfile
import unittest
from unittest.mock import AsyncMock
from uuid import UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.application.content.service import ContentSubmissionService
from src.domain.content.entity import ContentSubmission
from src.domain.content.repository import ContentSubmissionRepository
from src.infrastructure.content.local_storage import LocalContentStorage
from src.interface.deps import get_current_user_id
from src.interface.content import router as router_module


async def _noop_analysis(*args, **kwargs):
    return None


class InMemoryContentSubmissionRepository(ContentSubmissionRepository):
    def __init__(self):
        self.items: dict[UUID, ContentSubmission] = {}

    async def save(self, submission: ContentSubmission) -> ContentSubmission:
        self.items[submission.id] = submission
        return submission

    async def find_by_id(self, submission_id: UUID) -> ContentSubmission | None:
        return self.items.get(submission_id)

    async def list_recent(self, limit: int) -> list[ContentSubmission]:
        return list(self.items.values())[:limit]

    async def list_by_owner(self, owner_id: UUID, limit: int) -> list[ContentSubmission]:
        return [item for item in self.items.values() if item.owner_id == owner_id][:limit]

    async def update_finding_status(self, finding_id, status):
        return None

    async def update_title(self, submission_id: UUID, title: str):
        self.items[submission_id].title = title

    async def update_analysis_run(self, analysis_run):
        for submission in self.items.values():
            for index, existing in enumerate(submission.analysis_runs):
                if existing.id == analysis_run.id:
                    submission.analysis_runs[index] = analysis_run
                    return analysis_run
        raise LookupError


class ContentRouterTest(unittest.TestCase):
    def setUp(self):
        self._original_openai_key = router_module.config.OPEN_API_KEY
        self._original_run_analysis = router_module.run_analysis
        router_module.config.OPEN_API_KEY = "test-key"
        router_module.run_analysis = _noop_analysis
        self.directory = tempfile.TemporaryDirectory()
        self.storage = LocalContentStorage(self.directory.name)
        self.service = ContentSubmissionService(
            InMemoryContentSubmissionRepository(), self.storage
        )
        app = FastAPI()
        app.include_router(router_module.router)
        app.dependency_overrides[router_module._service] = lambda: self.service
        app.dependency_overrides[router_module._storage] = lambda: self.storage
        self.user_id = UUID("00000000-0000-0000-0000-000000000001")
        app.dependency_overrides[get_current_user_id] = lambda: self.user_id
        self.client = TestClient(app)

    def tearDown(self):
        router_module.config.OPEN_API_KEY = self._original_openai_key
        router_module.run_analysis = self._original_run_analysis
        self.directory.cleanup()

    def test_upload_returns_queued_submission_and_asset_download_redirect(self):
        response = self.client.post(
            "/contents",
            data={"text": "신제품 게시 전 문구입니다."},
            files={"file": ("poster.png", b"\x89PNG\r\n\x1a\nimage-bytes", "image/png")},
        )

        self.assertEqual(response.status_code, 201, response.text)
        created = response.json()
        self.assertEqual(created["status"], "QUEUED")
        self.assertEqual(created["assets"][0]["content_type"], "IMAGE")

        analysis = self.client.get(f"/contents/{created['id']}/analysis")
        self.assertEqual(analysis.status_code, 200)
        self.assertEqual(analysis.json()["findings"], [])

        self.storage.get_download_url = AsyncMock(
            return_value="https://storage.example/poster.png"
        )
        asset = self.client.get(
            created["assets"][0]["download_url"],
            follow_redirects=False,
        )
        self.assertEqual(asset.status_code, 307)
        self.assertEqual(asset.headers["location"], "https://storage.example/poster.png")

        invalid_asset = self.client.get(
            created["assets"][0]["download_url"].split("?", 1)[0] + "?token=invalid",
            follow_redirects=False,
        )
        self.assertEqual(invalid_asset.status_code, 404)

    def test_rejects_upload_when_analysis_is_not_configured(self):
        router_module.config.OPEN_API_KEY = ""

        response = self.client.post("/contents", data={"text": "review this"})

        self.assertEqual(response.status_code, 503)

    def test_rejects_unauthenticated_content_access(self):
        app = FastAPI()
        app.include_router(router_module.router)
        app.dependency_overrides[router_module._service] = lambda: self.service

        response = TestClient(app).get("/contents")

        self.assertEqual(response.status_code, 401)
