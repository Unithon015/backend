from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.audience_profile.dto import AudienceProfileResponse, UpsertAudienceProfileRequest
from src.application.audience_profile.service import (
    AudienceProfileNotFoundError,
    AudienceProfileService,
    AudienceProfileUserNotFoundError,
)
from src.database import get_db
from src.interface.deps import get_current_user_id
from src.infrastructure.audience_profile.pg_repository import PostgresAudienceProfileRepository
from src.infrastructure.user.pg_repository import PostgresUserRepository

router = APIRouter(prefix="/users", tags=["audience-profile"])


def _service(db: AsyncSession = Depends(get_db)) -> AudienceProfileService:
    return AudienceProfileService(
        PostgresAudienceProfileRepository(db),
        PostgresUserRepository(db),
    )


@router.get("/me/audience-profile", response_model=AudienceProfileResponse)
async def get_audience_profile(
    current_user_id = Depends(get_current_user_id),
    service: AudienceProfileService = Depends(_service),
):
    try:
        return await service.get(current_user_id)
    except AudienceProfileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Audience profile not found") from exc


@router.put("/me/audience-profile", response_model=AudienceProfileResponse)
async def save_audience_profile(
    request: UpsertAudienceProfileRequest,
    current_user_id = Depends(get_current_user_id),
    service: AudienceProfileService = Depends(_service),
):
    try:
        return await service.save(current_user_id, request)
    except AudienceProfileUserNotFoundError as exc:
        raise HTTPException(status_code=404, detail="User not found") from exc
