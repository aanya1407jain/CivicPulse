"""
CivicPulse — Regional Election Handlers
========================================
IndiaRegionHandler  — full 2026/2029 cycle
USRegionHandler     — 2026 midterms
UKRegionHandler     — proper UK handler (was pointing to GenericRegionHandler)
"""

from __future__ import annotations
from .base import BaseRegionHandler, ElectionStep, ElectionData
from config.settings import INDIA


class IndiaRegionHandler(BaseRegionHandler):
    country_code = "IN"
    country_name = "India"
    flag = "🇮🇳"

    def get_election_data(self, location: str) -> dict:
        state_name = location.strip().title()
        data = ElectionData(
            election_name="Assembly Elections 2026 / 19th Lok Sabha",
            election_type="Vidhan Sabha (State Assembly)",
            jurisdiction=state_name,
            next_election_date="2026-05-04",
            registration_deadline="Completed (new voters: Form 6 for 2029)",
            polling_stations_count="1,035,000+",
            key_dates={
                "Phase I (TN / WB / KL / AS)": "2026-04-23",
                "Phase II (West Bengal)": "2026-04-29",
                "Silence / Quiet Period": "2026-05-02",
                "Counting Day (all states)": "2026-05-04",
            },
            requirements=[
                "Citizen of India & 18+ years of age",
                "Ordinary resident of the constituency",
                "Name must be in the Electoral Roll",
                "EPIC Card or 12 alternative documents required",
            ],
            voting_methods=self.get_voting_methods(),
        )
        d = data.to_dict()
        d["registration_url"] = INDIA["VOTER_PORTAL_URL"]
        d["poll_date"]       = "2026-04-23"
        d["counting_day"]    = "2026-05-04"
        return d

    def get_checklist_steps(self) -> list[ElectionStep]:
        return [
            ElectionStep(
                id="check_roll",
                title="Search Name in Electoral Roll",
                jurisdiction="All India",
                description="Verify your name in the voter list using EPIC or personal details.",
                priority="urgent",
                url=INDIA["EPIC_SEARCH_URL"],
            ),
            ElectionStep(
                id="form_6",
                title="Register as New Voter (Form 6)",
                jurisdiction="All India",
                description="If missing from roll, fill Form 6 to register for 2029 elections.",
                priority="urgent",
                url=INDIA["FORM_6_URL"],
            ),
            ElectionStep(
                id="find_booth",
                title="Locate Your Polling Booth",
                jurisdiction="Local",
                description="Find your specific room number and booth via the ECI electoral search.",
                priority="normal",
                url=INDIA["EPIC_SEARCH_URL"],
            ),
            ElectionStep(
                id="know_candidate",
                title="Know Your Candidate",
                jurisdiction="Constituency",
                description="Check affidavits and backgrounds of candidates before voting.",
                priority="optional",
                url=INDIA["KNOW_YOUR_CANDIDATE"],
            ),
            ElectionStep(
                id="vote_day",
                title="Go Vote on Poll Day!",
                jurisdiction="Constituency",
                description=(
                    "Carry Voter ID or Aadhaar. No mobile phones allowed. "
                    "Confirm VVPAT slip before leaving."
                ),
                priority="urgent",
            ),
        ]

    def get_registration_url(self, location: str) -> str:
        return INDIA["VOTER_PORTAL_URL"]

    def get_local_rules(self, jurisdiction: str) -> list[str]:
        return [
            "✅ ID: Use Aadhaar, PAN, or Passport if EPIC is unavailable.",
            "🚫 No Mobile: Strictly prohibited inside the voting compartment.",
            "🕒 Timing: Polling hours are 7:00 AM to 6:00 PM.",
            "♿ Priority: Fast-track queues available for seniors (85+) and PwD voters.",
            f"📞 Helpline: Dial {INDIA['VOTER_HELPLINE']} for instant ECI support.",
        ]

    def get_voting_methods(self) -> list[dict]:
        return [
            {
                "icon": "📟",
                "name": "EVM & VVPAT",
                "description": "Electronic voting with paper slip confirmation at your booth.",
            },
            {
                "icon": "🏠",
                "name": "Home Voting (Form 12D)",
                "description": "Available for voters aged 85+ and PwD via ECI mobile teams.",
            },
        ]


