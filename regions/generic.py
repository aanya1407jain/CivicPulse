"""
CivicPulse — India-Centric Fallback Election Handler
====================================================
Used when a specific region is not fully mapped. 
Defaults to General Indian Election Commission (ECI) standards.
"""

from __future__ import annotations
from regions.base import BaseRegionHandler, ElectionStep

class GenericRegionHandler(BaseRegionHandler):
    country_code = "IN"
    country_name = "India"
    flag = "🇮🇳"

    def get_election_data(self, location: str) -> dict:
        return {
            "election_name": "General Election / Lok Sabha",
            "election_type": "Parliamentary General Election",
            "next_election_date": "2029-05-01",
            "registration_deadline": "Continuous (Apply via Form 6)",
            "early_voting_start": None,
            "early_voting_end": None,
            "polling_stations_count": "1 Million+",
            "jurisdiction": location if location else "General India",
            "key_dates": {
                "Registration": "Ongoing via Voters Portal",
                "Phase Announcements": "Check ECI Notifications",
                "Poll Day": "Expected May 2029"
            },
            "requirements": [
                "Must be a Citizen of India",
                "Must be 18 years of age on the qualifying date",
                "Must possess a valid Voter ID (EPIC) or approved alternative ID",
                "Name must appear in the current Electoral Roll"
            ],
            "voting_methods": self.get_voting_methods(),
            "polling_stations": [],
            "registration_url": "https://voters.eci.gov.in/",
        }

    def get_checklist_steps(self) -> list[ElectionStep]:
        return [
            ElectionStep(
                id="check_name", 
                title="Verify Electoral Roll", 
                description="Search your name on electoralsearch.eci.gov.in to ensure you are eligible to vote.", 
                priority="urgent",
                url="https://electoralsearch.eci.gov.in/"
            ),
            ElectionStep(
                id="voter_id", 
                title="Apply for Voter ID", 
                description="If not registered, fill Form 6 on the Voter Portal.", 
                priority="urgent",
                url="https://voters.eci.gov.in/"
            ),
            ElectionStep(
                id="helpline", 
                title="Voter Helpline", 
                description="Download the Voter Helpline App or call 1950 for assistance.",
                url="https://play.google.com/store/apps/details?id=com.eci.citizen"
            ),
            ElectionStep(
                id="research", 
                title="Know Your Candidate", 
                description="Check candidate backgrounds and affidavits before voting.",
                url="https://affidavit.eci.gov.in/"
            ),
            ElectionStep(
                id="vote", 
                title="Cast Your Vote!", 
                description="Visit your assigned polling station and get your finger inked.", 
                priority="urgent"
            ),
        ]

    def get_registration_url(self, location: str) -> str:
        return "https://voters.eci.gov.in/"

    def get_local_rules(self, jurisdiction: str) -> list[str]:
        return [
            "📞 Call 1950 (Voter Helpline) for any location-specific queries.",
            "📑 Carry your EPIC card or any of the 12 alternative photo ID documents.",
            "🚫 Do not carry mobile phones inside the polling compartment."
        ]

    def get_voting_methods(self) -> list[dict]:
        return [
            {"icon": "📟", "name": "EVM/VVPAT", "description": "Electronic voting with paper trail verification."},
            {"icon": "✉️", "name": "Postal Ballot", "description": "For eligible service voters and senior citizens."},
        ]