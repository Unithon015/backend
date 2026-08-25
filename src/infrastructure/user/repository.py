from uuid import UUID
from src.domain.user.entity import User
from src.domain.user.repository import UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._store: dict[UUID, User] = {}

    def save(self, user: User) -> User:
        self._store[user.id] = user
        return user

    def find_by_id(self, user_id: UUID) -> User | None:
        return self._store.get(user_id)

    def find_all(self) -> list[User]:
        return list(self._store.values())
