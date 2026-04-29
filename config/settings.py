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
# Prioritizing the Gemini/AI Studio key for our "Expert" bot
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
# Others default to empty as we are using mock/local data for hackathon stability
GOOGLE_CIVIC_API_KEY = os.getenv("GOOGLE_CIVIC_API_KEY", "")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY", "")

# ── Supported Countries (India First & Detailed) ──────────────────────────────
SUPPORTED_COUNTRIES: dict[str, dict] = {
    "IN": {
        "name": "India",
        "flag": "🇮🇳",
        "civic_api_supported": False, # We use local JSON for better accuracy
        "election_body": "Election Commission of India (ECI)",
        "official_url": "https://eci.gov.in",
        "voter_portal": "https://voters.eci.gov.in",
        # Expanded Indian languages for localization
        "languages": ["en", "hi", "bn", "te", "mr", "ta", "gu"],
        "voting_age": 18,
        "id_required": True,
        "primary_id": "EPIC (Voter ID Card)",
    },
    "US": {
        "name": "United States",
        "flag": "🇺🇸",
        "civic_api_supported": True,
        "election_body": "Federal Election Commission (FEC)",
        "official_url": "https://www.usa.gov/voting",
        "languages": ["en", "es"],
        "voting_age": 18,
        "id_required": True,
    },
    "UK": {
        "name": "United Kingdom",
        "flag": "🇬🇧",
        "election_body": "Electoral Commission",
        "official_url": "https://www.electoralcommission.org.uk",
        "languages": ["en"],
        "voting_age": 18,
        "id_required": True,
    }
}

# ── Election Types (Localized for India) ──────────────────────────────────────
ELECTION_TYPES = [
    "Lok Sabha (General Election)",
    "Vidhan Sabha (State Assembly)",
    "Rajya Sabha Election",
    "Panchayat / Municipal Election",
    "By-Election",
]

# ── India-Specific Constants ──────────────────────────────────────────────────
# Helpful for the AI Assistant and UI components
INDIA_CONSTANTS = {
    "EPIC_SEARCH_URL": "https://electoralsearch.eci.gov.in/",
    "FORM_6_URL": "https://voters.eci.gov.in/registration-details?formCode=FORM6",
    "KNOW_YOUR_CANDIDATE": "https://affidavit.eci.gov.in/",
    "VOTER_HELPLINE": "1950",
}

# ── Caching ───────────────────────────────────────────────────────────────────
CACHE_TTL_SECONDS = {
    "election_data": 3600,      # 1 hour
    "polling_stations": 86400,  # 24 hours
    "ai_responses": 1800,       # 30 minutes
    "location_lookup": 86400,   # 24 hours
}