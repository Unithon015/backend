from uuid import UUID
from fastapi import APIRouter, HTTPException
from src.application.user.dto import CreateUserRequest, UserResponse
from src.application.user.service import UserService
from src.infrastructure.user.repository import InMemoryUserRepository

router = APIRouter(prefix="/users", tags=["users"])

# ponytail: global singleton repo, swap with DI container when adding real DB
_service = UserService(InMemoryUserRepository())


@router.post("", response_model=UserResponse, status_code=201)
def create_user(req: CreateUserRequest):
    return _service.create(req)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID):
    user = _service.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("", response_model=list[UserResponse])
def list_users():
    return _service.list_all()
