"""
CivicPulse — Test Suite: India-Centric Region Handlers
======================================================
Tests validation logic for Indian election data structures,
ECI requirements, and localized checklist validity.
"""

import unittest
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from regions import get_region_handler
from regions.base import ElectionStep

# Primary country list with IN as the focus
COUNTRIES = ["IN", "US", "UK"] 

REQUIRED_ELECTION_FIELDS = [
    "election_name",
    "election_type",
    "next_election_date",
    "registration_deadline",
    "polling_stations_count",
    "jurisdiction",
    "key_dates",
    "requirements",
    "voting_methods",
]

# India-centric sample locations for testing
SAMPLE_LOCATIONS = {
    "IN": "West Bengal", # Testing 2026 Assembly cycle
    "US": "California",
    "UK": "London",
}

class TestRegionHandlers(unittest.TestCase):
    """Test suite for validating India-centric election data handlers."""

    def _get_handler_and_data(self, country_code: str):
        handler = get_region_handler(country_code)
        location = SAMPLE_LOCATIONS.get(country_code, "General India")
        data = handler.get_election_data(location)
        return handler, data

    def _test_election_data_structure(self, country_code: str) -> None:
        handler, data = self._get_handler_and_data(country_code)
        for field in REQUIRED_ELECTION_FIELDS:
            self.assertIn(field, data, f"{country_code}: Missing field '{field}'")
        
        # Verify Indian specifics if IN is tested
        if country_code == "IN":
            self.assertIn("registration_url", data)
            self.assertIn("EPIC", str(data["requirements"]))

    def _test_checklist_steps(self, country_code: str) -> None:
        handler, _ = self._get_handler_and_data(country_code)
        steps = handler.get_checklist_steps()
        self.assertGreater(len(steps), 0, f"{country_code}: checklist must have steps")
        for step in steps:
            self.assertIsInstance(step, ElectionStep)
            # Verify India-specific URLs point to ECI portals
            if country_code == "IN" and step.url:
                self.assertTrue("eci.gov.in" in step.url or "voters" in step.url)

    def _test_local_rules(self, country_code: str) -> None:
        handler, data = self._get_handler_and_data(country_code)
        rules = handler.get_local_rules(data.get("jurisdiction", ""))
        self.assertGreater(len(rules), 0)
        if country_code == "IN":
            # Ensure Indian safety/helpline rules exist
            self.assertTrue(any("1950" in r or "mobile" in r.lower() for r in rules))

# Helper to generate tests
def _make_test(country_code: str, test_method: str):
    def test(self):
        getattr(self, test_method)(country_code)
    test.__name__ = f"test_{test_method.replace('_test_', '')}_{country_code}"
    return test

for _country in COUNTRIES:
    for _method in ["_test_election_data_structure", "_test_checklist_steps", "_test_local_rules"]:
        _test_fn = _make_test(_country, _method)
        setattr(TestRegionHandlers, _test_fn.__name__, _test_fn)

class TestIndiaSpecifics(unittest.TestCase):
    """Deep validation for the IndiaRegionHandler."""

    def test_voting_age_india(self):
        handler = get_region_handler("IN")
        self.assertEqual(handler.get_voting_age(), 18)

    def test_non_compulsory_india(self):
        handler = get_region_handler("IN")
        self.assertFalse(handler.is_compulsory_voting(), "India is a voluntary voting democracy.")

    def test_id_requirements_india(self):
        handler = get_region_handler("IN")
        reqs = handler.get_id_requirements()
        self.assertIn("EPIC", reqs, "Indian ID requirements must mention EPIC card.")

    def test_voting_methods_india(self):
        handler = get_region_handler("IN")
        methods = handler.get_voting_methods()
        # Verify EVM and VVPAT are present
        method_names = [m['name'] for m in methods]
        self.assertTrue(any("EVM" in name for name in method_names))

class TestDateUtilsIndia(unittest.TestCase):
    """Test date logic for Indian election cycles (2026/2029)."""

    def test_days_until_lok_sabha(self):
        from utils.date_utils import days_until
        # Testing against the 2029-05-01 expected General Election
        result = days_until("2029-05-01")
        self.assertIsNotNone(result)
        self.assertGreater(result, 0)

class TestValidatorsIndia(unittest.TestCase):
    """Test validation for Indian PIN codes and locations."""

    def test_validate_pin_code(self):
        from utils.validators import validate_location_input
        # Test valid 6-digit Indian PIN
        self.assertTrue(validate_location_input("400001")) 
        self.assertTrue(validate_location_input("Maharashtra"))

    def test_invalid_location(self):
        from utils.validators import validate_location_input
        self.assertFalse(validate_location_input("123")) # Too short

if __name__ == "__main__":
    print("🇮🇳 Starting India-Centric CivicPulse Test Suite...")
    unittest.main(verbosity=2)