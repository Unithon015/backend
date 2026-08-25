from uuid import UUID

from src.application.content.analysis_service import ContentAnalysisService
from src.infrastructure.content.pg_repository import PostgresContentSubmissionRepository
from src.infrastructure.openai.text_analyzer import analyze_text


async def run_text_analysis(submission_id: UUID, caption_text: str, *, api_key: str) -> None:
    from src.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        repo = PostgresContentSubmissionRepository(db)
        service = ContentAnalysisService(repo)
        try:
            await service.start(submission_id, step="TEXT_ANALYSIS")
            findings = await analyze_text(caption_text, api_key=api_key)
            await service.complete(submission_id, findings=findings)
        except Exception as exc:
            await service.fail(submission_id, message=str(exc))
