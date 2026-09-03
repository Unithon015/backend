from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass(frozen=True)
class AudienceProfile:
    """One account-level review context, configured during onboarding."""

    user_id: UUID
    content_categories: list[str]
    audience_contexts: list[str]
    account_purposes: list[str]
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
