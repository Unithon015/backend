from abc import ABC, abstractmethod
from uuid import UUID
from .entity import User


class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User: ...

    @abstractmethod
    def find_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    def find_all(self) -> list[User]: ...