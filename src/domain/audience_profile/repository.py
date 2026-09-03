from abc import ABC, abstractmethod
from uuid import UUID

from .entity import AudienceProfile


class AudienceProfileRepository(ABC):
    @abstractmethod
    async def upsert(self, profile: AudienceProfile) -> AudienceProfile: ...

    @abstractmethod
    async def find_by_user_id(self, user_id: UUID) -> AudienceProfile | None: ...
