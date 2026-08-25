from datetime import datetime, timedelta, timezone
from jose import jwt
from src import config
from src.domain.user.entity import User
from src.domain.user.repository import UserRepository
from src.infrastructure.google import client as google
from .dto import TokenResponse


class GoogleAuthService:
    def __init__(self, repo: UserRepository):
        self._repo = repo

    async def login(self, code: str) -> TokenResponse:
        tokens = await google.exchange_code(code)
        user_info = await google.get_user_info(tokens["access_token"])

        email = user_info["email"]
        user = await self._repo.find_by_email(email)
        if not user:
            user = await self._repo.save(User(
                email=email,
                name=user_info.get("name", email),
                provider="google",
                provider_id=user_info["sub"],
            ))

        return TokenResponse(access_token=self._issue_jwt(user))

    def _issue_jwt(self, user: User) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=config.JWT_EXPIRE_MINUTES)
        return jwt.encode(
            {"sub": str(user.id), "email": user.email, "exp": expire},
            config.JWT_SECRET,
            algorithm=config.JWT_ALGORITHM,
        )
