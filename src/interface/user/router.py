from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.user.dto import UserResponse
from src.application.user.service import UserService
from src.database import get_db
from src.infrastructure.user.pg_repository import PostgresUserRepository
from src.interface.deps import get_current_user_id

router = APIRouter(prefix="/users", tags=["users"])


def _service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(PostgresUserRepository(db))


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user_id: UUID = Depends(get_current_user_id),
    service: UserService = Depends(_service),
):
    user = await service.get(current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


__all__ = ["router"]
