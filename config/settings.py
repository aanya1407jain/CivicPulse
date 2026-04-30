"""
CivicPulse — India-Centric Application Configuration
"""

from __future__ import annotations
import os
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
ASSETS_DIR = ROOT_DIR / "assets"

# ── Application Meta ──────────────────────────────────────────────────────────
APP_CONFIG = {
    "name": "CivicPulse India",
    "version": "2.0.0-IN",
    "description": "Localized Election Intelligence for Indian Citizens",
    "author": "CivicPulse Hackathon Team",
    "github": "https://github.com/your-username/civicpulse",
}

# ── Google API Keys ───────────────────────────────────────────────────────────
GOOGLE_API_KEY          = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CIVIC_API_KEY    = os.getenv("GOOGLE_CIVIC_API_KEY", "")
GOOGLE_MAPS_API_KEY     = os.getenv("GOOGLE_MAPS_API_KEY", "")
GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY", "")

# OAuth2 credentials (used by google_auth.py for real login)
GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI  = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501")

# ── India Constants (single source of truth — never scatter these) ────────────
INDIA = {
    "COUNTRY_CODE":        "IN",
    "TIMEZONE":            "Asia/Kolkata",
    "VOTER_HELPLINE":      "1950",
    "EPIC_SEARCH_URL":     "https://electoralsearch.eci.gov.in/",
    "VOTER_PORTAL_URL":    "https://voters.eci.gov.in/",
    "ECI_MAIN_URL":        "https://eci.gov.in/",
    "FORM_6_URL":          "https://voters.eci.gov.in/registration-details?formCode=FORM6",
    "FORM_8_URL":          "https://voters.eci.gov.in/registration-details?formCode=FORM8",
    "KNOW_YOUR_CANDIDATE": "https://affidavit.eci.gov.in/",
    "VOTER_APP_PLAYSTORE": "https://play.google.com/store/apps/details?id=com.eci.citizen",
    "SMS_NUMBER":          "1950",
    "MOCK_FALLBACK_LAT":   28.6139,
    "MOCK_FALLBACK_LNG":   77.2090,
    "MOCK_FALLBACK_ADDR":  "New Delhi, India (Demo Mode)",
    "DEFAULT_STATE_CODE":  "DEFAULT",
}

# Keep the old name as an alias so existing imports don't break
INDIA_CONSTANTS = {
    "EPIC_SEARCH_URL":     INDIA["EPIC_SEARCH_URL"],
    "FORM_6_URL":          INDIA["FORM_6_URL"],
    "KNOW_YOUR_CANDIDATE": INDIA["KNOW_YOUR_CANDIDATE"],
    "VOTER_HELPLINE":      INDIA["VOTER_HELPLINE"],
}

# ── Supported Countries (India First & Detailed) ──────────────────────────────
SUPPORTED_COUNTRIES: dict[str, dict] = {
    "IN": {
        "name":               "India",
        "flag":               "🇮🇳",
        "civic_api_supported": False,
        "election_body":      "Election Commission of India (ECI)",
        "official_url":       INDIA["ECI_MAIN_URL"],
        "voter_portal":       INDIA["VOTER_PORTAL_URL"],
        "languages":          ["en", "hi", "bn", "te", "mr", "ta", "gu"],
        "voting_age":         18,
        "id_required":        True,
        "primary_id":         "EPIC (Voter ID Card)",
        "compulsory_voting":  False,
    },
    "US": {
        "name":               "United States",
        "flag":               "🇺🇸",
        "civic_api_supported": True,
        "election_body":      "Federal Election Commission (FEC)",
        "official_url":       "https://www.usa.gov/voting",
        "languages":          ["en", "es"],
        "voting_age":         18,
        "id_required":        True,
        "compulsory_voting":  False,
    },
    "UK": {
        "name":               "United Kingdom",
        "flag":               "🇬🇧",
        "election_body":      "Electoral Commission",
        "official_url":       "https://www.electoralcommission.org.uk",
        "languages":          ["en"],
        "voting_age":         18,
        "id_required":        True,
        "compulsory_voting":  False,
    },
}

# ── Election Types ─────────────────────────────────────────────────────────────
ELECTION_TYPES = [
    "Lok Sabha (General Election)",
    "Vidhan Sabha (State Assembly)",
    "Rajya Sabha Election",
    "Panchayat / Municipal Election",
    "By-Election",
]

# ── Caching TTLs (seconds) ────────────────────────────────────────────────────
CACHE_TTL = {
    "election_data":     3600,    # 1 hour
    "polling_stations":  86400,   # 24 hours
    "ai_responses":      1800,    # 30 minutes
    "location_lookup":   86400,   # 24 hours
}
# Legacy alias
CACHE_TTL_SECONDS = CACHE_TTL

# ── Gemini Model ──────────────────────────────────────────────────────────────
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_MAX_TOKENS = 512
