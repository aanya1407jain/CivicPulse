"""
CivicPulse — Base Election Region Handler
==========================================
Abstract base class updated for Indian localized requirements.
Ensures strict parameter ordering to prevent Dataclass TypeErrors.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ElectionStep:
    """
    Represents a single step in a voter's journey.
    Ordering: Required fields first, then fields with default values.
    """
    id: str
    title: str
    jurisdiction: str
    description: str = ""
    url: str = ""
    deadline: str = ""
    priority: str = "normal"  # urgent, normal, optional


@dataclass
class ElectionData:
    """
    Structured election data localized for India & Global context.
    Ensures 'jurisdiction' precedes any default arguments.
    """
    election_name: str
    election_type: str        # e.g., Lok Sabha, Vidhan Sabha
    jurisdiction: str         # State/UT or Constituency (Required)
    next_election_date: str | None
    registration_deadline: str | None

    # Fields with default values MUST follow non-default fields
    early_voting_start: str | None = None  # Used for Home Voting / Postal Ballot
    early_voting_end: str | None = None
    polling_stations_count: str | int = 0
    key_dates: dict[str, str] = field(default_factory=dict)
    requirements: list[str] = field(default_factory=list)
    voting_methods: list[dict] = field(default_factory=list)
    candidates: list[dict] = field(default_factory=list)
    polling_stations: list[dict] = field(default_factory=list)
    
    # India-Specific Extensions
    phase: str | int | None = None 
    constituency_type: str | None = None   # AC (Assembly) or PC (Parliamentary)

    def to_dict(self) -> dict:
        """Convert dataclass to dictionary for Streamlit component consumption."""
        return self.__dict__


class BaseRegionHandler(ABC):
    """
    Abstract base for region-specific election logic.
    Prioritizes Election Commission of India (ECI) standards.
    """

    country_code: str = ""
    country_name: str = ""
    flag: str = ""

    # ── Abstract Interface ────────────────────────────────────────────────────

    @abstractmethod
    def get_election_data(self, location: str) -> dict:
        """Return structured election data based on Local JSON/Mock data."""
        pass

    @abstractmethod
    def get_checklist_steps(self) -> list[ElectionStep]:
        """Return the voter journey (e.g., Verify Name -> Form 6 -> Booth -> Ink)."""
        pass

    @abstractmethod
    def get_registration_url(self, location: str) -> str:
        """Return official ECI/National registration URL."""
        pass

    @abstractmethod
    def get_local_rules(self, jurisdiction: str) -> list[str]:
        """Return specific rules (e.g., No Mobile Phones, Dry Days)."""
        pass

    # ── Concrete Helpers (Localized) ──────────────────────────────────────────

    def get_voting_methods(self) -> list[dict]:
        """Standard Indian voting methods — override if needed."""
        return [
            {
                "icon": "📟", 
                "name": "EVM & VVPAT", 
                "description": "Electronic voting with paper slip confirmation at your booth."
            },
            {
                "icon": "🏠", 
                "name": "Home Voting", 
                "description": "Available for 85+ seniors and PwD voters via Form 12D."
            },
        ]

    def get_official_url(self) -> str:
        """Return the ECI / National authority URL."""
        from config.settings import SUPPORTED_COUNTRIES
        return SUPPORTED_COUNTRIES.get(self.country_code, {}).get("official_url", "https://eci.gov.in")

    def get_id_requirements(self) -> str:
        """Refactored for ECI standards: EPIC card or approved alternatives."""
        if self.country_code == "IN":
            return "EPIC (Voter ID) or 12 approved alternatives (Aadhaar, PAN, etc.) required."
        
        from config.settings import SUPPORTED_COUNTRIES
        id_req = SUPPORTED_COUNTRIES.get(self.country_code, {}).get("id_required", True)
        return "Photo ID required to vote." if id_req else "No photo ID required."

    def get_voting_age(self) -> int:
        """Return minimum age to vote (standard 18)."""
        from config.settings import SUPPORTED_COUNTRIES
        return SUPPORTED_COUNTRIES.get(self.country_code, {}).get("voting_age", 18)

    def is_compulsory_voting(self) -> bool:
        """Identify if voting is a legal mandate (e.g., Brazil vs India)."""
        from config.settings import SUPPORTED_COUNTRIES
        return SUPPORTED_COUNTRIES.get(self.country_code, {}).get("compulsory_voting", False)