class USRegionHandler(BaseRegionHandler):
    """2026 US Midterm Elections handler."""
    country_code = "US"
    country_name = "United States"
    flag = "🇺🇸"

    def get_election_data(self, location: str) -> dict:
        return {
            "election_name": "2026 US Midterm Elections",
            "election_type": "Congressional",
            "jurisdiction": location.strip().title(),
            "next_election_date": "2026-11-03",
            "registration_deadline": "Varies by state — check vote.gov",
            "polling_stations_count": "Varies",
            "key_dates": {"Election Day": "November 3, 2026"},
            "requirements": ["US Citizen", "18+ years old", "Registered voter"],
            "voting_methods": self.get_voting_methods(),
        }

    def get_checklist_steps(self) -> list[ElectionStep]:
        return [
            ElectionStep(
                id="us_reg",
                title="Check Voter Registration",
                jurisdiction="State",
                description="Confirm or update your registration at vote.gov.",
                priority="urgent",
                url="https://vote.gov",
            ),
            ElectionStep(
                id="us_id",
                title="Check State ID Requirements",
                jurisdiction="State",
                description="ID rules vary by state — confirm yours at vote.gov.",
                priority="normal",
                url="https://vote.gov",
            ),
        ]

    def get_registration_url(self, location: str) -> str:
        return "https://vote.gov"

    def get_local_rules(self, jurisdiction: str) -> list[str]:
        return [
            "Check your state's specific ID requirements at vote.gov.",
            "Early voting and mail-in ballot deadlines vary by state.",
        ]

    def get_voting_methods(self) -> list[dict]:
        return [
            {"icon": "📮", "name": "Mail-in / Absentee", "description": "Request a ballot by your state deadline."},
            {"icon": "🏛️", "name": "In-Person", "description": "Vote at your assigned polling place on Election Day."},
        ]


class UKRegionHandler(BaseRegionHandler):
    """UK General Election handler."""
    country_code = "UK"
    country_name = "United Kingdom"
    flag = "🇬🇧"

    def get_election_data(self, location: str) -> dict:
        return {
            "election_name": "UK General Election",
            "election_type": "Parliamentary General Election",
            "jurisdiction": location.strip().title(),
            "next_election_date": "2029-01-28",
            "registration_deadline": "12 working days before poll",
            "polling_stations_count": "Approx. 40,000",
            "key_dates": {
                "Dissolution of Parliament": "Expected Jan 2029",
                "Polling Day": "Expected Jan 28, 2029",
            },
            "requirements": [
                "British / Irish / qualifying Commonwealth citizen",
                "18+ years old on polling day",
                "Registered to vote",
                "Photo ID required at polling station",
            ],
            "voting_methods": self.get_voting_methods(),
        }

    def get_checklist_steps(self) -> list[ElectionStep]:
        return [
            ElectionStep(
                id="uk_reg",
                title="Register to Vote",
                jurisdiction="England / Wales / Scotland / NI",
                description="Register online at gov.uk — takes 5 minutes.",
                priority="urgent",
                url="https://www.gov.uk/register-to-vote",
            ),
            ElectionStep(
                id="uk_id",
                title="Get Accepted Photo ID",
                jurisdiction="England / Wales / Scotland",
                description="Passport, driving licence, or free Voter Authority Certificate.",
                priority="urgent",
                url="https://www.electoralcommission.org.uk/",
            ),
        ]

    def get_registration_url(self, location: str) -> str:
        return "https://www.gov.uk/register-to-vote"

    def get_local_rules(self, jurisdiction: str) -> list[str]:
        return [
            "Photo ID is now required at polling stations in England.",
            "Polling hours: 7:00 AM to 10:00 PM.",
            "Proxy or postal vote options available — apply in advance.",
        ]

    def get_voting_methods(self) -> list[dict]:
        return [
            {"icon": "✏️", "name": "In-Person (Paper Ballot)", "description": "Vote at your local polling station with photo ID."},
            {"icon": "📮", "name": "Postal Vote", "description": "Apply for a postal ballot well before the deadline."},
        ]
