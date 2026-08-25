import tempfile
import unittest
from uuid import UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.application.content.service import ContentSubmissionService
from src.domain.content.entity import ContentSubmission
from src.domain.content.repository import ContentSubmissionRepository
from src.infrastructure.content.local_storage import LocalContentStorage
from src.interface.content import router as router_module


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

    async def update_analysis_run(self, analysis_run):
        for submission in self.items.values():
            for index, existing in enumerate(submission.analysis_runs):
                if existing.id == analysis_run.id:
                    submission.analysis_runs[index] = analysis_run
                    return analysis_run
        raise LookupError


class ContentRouterTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.storage = LocalContentStorage(self.directory.name)
        self.service = ContentSubmissionService(
            InMemoryContentSubmissionRepository(), self.storage
        )
        app = FastAPI()
        app.include_router(router_module.router)
        app.dependency_overrides[router_module._service] = lambda: self.service
        app.dependency_overrides[router_module._storage] = lambda: self.storage
        self.client = TestClient(app)

    def tearDown(self):
        self.directory.cleanup()

    def test_upload_returns_queued_submission_and_asset_can_be_read(self):
        response = self.client.post(
            "/contents",
            data={"text": "신제품 게시 전 문구입니다."},
            files={"file": ("poster.png", b"image-bytes", "image/png")},
        )

        self.assertEqual(response.status_code, 201, response.text)
        created = response.json()
        self.assertEqual(created["status"], "QUEUED")
        self.assertEqual(created["assets"][0]["content_type"], "IMAGE")

        analysis = self.client.get(f"/contents/{created['id']}/analysis")
        self.assertEqual(analysis.status_code, 200)
        self.assertEqual(analysis.json()["findings"], [])

        asset = self.client.get(created["assets"][0]["download_url"])
        self.assertEqual(asset.status_code, 200)
        self.assertEqual(asset.content, b"image-bytes")
