"""
CivicPulse — India-Centric Civic Information Service
====================================================
Localized to prioritize ECI (Election Commission of India) data.
Uses local JSON as the source of truth for Indian elections.
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any

import streamlit as st

from config.settings import INDIA, CACHE_TTL

logger = logging.getLogger(__name__)

_LOCAL_DATA_PATH = Path("global_elections_2025_2030.json")


@st.cache_data(ttl=CACHE_TTL["election_data"], show_spinner=False)
def _load_local_json() -> dict:
    """
    Load the elections JSON once and cache for 1 hour.
    Decorated at module level so Streamlit can hash the result correctly.
    """
    try:
        with open(_LOCAL_DATA_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        logger.error("elections JSON not found at %s", _LOCAL_DATA_PATH)
        return {}
    except json.JSONDecodeError as exc:
        logger.error("Malformed elections JSON: %s", exc)
        return {}


class CivicAPIService:
    """
    Service to fetch election and voter information.
    Optimized for Indian elections — local JSON is the source of truth.
    """

    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key

    # ── Public Methods ────────────────────────────────────────────────────────

    def get_election_details(self, country_code: str, state_code: str = "DEFAULT") -> dict:
        """Fetch election data from cached local JSON."""
        full_data = _load_local_json()
        country_info: dict = full_data.get("country_data", {}).get(country_code, {})

        if not country_info:
            logger.info("No data for country '%s'; returning India fallback.", country_code)
            return self._get_fallback_india_data()

        # Augment India data with ECI meta
        if country_code == INDIA["COUNTRY_CODE"]:
            country_info = dict(country_info)   # don't mutate the cached object
            country_info["election_body"] = "Election Commission of India (ECI)"
            country_info["helpline"] = INDIA["VOTER_HELPLINE"]

        return country_info

    def get_voter_info(self, location: str) -> dict:
        """Return localized ECI portal links for the given location."""
        return {
            "status": "success",
            "jurisdiction": location,
            "voter_portal": INDIA["VOTER_PORTAL_URL"],
            "booth_locator": INDIA["EPIC_SEARCH_URL"],
            "message": (
                "Use the ECI Voter Search portal to find your specific booth "
                "using your EPIC number."
            ),
        }

    def get_polling_locations(self, location: str) -> list[dict]:
        """
        Return representative polling location examples for Indian demos.
        A real implementation would call the ECI or Maps API with coordinates.
        """
        return [
            {
                "name": "Government Primary School (Polling Station)",
                "address": f"Block 4, Central Area, {location}",
                "hours": "7:00 AM – 6:00 PM",
                "notes": "Wheelchair accessible. Queue assistance for PwD/Seniors.",
                "accessible": True,
            },
            {
                "name": "Community Hall / Panchayat Bhawan",
                "address": f"Main Road Near Post Office, {location}",
                "hours": "7:00 AM – 6:00 PM",
                "notes": "VVPAT enabled booth.",
                "accessible": True,
            },
        ]

    # ── Private Helpers ───────────────────────────────────────────────────────

    def _get_fallback_india_data(self) -> dict:
        """Standard India-centric fallback when JSON is unavailable."""
        return {
            "election_name": "General Election to Lok Sabha",
            "country_name": "India",
            "next_election_date": "2029-05-01",
            "requirements": [
                "Indian Citizen",
                "18 years or older",
                "Registered in Electoral Roll",
                "Must possess Voter ID or 12 approved alternatives",
            ],
        }
