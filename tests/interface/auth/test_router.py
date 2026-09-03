import unittest
from urllib.parse import parse_qs, urlparse

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.application.auth.dto import TokenResponse
from src.interface.auth import router as router_module


class _FakeGoogleAuthService:
    async def login(self, code: str) -> TokenResponse:
        return TokenResponse(access_token=f"token-for-{code}")


class GoogleAuthRouterTest(unittest.TestCase):
    def setUp(self):
        app = FastAPI()
        app.include_router(router_module.router)
        app.dependency_overrides[router_module._service] = _FakeGoogleAuthService
        self.client = TestClient(app)

    def test_rejects_a_callback_without_a_matching_state(self):
        response = self.client.get(
            "/auth/google/callback?code=authorization-code&state=wrong",
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 400)

    def test_uses_state_cookie_and_returns_the_frontend_compatible_token(self):
        login = self.client.get("/auth/google/login", follow_redirects=False)
        state = parse_qs(urlparse(login.headers["location"]).query)["state"][0]

        callback = self.client.get(
            f"/auth/google/callback?code=authorization-code&state={state}",
            follow_redirects=False,
        )

        self.assertEqual(callback.status_code, 307)
        self.assertEqual(callback.headers["location"], "http://localhost:5173?token=token-for-authorization-code")
        self.assertIn("oauth_state=\"\"", callback.headers["set-cookie"])
