from uuid import UUID
from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    email: str
    name: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str