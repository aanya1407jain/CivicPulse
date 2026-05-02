"""
CivicPulse — India-Centric Civic Information Service
====================================================
Localized to prioritize ECI (Election Commission of India) data.

Google Civic Information API (civicinfo.googleapis.com) is used when
GOOGLE_CIVIC_API_KEY is set. Falls back to local JSON for Indian elections
since the Civic API has limited India coverage.

Architecture:
    1. For India (IN): Local JSON → ECI portal links (Civic API not needed)
    2. For US/UK:      Google Civic Information API → local JSON fallback
"""

from __future__ import annotations
import json
import logging
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Any

import streamlit as st

from config.settings import INDIA, CACHE_TTL, GOOGLE_CIVIC_API_KEY

logger = logging.getLogger(__name__)

_LOCAL_DATA_PATH = Path("global_elections_2025_2030.json")
_CIVIC_API_BASE  = "https://www.googleapis.com/civicinfo/v2"


@st.cache_data(ttl=CACHE_TTL["election_data"], show_spinner=False)
def _load_local_json() -> dict:
    """Load the elections JSON once and cache for 1 hour."""
    try:
        with open(_LOCAL_DATA_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        logger.error("elections JSON not found at %s", _LOCAL_DATA_PATH)
        return {}
    except json.JSONDecodeError as exc:
        logger.error("Malformed elections JSON: %s", exc)
        return {}


@st.cache_data(ttl=CACHE_TTL["election_data"], show_spinner=False)
def _fetch_civic_api(address: str) -> dict | None:
    """
    Call the Google Civic Information API for a given address.
    Returns parsed JSON on success, None on failure or missing key.
    """
    if not GOOGLE_CIVIC_API_KEY:
        return None
    try:
        params = urllib.parse.urlencode({
            "key":     GOOGLE_CIVIC_API_KEY,
            "address": address,
        })
        url = f"{_CIVIC_API_BASE}/voterinfo?{params}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        logger.info("Civic API HTTP error for '%s': %s", address, exc.code)
        return None
    except Exception as exc:
        logger.warning("Civic API fetch failed for '%s': %s", address, exc)
        return None


@st.cache_data(ttl=CACHE_TTL["election_data"], show_spinner=False)
def _fetch_civic_representatives(address: str) -> dict | None:
    """
    Call the Civic API representatives endpoint.
    Useful for US/UK elections where full representative data is available.
    """
    if not GOOGLE_CIVIC_API_KEY:
        return None
    try:
        params = urllib.parse.urlencode({
            "key":     GOOGLE_CIVIC_API_KEY,
            "address": address,
        })
        url = f"{_CIVIC_API_BASE}/representatives?{params}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read())
    except Exception as exc:
        logger.warning("Civic representatives fetch failed: %s", exc)
        return None


class CivicAPIService:
    """
    Service to fetch election and voter information.
    - India:  Local JSON + ECI portal links (Civic API has limited India coverage)
    - US/UK:  Google Civic Information API with local JSON fallback
    """

    def __init__(self, api_key: str = GOOGLE_CIVIC_API_KEY) -> None:
        self.api_key  = api_key
        self.has_key  = bool(api_key)

    # ── Public Methods ────────────────────────────────────────────────────────

    def get_election_details(self, country_code: str, state_code: str = "DEFAULT") -> dict:
        """Fetch election data — Civic API for US/UK, local JSON for India."""
        if country_code != "IN" and self.has_key:
            civic_data = _fetch_civic_api(state_code)
            if civic_data:
                return self._parse_civic_election(civic_data)

        full_data    = _load_local_json()
        country_info = dict(full_data.get("country_data", {}).get(country_code, {}))

        if not country_info:
            logger.info("No data for country '%s'; returning India fallback.", country_code)
            return self._get_fallback_india_data()

        if country_code == INDIA["COUNTRY_CODE"]:
            country_info["election_body"] = "Election Commission of India (ECI)"
            country_info["helpline"]      = INDIA["VOTER_HELPLINE"]

        return country_info

    def get_voter_info(self, location: str) -> dict:
        """Return localized ECI portal links for the given location."""
        # Try Civic API for non-India addresses
        if not any(c.isdigit() for c in location[:3]):
            civic = _fetch_civic_api(location)
            if civic and "pollingLocations" in civic:
                return {
                    "status":        "success",
                    "jurisdiction":  location,
                    "source":        "google_civic_api",
                    "polling_locations": civic.get("pollingLocations", []),
                    "contests":      civic.get("contests", []),
                }

        return {
            "status":       "success",
            "jurisdiction": location,
            "source":       "eci_local",
            "voter_portal": INDIA["VOTER_PORTAL_URL"],
            "booth_locator": INDIA["EPIC_SEARCH_URL"],
            "message": (
                "Use the ECI Voter Search portal to find your specific booth "
                "using your EPIC number."
            ),
        }

    def get_representatives(self, address: str) -> dict | None:
        """
        Fetch elected representatives for an address via the Civic API.
        Returns None when no key is configured or request fails.
        """
        return _fetch_civic_representatives(address)

    def get_polling_locations(self, location: str) -> list[dict]:
        """Return polling location examples (ECI-sourced for India)."""
        return [
            {
                "name":       "Government Primary School (Polling Station)",
                "address":    f"Block 4, Central Area, {location}",
                "hours":      "7:00 AM – 6:00 PM",
                "notes":      "Wheelchair accessible. Queue assistance for PwD/Seniors.",
                "accessible": True,
            },
            {
                "name":       "Community Hall / Panchayat Bhawan",
                "address":    f"Main Road Near Post Office, {location}",
                "hours":      "7:00 AM – 6:00 PM",
                "notes":      "VVPAT enabled booth.",
                "accessible": True,
            },
        ]

    # ── Private Helpers ───────────────────────────────────────────────────────

    def _parse_civic_election(self, civic_data: dict) -> dict:
        """Parse a Google Civic API response into our standard format."""
        elections = civic_data.get("elections", [])
        if elections:
            e = elections[0]
            return {
                "election_name":     e.get("name", "Election"),
                "next_election_date": e.get("electionDay", ""),
                "jurisdiction":      e.get("ocdDivisionId", ""),
                "source":            "google_civic_api",
            }
        return self._get_fallback_india_data()

    def _get_fallback_india_data(self) -> dict:
        """Standard India-centric fallback when all sources fail."""
        return {
            "election_name":     "General Election to Lok Sabha",
            "country_name":      "India",
            "next_election_date": "2029-05-01",
            "requirements": [
                "Indian Citizen",
                "18 years or older",
                "Registered in Electoral Roll",
                "Must possess Voter ID or 12 approved alternatives",
            ],
        }
