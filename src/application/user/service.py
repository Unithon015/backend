from uuid import UUID
from src.domain.user.entity import User
from src.domain.user.repository import UserRepository
from .dto import CreateUserRequest, UserResponse


class UserService:
    def __init__(self, repo: UserRepository):
        self._repo = repo

    def create(self, req: CreateUserRequest) -> UserResponse:
        user = self._repo.save(User(email=req.email, name=req.name))
        return UserResponse(id=user.id, email=user.email, name=user.name)

    def get(self, user_id: UUID) -> UserResponse | None:
        user = self._repo.find_by_id(user_id)
        return UserResponse(id=user.id, email=user.email, name=user.name) if user else None

    def list_all(self) -> list[UserResponse]:
        return [UserResponse(id=u.id, email=u.email, name=u.name) for u in self._repo.find_all()]
