from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class User:
    email: str
    name: str
    provider: str
    provider_id: str
    id: UUID = field(default_factory=uuid4)
