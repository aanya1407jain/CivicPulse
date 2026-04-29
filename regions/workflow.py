"""
CivicPulse — Regional Election Handlers
============================================
Handles specialized logic for India and US.
"""

from __future__ import annotations
from .base import BaseRegionHandler, ElectionStep, ElectionData
from .generic import GenericRegionHandler # Fixes the yellow underline

class IndiaRegionHandler(BaseRegionHandler):
    country_code = "IN"
    country_name = "India"
    flag = "🇮🇳"

    def get_election_data(self, location: str) -> dict:
        state_name = location.strip().title()
        
        # We wrap this in the ElectionData dataclass we built in base.py
        data = ElectionData(
            election_name="19th Lok Sabha General Election",
            election_type="Parliamentary General Election",
            jurisdiction=state_name,
            next_election_date="2029-05-01",
            registration_deadline="10 days before nomination",
            polling_stations_count="1.1 Million+",
            key_dates={
                "Nomination Deadline": "April 2029 (Tentative)",
                "Poll Day": "May 1, 2029",
                "Counting Day": "May 25, 2029",
                "Results Declaration": "May 26, 2029",
            },
            requirements=[
                "Citizen of India & 18+ years of age",
                "Ordinary resident of the constituency",
                "Name must be in the Electoral Roll",
                "EPIC Card or 12 alternative documents required"
            ],
            voting_methods=self.get_voting_methods()
        )
        return data.to_dict()

    def get_checklist_steps(self) -> list[ElectionStep]:
        # Note: jurisdiction is now a required argument for ElectionStep
        return [
            ElectionStep(
                id="check_roll",
                title="Search Name in Electoral Roll",
                jurisdiction="All India",
                description="Verify your name in the voter list using EPIC or personal details.",
                priority="urgent",
                url="https://electoralsearch.eci.gov.in/",
            ),
            ElectionStep(
                id="form_6",
                title="Register as New Voter (Form 6)",
                jurisdiction="All India",
                description="If missing from roll, fill Form 6 to register.",
                priority="urgent",
                url="https://voters.eci.gov.in/",
            ),
            ElectionStep(
                id="find_booth",
                title="Locate Polling Booth",
                jurisdiction="Local",
                description="Find your specific room number and booth via ECI search.",
                url="https://electoralsearch.eci.gov.in/",
            ),
            ElectionStep(
                id="vote_day",
                title="Go Vote on Poll Day!",
                jurisdiction="Constituency",
                description="Carry ID. No mobile phones allowed. Confirm VVPAT slip.",
                priority="urgent",
            ),
        ]

    def get_registration_url(self, location: str) -> str:
        return "https://voters.eci.gov.in/"

    def get_local_rules(self, jurisdiction: str) -> list[str]:
        return [
            "✅ **ID:** Use Aadhaar, PAN, or Passport if EPIC is unavailable.",
            "⚠️ **No Mobile:** Strictly prohibited inside the voting compartment.",
            "🕒 **Timing:** 7:00 AM to 6:00 PM.",
            "📍 **Priority:** Fast-track queues for seniors and PwD voters.",
            "📞 **Helpline:** Dial 1950 for instant ECI support."
        ]

class USRegionHandler(BaseRegionHandler):
    """Basic implementation for US Midterms."""
    country_code = "US"
    country_name = "United States"
    flag = "🇺🇸"

    def get_election_data(self, location: str) -> dict:
        return {
            "election_name": "2026 US Midterm Elections",
            "election_type": "Congressional",
            "jurisdiction": location.strip().title(),
            "next_election_date": "2026-11-03",
            "registration_deadline": "Varies by State",
            "polling_stations_count": "Unknown",
            "key_dates": {"Election Day": "Nov 3, 2026"},
            "requirements": ["US Citizen", "18+ years old"],
            "voting_methods": [{"icon": "📮", "name": "Mail-in/In-person"}]
        }

    def get_checklist_steps(self) -> list[ElectionStep]:
        return [
            ElectionStep(id="us_reg", title="Check Registration", jurisdiction="State")
        ]

    def get_registration_url(self, location: str) -> str:
        return "https://vote.gov"

    def get_local_rules(self, jurisdiction: str) -> list[str]:
        return ["Check your state ID requirements at vote.gov"]