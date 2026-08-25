from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src import config
from src.application.content.dto import (
    AnalysisStatusResponse,
    ContentAssetResponse,
    ContentSubmissionResponse,
    FindingEvidenceResponse,
    RecentContentResponse,
    ReviewFindingResponse,
)
from src.application.content.service import (
    ContentSubmissionNotFoundError,
    ContentSubmissionService,
    ContentSubmissionValidationError,
    UploadPayload,
)
from src.application.content.analysis_worker import run_analysis
from src.database import get_db
from src.domain.content.entity import ContentSubmission
from src.infrastructure.content.local_storage import LocalContentStorage
from src.infrastructure.content.pg_repository import PostgresContentSubmissionRepository

router = APIRouter(prefix="/contents", tags=["contents"])


def _storage() -> LocalContentStorage:
    return LocalContentStorage(config.UPLOAD_DIRECTORY)


def _service(db: AsyncSession = Depends(get_db)) -> ContentSubmissionService:
    return ContentSubmissionService(PostgresContentSubmissionRepository(db), _storage())


@router.post("", response_model=ContentSubmissionResponse, status_code=201)
async def create_content(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile | None, File(description="이미지 파일 (선택)")] = None,
    text: Annotated[str | None, Form()] = None,
    service: ContentSubmissionService = Depends(_service),
):
    payloads = []
    if file and file.filename:
        payloads.append(UploadPayload(
            filename=file.filename,
            mime_type=file.content_type or "application/octet-stream",
            content=await file.read(),
        ))
    try:
        submission = await service.create(title=None, caption_text=text, files=payloads)
    except ContentSubmissionValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    has_content = submission.caption_text or submission.assets
    if has_content and config.OPEN_API_KEY:
        background_tasks.add_task(
            run_analysis,
            submission.id,
            api_key=config.OPEN_API_KEY,
            upload_directory=config.UPLOAD_DIRECTORY,
        )

    return _submission_response(submission)


@router.get("", response_model=RecentContentResponse)
async def list_recent_contents(
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    service: ContentSubmissionService = Depends(_service),
):
    submissions = await service.list_recent(limit)
    return RecentContentResponse(items=[_submission_response(submission) for submission in submissions])


@router.get("/{submission_id}", response_model=ContentSubmissionResponse)
async def get_content(
    submission_id: UUID,
    service: ContentSubmissionService = Depends(_service),
):
    return _submission_response(await _get_submission(service, submission_id))


@router.get("/{submission_id}/analysis", response_model=AnalysisStatusResponse)
async def get_analysis_status(
    submission_id: UUID,
    service: ContentSubmissionService = Depends(_service),
):
    submission = await _get_submission(service, submission_id)
    run = submission.latest_analysis

    content_types: list[str] = []
    if submission.caption_text:
        content_types.append("text")
    for asset in submission.assets:
        label = asset.content_type.value.lower()  # "image" or "video"
        if label not in content_types:
            content_types.append(label)

    return AnalysisStatusResponse(
        id=run.id,
        type=content_types,
        status=run.status,
        current_step=run.current_step,
        progress_percent=run.progress_percent,
        error_message=run.error_message,
        started_at=run.started_at,
        completed_at=run.completed_at,
        findings=[
            ReviewFindingResponse(
                id=finding.id,
                type=finding.media_types,
                category_code=finding.category_code,
                priority=finding.priority,
                signal_type=finding.signal_type,
                reason=finding.reason,
                excerpt=finding.excerpt,
                asset_id=finding.asset_id,
                start_ms=finding.start_ms,
                end_ms=finding.end_ms,
                evidences=[
                    FindingEvidenceResponse(
                        id=evidence.id,
                        layer=evidence.layer,
                        title=evidence.title,
                        source_url=evidence.source_url,
                        excerpt=evidence.excerpt,
                        provider=evidence.provider,
                    )
                    for evidence in finding.evidences[:3]
                ],
            )
            for finding in run.findings
        ],
    )


@router.get("/{submission_id}/assets/{asset_id}")
async def download_asset(
    submission_id: UUID,
    asset_id: UUID,
    service: ContentSubmissionService = Depends(_service),
    storage: LocalContentStorage = Depends(_storage),
):
    submission = await _get_submission(service, submission_id)
    asset = next((asset for asset in submission.assets if asset.id == asset_id), None)
    if not asset:
        raise HTTPException(status_code=404, detail="Content asset not found")

    path = storage.resolve_for_download(asset.storage_key)
    if not path.exists():
        raise HTTPException(status_code=410, detail="The original content is no longer available")
    return FileResponse(path, media_type=asset.mime_type, filename=asset.original_filename)


async def _get_submission(
    service: ContentSubmissionService, submission_id: UUID
) -> ContentSubmission:
    try:
        return await service.get(submission_id)
    except ContentSubmissionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Content submission not found") from exc


def _submission_response(submission: ContentSubmission) -> ContentSubmissionResponse:
    return ContentSubmissionResponse(
        id=submission.id,
        title=submission.title,
        caption_text=submission.caption_text,
        status=submission.status,
        created_at=submission.created_at,
        assets=[
            ContentAssetResponse(
                id=asset.id,
                content_type=asset.content_type,
                original_filename=asset.original_filename,
                mime_type=asset.mime_type,
                byte_size=asset.byte_size,
                download_url=f"/contents/{submission.id}/assets/{asset.id}",
            )
            for asset in submission.assets
        ],
    )
