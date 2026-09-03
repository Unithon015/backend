import hmac
from secrets import token_urlsafe

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.infrastructure.user.pg_repository import PostgresUserRepository
from src.infrastructure.google.client import get_login_url
from src.application.auth.service import GoogleAuthService
from src.application.auth.dto import TokenResponse
from src import config

router = APIRouter(prefix="/auth", tags=["auth"])
_OAUTH_STATE_COOKIE = "oauth_state"


def _service(db: AsyncSession = Depends(get_db)) -> GoogleAuthService:
    return GoogleAuthService(PostgresUserRepository(db))


@router.get("/google/login")
def google_login():
    state = token_urlsafe(32)
    response = RedirectResponse(get_login_url(state))
    response.set_cookie(
        _OAUTH_STATE_COOKIE,
        state,
        httponly=True,
        secure=config.ENVIRONMENT in {"production", "prod"},
        samesite="lax",
        max_age=600,
    )
    return response


@router.get("/google/callback")
async def google_callback(
    code: str,
    request: Request,
    state: str | None = None,
    service: GoogleAuthService = Depends(_service),
):
    expected_state = request.cookies.get(_OAUTH_STATE_COOKIE)
    if not state or not expected_state or not hmac.compare_digest(state, expected_state):
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    token = await service.login(code)
    response = RedirectResponse(f"{config.FRONTEND_URL.rstrip('/')}?token={token.access_token}")
    response.delete_cookie(_OAUTH_STATE_COOKIE)
    return response
