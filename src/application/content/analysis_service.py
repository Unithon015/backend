from dataclasses import replace
from datetime import datetime, timezone
from uuid import UUID

from src.domain.content.entity import AnalysisRun, AnalysisStatus, ReviewFinding
from src.domain.content.repository import ContentSubmissionRepository


class InvalidAnalysisTransitionError(ValueError):
    pass


class ContentAnalysisService:
    """Application boundary used by STT/OCR/retrieval workers, not public HTTP routes."""

    def __init__(self, repository: ContentSubmissionRepository):
        self._repository = repository

    async def start(self, submission_id: UUID, *, step: str = "PREPROCESSING") -> AnalysisRun:
        run = await self._latest_run(submission_id)
        if run.status != AnalysisStatus.QUEUED:
            raise InvalidAnalysisTransitionError("Only queued analysis can be started")
        return await self._repository.update_analysis_run(
            replace(
                run,
                status=AnalysisStatus.ANALYZING,
                current_step=step,
                started_at=datetime.now(timezone.utc),
            )
        )

    async def report_progress(
        self, submission_id: UUID, *, step: str, progress_percent: int
    ) -> AnalysisRun:
        if not 0 <= progress_percent <= 99:
            raise ValueError("Progress must be between 0 and 99 while analysis is running")
        run = await self._latest_run(submission_id)
        if run.status != AnalysisStatus.ANALYZING:
            raise InvalidAnalysisTransitionError("Only running analysis can report progress")
        return await self._repository.update_analysis_run(
            replace(run, current_step=step, progress_percent=progress_percent)
        )

    async def complete(
        self,
        submission_id: UUID,
        *,
        findings: list[ReviewFinding],
        review_context_snapshot: dict[str, object] | None = None,
    ) -> AnalysisRun:
        run = await self._latest_run(submission_id)
        if run.status != AnalysisStatus.ANALYZING:
            raise InvalidAnalysisTransitionError("Only running analysis can be completed")
        return await self._repository.update_analysis_run(
            replace(
                run,
                status=AnalysisStatus.COMPLETED,
                current_step="REVIEW_QUEUE_READY",
                progress_percent=100,
                completed_at=datetime.now(timezone.utc),
                findings=findings,
                review_context_snapshot=review_context_snapshot or {},
            )
        )

    async def fail(self, submission_id: UUID, *, message: str) -> AnalysisRun:
        run = await self._latest_run(submission_id)
        if run.status not in {AnalysisStatus.QUEUED, AnalysisStatus.ANALYZING}:
            raise InvalidAnalysisTransitionError("Only pending or running analysis can fail")
        return await self._repository.update_analysis_run(
            replace(
                run,
                status=AnalysisStatus.FAILED,
                current_step="FAILED",
                error_message=message[:1_000],
                completed_at=datetime.now(timezone.utc),
            )
        )

    async def _latest_run(self, submission_id: UUID) -> AnalysisRun:
        submission = await self._repository.find_by_id(submission_id)
        if not submission:
            raise LookupError("Content submission not found")
        return submission.latest_analysis
