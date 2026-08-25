from uuid import UUID
from src.domain.user.entity import User
from src.domain.user.repository import UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._store: dict[UUID, User] = {}

    async def save(self, user: User) -> User:
        self._store[user.id] = user
        return user

    async def find_by_id(self, user_id: UUID) -> User | None:
        return self._store.get(user_id)

    async def find_by_email(self, email: str) -> User | None:
        return next((u for u in self._store.values() if u.email == email), None)

    async def find_all(self) -> list[User]:
        return list(self._store.values())
