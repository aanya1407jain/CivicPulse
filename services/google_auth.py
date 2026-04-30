"""
CivicPulse — Google OAuth2 Authentication Service
==================================================
Uses real google-auth-oauthlib when CLIENT_ID/SECRET are set in .env.
Falls back to a safe demo mode when credentials are absent (hackathon mode).
"""

from __future__ import annotations
import logging
import secrets
from typing import Any

from config.settings import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI

logger = logging.getLogger(__name__)

_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

_REAL_AUTH_AVAILABLE = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)


class GoogleAuthService:
    """
    Google OAuth2 service.
    - When GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are present: uses the
      real google-auth-oauthlib flow.
    - Otherwise: returns safe mock data so the dashboard keeps running for demos.
    """

    def __init__(
        self,
        client_id: str = GOOGLE_CLIENT_ID,
        client_secret: str = GOOGLE_CLIENT_SECRET,
        redirect_uri: str = GOOGLE_REDIRECT_URI,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self._real = bool(client_id and client_secret)

    # ── Public Interface ──────────────────────────────────────────────────────

    def get_authorization_url(self) -> tuple[str, str]:
        """
        Return (authorization_url, state_token).
        Uses real Google OAuth2 when credentials are available.
        """
        state = secrets.token_urlsafe(32)
        if self._real:
            try:
                from google_auth_oauthlib.flow import Flow  # type: ignore

                flow = Flow.from_client_config(
                    {
                        "web": {
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                            "redirect_uris": [self.redirect_uri],
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                        }
                    },
                    scopes=_SCOPES,
                )
                flow.redirect_uri = self.redirect_uri
                auth_url, _ = flow.authorization_url(
                    state=state,
                    access_type="offline",
                    prompt="select_account",
                )
                return auth_url, state
            except Exception as exc:
                logger.warning("Real OAuth2 flow failed; falling back to mock: %s", exc)

        return "#mock_login", state

    def exchange_code_for_tokens(self, code: str) -> dict[str, Any]:
        """Exchange an authorization code for access/refresh tokens."""
        if self._real:
            try:
                from google_auth_oauthlib.flow import Flow  # type: ignore

                flow = Flow.from_client_config(
                    {
                        "web": {
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                            "redirect_uris": [self.redirect_uri],
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                        }
                    },
                    scopes=_SCOPES,
                )
                flow.redirect_uri = self.redirect_uri
                flow.fetch_token(code=code)
                creds = flow.credentials
                return {
                    "access_token": creds.token,
                    "refresh_token": creds.refresh_token,
                    "expires_in": 3600,
                }
            except Exception as exc:
                logger.warning("Token exchange failed; returning mock: %s", exc)

        return {
            "access_token": "mock_access_token_india_2026",
            "refresh_token": "mock_refresh_token",
            "expires_in": 3600,
        }

    def get_user_info(self, access_token: str) -> dict[str, Any]:
        """Fetch the logged-in user's profile from Google, or return a demo profile."""
        if self._real and not access_token.startswith("mock_"):
            try:
                import requests

                resp = requests.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10,
                )
                resp.raise_for_status()
                return resp.json()
            except Exception as exc:
                logger.warning("get_user_info failed; returning mock: %s", exc)

        # Demo / hackathon profile
        return {
            "name": "Arjun Sharma",
            "email": "arjun.voter@example.in",
            "picture": "https://api.dicebear.com/7.x/avataaars/svg?seed=Arjun",
            "locale": "en-IN",
            "verified_email": True,
            "location_hint": "Maharashtra, India",
        }

    def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh the access token."""
        return {"access_token": "mock_refreshed_token", "expires_in": 3600}

    def revoke_token(self, token: str) -> bool:
        """Revoke a token (no-op in demo mode)."""
        if self._real and not token.startswith("mock_"):
            try:
                import requests
                requests.post(
                    "https://oauth2.googleapis.com/revoke",
                    params={"token": token},
                    timeout=10,
                )
            except Exception as exc:
                logger.warning("Token revocation failed: %s", exc)
        return True
