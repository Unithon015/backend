from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.content.entity import AnalysisStatus, AssetType, EvidenceLayer, ReviewPriority


class ContentAssetResponse(BaseModel):
    id: UUID
    content_type: AssetType
    original_filename: str
    mime_type: str
    byte_size: int
    download_url: str


class ContentSubmissionResponse(BaseModel):
    id: UUID
    title: str
    caption_text: str | None
    status: AnalysisStatus
    type: list[str]
    assets: list[ContentAssetResponse]
    created_at: datetime


class RecentContentResponse(BaseModel):
    items: list[ContentSubmissionResponse]


class FindingEvidenceResponse(BaseModel):
    id: UUID
    layer: EvidenceLayer
    title: str
    source_url: str
    excerpt: str | None
    provider: str | None


class ReviewFindingResponse(BaseModel):
    id: UUID
    type: str
    category_code: str = Field(description="R-01 through R-08 review category")
    priority: ReviewPriority
    signal_type: str
    reason: str
    excerpt: str | None
    asset_id: UUID | None
    start_ms: int | None
    end_ms: int | None
    evidences: list[FindingEvidenceResponse]


class AnalysisStatusResponse(BaseModel):
    id: UUID
    type: list[str]
    status: AnalysisStatus
    current_step: str | None
    progress_percent: int = Field(ge=0, le=100)
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    findings: list[ReviewFindingResponse]
