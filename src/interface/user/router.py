from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.user.dto import CreateUserRequest, UserResponse
from src.application.user.service import UserService
from src.database import get_db
from src.infrastructure.user.pg_repository import PostgresUserRepository

router = APIRouter(prefix="/users", tags=["users"])


def _service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(PostgresUserRepository(db))


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(req: CreateUserRequest, service: UserService = Depends(_service)):
    return await service.create(req)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, service: UserService = Depends(_service)):
    user = await service.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("", response_model=list[UserResponse])
async def list_users(service: UserService = Depends(_service)):
    return await service.list_all()
