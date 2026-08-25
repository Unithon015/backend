from uuid import UUID

from src.application.content.analysis_service import ContentAnalysisService
from src.application.content.service import ContentStorage
from src.domain.content.entity import AssetType
from src.infrastructure.content.pg_repository import PostgresContentSubmissionRepository
from src.infrastructure.openai.analyzer import analyze


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
            await service.start(submission_id, step="ANALYZING")
            submission = await repo.find_by_id(submission_id)
            assert submission

            images = await _read_images(submission.assets, storage)
            findings = await analyze(
                text=submission.caption_text or None,
                images=images if images else None,
                api_key=api_key,
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
