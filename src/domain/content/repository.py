from abc import ABC, abstractmethod
from uuid import UUID

from .entity import AnalysisRun, ContentSubmission, FindingStatus


class ContentSubmissionRepository(ABC):
    @abstractmethod
    async def save(self, submission: ContentSubmission) -> ContentSubmission: ...

    @abstractmethod
    async def find_by_id(self, submission_id: UUID) -> ContentSubmission | None: ...

    @abstractmethod
    async def list_recent(self, limit: int) -> list[ContentSubmission]: ...

    @abstractmethod
    async def update_analysis_run(self, analysis_run: AnalysisRun) -> AnalysisRun: ...

    @abstractmethod
    async def update_finding_status(self, finding_id: UUID, status: FindingStatus) -> None: ...

    @abstractmethod
    async def list_by_owner(self, owner_id: UUID, limit: int) -> list[ContentSubmission]: ...

    @abstractmethod
    async def update_title(self, submission_id: UUID, title: str) -> None: ...
