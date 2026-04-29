"""
CivicPulse — India-Centric Civic Information Service
====================================================
Localized to prioritize ECI (Election Commission of India) data.
Uses local JSON as the source of truth for Indian elections.
"""

from __future__ import annotations
import logging
import json
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

class CivicAPIService:
    """
    Service to fetch election and voter information.
    Optimized to use local datasets for Indian elections to bypass 
    the need for a paid Google Civic API key.
    """

    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key
        # Path to your local election database
        self.local_data_path = Path("global_elections_2025_2030.json")

    # ── Public Methods ────────────────────────────────────────────────────────

    def get_election_details(self, country_code: str, state_code: str = "DEFAULT") -> dict:
        """
        Main entry point for the dashboard. Fetches data from local JSON.
        """
        try:
            with open(self.local_data_path, 'r', encoding='utf-8') as f:
                full_data = json.load(f)
            
            # Access the 'country_data' section
            country_info = full_data.get("country_data", {}).get(country_code, {})
            
            if not country_info:
                return self._get_fallback_india_data()

            # If it's India, we can add extra context
            if country_code == "IN":
                country_info["election_body"] = "Election Commission of India (ECI)"
                country_info["helpline"] = "1950"

            return country_info

        except Exception as e:
            logger.error(f"Error loading local civic data: {e}")
            return self._get_fallback_india_data()

    def get_voter_info(self, location: str) -> dict:
        """
        In the US version, this calls Google. 
        In our India version, this provides localized ECI portal links.
        """
        return {
            "status": "success",
            "jurisdiction": location,
            "voter_portal": "https://voters.eci.gov.in/",
            "booth_locator": "https://electoralsearch.eci.gov.in/",
            "message": "Use the ECI Voter Search portal to find your specific booth using your EPIC number."
        }

    def get_polling_locations(self, location: str) -> list[dict]:
        """
        Returns 'Mock' polling locations for the demo if a specific PIN is entered.
        """
        # For a hackathon demo, we return structured example data for India
        return [
            {
                "name": "Government Primary School (Polling Station)",
                "address": f"Block 4, Central Area, {location}",
                "hours": "7:00 AM - 6:00 PM",
                "notes": "Wheelchair accessible. Queue assistance for PwD/Seniors available.",
                "accessible": True
            },
            {
                "name": "Community Hall / Panchayat Bhawan",
                "address": f"Main Road Near Post Office, {location}",
                "hours": "7:00 AM - 6:00 PM",
                "notes": "VVPAT enabled booth.",
                "accessible": True
            }
        ]

    # ── Private Helpers ───────────────────────────────────────────────────────

    def _get_fallback_india_data(self) -> dict:
        """Standard India-centric fallback if JSON fails."""
        return {
            "election_name": "General Election to Lok Sabha",
            "country_name": "India",
            "next_election_date": "2029-05-01",
            "requirements": [
                "Indian Citizen",
                "18 years or older",
                "Registered in Electoral Roll",
                "Must possess Voter ID or 12 approved alternatives"
            ]
        }