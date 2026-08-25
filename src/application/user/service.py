from uuid import UUID
from src.domain.user.entity import User
from src.domain.user.repository import UserRepository
from .dto import CreateUserRequest, UserResponse


class UserService:
    def __init__(self, repo: UserRepository):
        self._repo = repo

    async def create(self, req: CreateUserRequest) -> UserResponse:
        user = await self._repo.save(
            User(email=req.email, name=req.name, provider="local", provider_id="")
        )
        return UserResponse(id=user.id, email=user.email, name=user.name)

    async def get(self, user_id: UUID) -> UserResponse | None:
        user = await self._repo.find_by_id(user_id)
        return UserResponse(id=user.id, email=user.email, name=user.name) if user else None

    async def list_all(self) -> list[UserResponse]:
        return [UserResponse(id=u.id, email=u.email, name=u.name) for u in await self._repo.find_all()]
