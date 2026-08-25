from uuid import UUID

from src.application.content.analysis_service import ContentAnalysisService
from src.application.content.service import ContentStorage
from src.domain.content.entity import AssetType
from src.infrastructure.content.pg_repository import PostgresContentSubmissionRepository
from src.infrastructure.openai.analyzer import analyze_general, analyze_references
from src.infrastructure.policy_catalog.context import search_relevant_reference_context


async def run_analysis(
    submission_id: UUID,
    *,
    api_key: str,
    storage: ContentStorage,
) -> None:
    from src.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        repo = PostgresContentSubmissionRepository(db)
        service = ContentAnalysisService(repo)
        try:
            await service.start(submission_id, step="GENERAL_REVIEW")
            submission = await repo.find_by_id(submission_id)
            assert submission

            images = await _read_images(submission.assets, storage)
            general_result = await analyze_general(
                text=submission.caption_text or None,
                images=images if images else None,
                api_key=api_key,
            )
            if general_result.title:
                await repo.update_title(submission_id, general_result.title)
            if general_result.findings:
                await service.complete(submission_id, findings=general_result.findings)
                return

            await service.report_progress(
                submission_id,
                step="REFERENCE_SEARCH",
                progress_percent=55,
            )
            query_text = general_result.retrieval_query(submission.caption_text)
            policy_context, incident_context = await search_relevant_reference_context(
                db,
                query_text,
            )
            if not policy_context and not incident_context:
                await service.complete(submission_id, findings=[])
                return

            await service.report_progress(
                submission_id,
                step="REFERENCE_REVIEW",
                progress_percent=75,
            )
            findings = await analyze_references(
                text=submission.caption_text or None,
                images=images if images else None,
                api_key=api_key,
                policy_context=policy_context,
                incident_context=incident_context,
            )
            await service.complete(submission_id, findings=findings)
        except Exception as exc:
            await service.fail(submission_id, message=str(exc))


async def _read_images(assets, storage: ContentStorage) -> list[tuple[bytes, str]]:
    result = []
    for asset in assets:
        if asset.content_type != AssetType.IMAGE:
            continue
        try:
            data = await storage.read_bytes(asset.storage_key)
            result.append((data, asset.mime_type))
        except Exception:
            pass
    return result
