"""
CivicPulse — Pytest Shared Fixtures
=====================================
Shared mocks and sample data used across all test modules.
Eliminates boilerplate from individual test files.
"""

from __future__ import annotations
import pytest
from unittest.mock import MagicMock


# ── Streamlit mock ────────────────────────────────────────────────────────────

@pytest.fixture
def mock_st() -> MagicMock:
    """A MagicMock replacing streamlit with an empty session_state dict."""
    st = MagicMock()
    st.session_state = {}
    return st


# ── Election data fixtures ────────────────────────────────────────────────────

@pytest.fixture
def sample_election_data() -> dict:
    """Minimal election data dict for West Bengal 2026."""
    return {
        "election_name":   "West Bengal Assembly Election 2026",
        "jurisdiction":    "West Bengal",
        "country_name":    "India",
        "counting_day":    "2026-05-04",
        "poll_date":       "2026-04-23",
        "election_type":   "Vidhan Sabha (State Assembly)",
        "total_seats":     294,
        "majority":        148,
    }


@pytest.fixture
def sample_results() -> dict:
    """Minimal results dict mirroring fetch_results() output shape."""
    return {
        "state":        "West Bengal",
        "total_seats":  294,
        "majority":     148,
        "last_updated": "2026-05-04 10:00 IST",
        "parties": [
            {"name": "AITC", "won": 160, "leading": 12, "total": 172, "color": "#27C96E"},
            {"name": "BJP",  "won":  70, "leading":  8, "total":  78, "color": "#FF6B1A"},
            {"name": "Others", "won": 30, "leading": 14, "total": 44, "color": "#9BA3BC"},
        ],
    }


@pytest.fixture
def sample_polling_locations() -> list[dict]:
    """Sample polling station list."""
    return [
        {"name": "Salt Lake School", "address": "Sector V, Kolkata",
         "accessible": True,  "hours": "7:00 AM – 6:00 PM"},
        {"name": "Government College", "address": "Park Street, Kolkata",
         "accessible": False, "hours": "7:00 AM – 6:00 PM"},
    ]


# ── Google API mock helpers ───────────────────────────────────────────────────

@pytest.fixture
def mock_gemini_model() -> MagicMock:
    """A mock Gemini GenerativeModel that returns a canned response."""
    model = MagicMock()
    model.generate_content.return_value = MagicMock(text="Here is your voter information.")
    return model


@pytest.fixture
def mock_maps_service() -> MagicMock:
    """A mock MapsService with pre-set return values."""
    svc = MagicMock()
    svc.geocode.return_value = {
        "lat": 22.5726, "lng": 88.3639,
        "formatted_address": "Kolkata, West Bengal, India",
    }
    svc.find_nearby_polling_booths.return_value = [
        {"name": "Test School", "address": "Test St", "lat": 22.57, "lng": 88.36},
    ]
    return svc


# ── Security test helpers ─────────────────────────────────────────────────────

@pytest.fixture
def xss_payloads() -> list[str]:
    """Common XSS attack strings for security tests."""
    return [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert(1)>",
        "javascript:alert(1)",
        '"><script>alert(document.cookie)</script>',
        "<svg onload=alert(1)>",
    ]


@pytest.fixture
def sql_injection_payloads() -> list[str]:
    """Common SQL injection strings."""
    return [
        "'; DROP TABLE voters; --",
        "1 OR 1=1",
        '" OR ""="',
        "admin'--",
    ]
