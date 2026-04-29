"""
CivicPulse — Mock Authentication Service
=========================================
Simplified for Hackathon use. Simulates Google Login for Indian users
to demonstrate personalized election journeys without requiring OAuth2 credentials.
"""

from __future__ import annotations
import logging
import secrets
from typing import Any

logger = logging.getLogger(__name__)

class GoogleAuthService:
    """
    Simulated Auth Service. 
    Allows the demo to proceed with a 'Mock' Indian User Profile.
    """

    def __init__(
        self,
        client_id: str = "MOCK_ID",
        client_secret: str = "MOCK_SECRET",
        redirect_uri: str = "http://localhost:8501",
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_authorization_url(self) -> tuple[str, str]:
        """
        In a real app, this redirects to Google. 
        For the hackathon, we return a local redirect or a success flag.
        """
        state = secrets.token_urlsafe(32)
        # We return a dummy URL that your app.py can catch to 'simulate' login
        return "#mock_login", state

    def exchange_code_for_tokens(self, code: str) -> dict[str, Any]:
        """Returns a fake token to keep the app running."""
        return {
            "access_token": "mock_access_token_india_2026",
            "refresh_token": "mock_refresh_token",
            "expires_in": 3600
        }

    def get_user_info(self, access_token: str) -> dict[str, Any]:
        """
        Returns a personalized Indian Voter profile for the demo.
        This makes your dashboard look 'live' and personalized.
        """
        return {
            "name": "Arjun Sharma",
            "email": "arjun.voter@example.in",
            "picture": "https://api.dicebear.com/7.x/avataaars/svg?seed=Arjun", # Placeholder avatar
            "locale": "en-IN",
            "verified_email": True,
            "location_hint": "Maharashtra, India"
        }

    def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        return {"access_token": "mock_refreshed_token", "expires_in": 3600}

    def revoke_token(self, token: str) -> bool:
        return True