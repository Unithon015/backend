from uuid import UUID

from src.application.content.analysis_service import ContentAnalysisService
from src.application.content.review_context import snapshot_for_audit
from src.infrastructure.audience_profile.pg_repository import PostgresAudienceProfileRepository
from src.infrastructure.content.pg_repository import PostgresContentSubmissionRepository
from src.infrastructure.openai.text_analyzer import analyze_text
from src.infrastructure.review_context.resolver import DatabaseReviewContextResolver


async def run_text_analysis(submission_id: UUID, caption_text: str, *, api_key: str) -> None:
    from src.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        repo = PostgresContentSubmissionRepository(db)
        service = ContentAnalysisService(repo)
        try:
            await service.start(submission_id, step="TEXT_ANALYSIS")
            submission = await repo.find_by_id(submission_id)
            assert submission
            audience_profile = None
            if submission.owner_id:
                audience_profile = await PostgresAudienceProfileRepository(db).find_by_user_id(
                    submission.owner_id
                )
            review_context = await DatabaseReviewContextResolver(db).resolve(audience_profile)
            findings = await analyze_text(
                caption_text,
                audience_profile=audience_profile,
                review_context=review_context,
                api_key=api_key,
            )
            await service.complete(
                submission_id,
                findings=findings,
                review_context_snapshot=snapshot_for_audit(audience_profile, review_context),
            )
        except Exception as exc:
            await service.fail(submission_id, message=str(exc))
