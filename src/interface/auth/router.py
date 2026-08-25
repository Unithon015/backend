from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.infrastructure.user.pg_repository import PostgresUserRepository
from src.infrastructure.google.client import get_login_url
from src.application.auth.service import GoogleAuthService
from src.application.auth.dto import TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def _service(db: AsyncSession = Depends(get_db)) -> GoogleAuthService:
    return GoogleAuthService(PostgresUserRepository(db))


@router.get("/google/login")
def google_login():
    return RedirectResponse(get_login_url())


@router.get("/google/callback")
async def google_callback(code: str, service: GoogleAuthService = Depends(_service)):
    token = await service.login(code)
    return RedirectResponse(f"http://localhost:5173?token={token.access_token}")
