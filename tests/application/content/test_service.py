import tempfile
import unittest
from uuid import UUID

from src.application.content.service import (
    ContentSubmissionService,
    ContentSubmissionValidationError,
    UploadPayload,
)
from src.application.content.analysis_service import ContentAnalysisService
from src.domain.content.entity import AnalysisStatus, AssetType, ContentSubmission
from src.domain.content.repository import ContentSubmissionRepository
from src.infrastructure.content.local_storage import LocalContentStorage


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


class ContentSubmissionServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.storage = LocalContentStorage(self.directory.name)
        self.repository = InMemoryContentSubmissionRepository()
        self.service = ContentSubmissionService(self.repository, self.storage)

    async def asyncTearDown(self):
        self.directory.cleanup()

    async def test_creates_a_text_and_image_submission_with_queued_analysis(self):
        submission = await self.service.create(
            title=None,
            caption_text="신제품 출시를 알리는 게시글입니다.",
            files=[
                UploadPayload(
                    filename="launch.png",
                    mime_type="image/png",
                    content=b"not-a-real-image-but-storage-is-tested",
                )
            ],
        )

        self.assertEqual(submission.title, "launch")
        self.assertEqual(submission.status.value, "QUEUED")
        self.assertEqual(submission.assets[0].content_type, AssetType.IMAGE)
        self.assertTrue(
            self.storage.resolve_for_download(submission.assets[0].storage_key).exists()
        )

    async def test_rejects_unsupported_or_empty_submission(self):
        with self.assertRaises(ContentSubmissionValidationError):
            await self.service.create(title=None, caption_text=None, files=[])

        with self.assertRaises(ContentSubmissionValidationError):
            await self.service.create(
                title=None,
                caption_text=None,
                files=[
                    UploadPayload(
                        filename="document.pdf",
                        mime_type="application/pdf",
                        content=b"pdf",
                    )
                ],
            )

    async def test_analysis_worker_transitions_a_real_submission(self):
        submission = await self.service.create(
            title=None,
            caption_text="텍스트 검수 요청",
            files=[],
        )
        workflow = ContentAnalysisService(self.repository)

        started = await workflow.start(submission.id)
        progressed = await workflow.report_progress(
            submission.id, step="TEXT_ANALYSIS", progress_percent=50
        )
        completed = await workflow.complete(submission.id, findings=[])

        self.assertEqual(started.status, AnalysisStatus.ANALYZING)
        self.assertEqual(progressed.progress_percent, 50)
        self.assertEqual(completed.status, AnalysisStatus.COMPLETED)
        self.assertEqual(completed.progress_percent, 100)
