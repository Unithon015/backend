from pathlib import Path
from uuid import UUID

from src.application.content.analysis_service import ContentAnalysisService
from src.domain.content.entity import AssetType
from src.infrastructure.content.pg_repository import PostgresContentSubmissionRepository
from src.infrastructure.openai.analyzer import analyze


async def run_analysis(
    submission_id: UUID,
    *,
    api_key: str,
    upload_directory: str,
) -> None:
    from src.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        repo = PostgresContentSubmissionRepository(db)
        service = ContentAnalysisService(repo)
        try:
            await service.start(submission_id, step="ANALYZING")
            submission = await repo.find_by_id(submission_id)
            assert submission

            images = _read_images(submission.assets, upload_directory)
            findings = await analyze(
                text=submission.caption_text or None,
                images=images if images else None,
                api_key=api_key,
            )
            await service.complete(submission_id, findings=findings)
        except Exception as exc:
            await service.fail(submission_id, message=str(exc))


def _read_images(assets, upload_directory: str) -> list[tuple[bytes, str]]:
    base = Path(upload_directory).resolve()
    result = []
    for asset in assets:
        if asset.content_type != AssetType.IMAGE:
            continue
        path = (base / asset.storage_key).resolve()
        if path.exists():
            result.append((path.read_bytes(), asset.mime_type))
    return result
