"""
CivicPulse — Test Suite: India-Centric Region Handlers
======================================================
Tests all three country handlers (IN, US, UK), data structure validity,
checklist integrity, local rules, and date utilities.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from regions import get_region_handler
from regions.base import ElectionStep

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

SAMPLE_LOCATIONS = {
    "IN": "West Bengal",
    "US": "California",
    "UK": "London",
}


class TestRegionHandlers(unittest.TestCase):
    """Parameterised tests for all region handlers."""

    def _get(self, cc: str):
        handler = get_region_handler(cc)
        location = SAMPLE_LOCATIONS.get(cc, "General")
        data = handler.get_election_data(location)
        return handler, data

    # ── Data structure ────────────────────────────────────────────────────────

    def _test_election_data_structure(self, cc: str) -> None:
        _, data = self._get(cc)
        for field in REQUIRED_ELECTION_FIELDS:
            self.assertIn(field, data, f"{cc}: missing field '{field}'")
        if cc == "IN":
            self.assertIn("registration_url", data)
            self.assertIn("EPIC", str(data["requirements"]))

    # ── Checklist ─────────────────────────────────────────────────────────────

    def _test_checklist_steps(self, cc: str) -> None:
        handler, _ = self._get(cc)
        steps = handler.get_checklist_steps()
        self.assertGreater(len(steps), 0, f"{cc}: checklist must have steps")
        for step in steps:
            self.assertIsInstance(step, ElectionStep)
            self.assertTrue(step.id, f"{cc}: step must have a non-empty id")
            self.assertTrue(step.title, f"{cc}: step must have a non-empty title")
            if cc == "IN" and step.url:
                self.assertTrue(
                    "eci.gov.in" in step.url or "voters" in step.url,
                    f"{cc}: Indian step URL should point to ECI: {step.url}",
                )

    # ── Local rules ───────────────────────────────────────────────────────────

    def _test_local_rules(self, cc: str) -> None:
        handler, data = self._get(cc)
        rules = handler.get_local_rules(data.get("jurisdiction", ""))
        self.assertGreater(len(rules), 0, f"{cc}: must have at least one local rule")
        if cc == "IN":
            rules_text = " ".join(rules).lower()
            self.assertTrue(
                "1950" in rules_text or "mobile" in rules_text,
                "India rules must mention helpline 1950 or mobile ban",
            )

    # ── Voting methods ────────────────────────────────────────────────────────

    def _test_voting_methods(self, cc: str) -> None:
        handler, _ = self._get(cc)
        methods = handler.get_voting_methods()
        self.assertGreater(len(methods), 0, f"{cc}: must have voting methods")
        for method in methods:
            self.assertIn("name", method)
            self.assertIn("icon", method)
            self.assertIn("description", method)


# Generate parameterised test methods
def _make_test(cc: str, method_name: str):
    def test_fn(self):
        getattr(self, method_name)(cc)
    test_fn.__name__ = f"test_{method_name.lstrip('_')}_{cc}"
    return test_fn


for _cc in COUNTRIES:
    for _m in [
        "_test_election_data_structure",
        "_test_checklist_steps",
        "_test_local_rules",
        "_test_voting_methods",
    ]:
        setattr(TestRegionHandlers, f"test{_m}_{_cc}", _make_test(_cc, _m))


# ─────────────────────────────────────────────────────────────────────────────
class TestIndiaSpecifics(unittest.TestCase):
    """Deep validation for the IndiaRegionHandler."""

    def setUp(self):
        self.handler = get_region_handler("IN")

    def test_voting_age_18(self):
        self.assertEqual(self.handler.get_voting_age(), 18)

    def test_non_compulsory(self):
        self.assertFalse(
            self.handler.is_compulsory_voting(),
            "India has voluntary voting.",
        )

    def test_id_requirements_mention_epic(self):
        reqs = self.handler.get_id_requirements()
        self.assertIn("EPIC", reqs)

    def test_voting_methods_contain_evm(self):
        methods = self.handler.get_voting_methods()
        names = [m["name"] for m in methods]
        self.assertTrue(any("EVM" in n for n in names))

    def test_get_registration_url_is_eci(self):
        url = self.handler.get_registration_url("West Bengal")
        self.assertIn("voters.eci.gov.in", url)

    def test_checklist_has_urgent_steps(self):
        steps = self.handler.get_checklist_steps()
        urgent = [s for s in steps if s.priority == "urgent"]
        self.assertGreater(len(urgent), 0)

    def test_election_data_has_counting_day(self):
        data = self.handler.get_election_data("Tamil Nadu")
        self.assertIn("counting_day", data)
        self.assertEqual(data["counting_day"], "2026-05-04")

    def test_election_data_has_poll_date(self):
        data = self.handler.get_election_data("Kerala")
        self.assertIn("poll_date", data)


# ─────────────────────────────────────────────────────────────────────────────
class TestUKHandler(unittest.TestCase):
    """Ensure UK now has its own proper handler."""

    def setUp(self):
        self.handler = get_region_handler("UK")

    def test_country_code(self):
        self.assertEqual(self.handler.country_code, "UK")

    def test_data_structure(self):
        data = self.handler.get_election_data("London")
        for field in REQUIRED_ELECTION_FIELDS:
            self.assertIn(field, data)

    def test_registration_url_is_gov_uk(self):
        url = self.handler.get_registration_url("London")
        self.assertIn("gov.uk", url)


# ─────────────────────────────────────────────────────────────────────────────
class TestDateUtils(unittest.TestCase):
    """Date utility edge cases."""

    def setUp(self):
        from utils.date_utils import days_until, format_date_locale, get_election_status
        self.days_until = days_until
        self.format_date = format_date_locale
        self.status = get_election_status

    def test_days_until_future(self):
        result = self.days_until("2099-01-01")
        self.assertIsNotNone(result)
        self.assertGreater(result, 0)

    def test_days_until_past(self):
        result = self.days_until("2000-01-01")
        self.assertIsNotNone(result)
        self.assertLess(result, 0)

    def test_days_until_tbd_returns_none(self):
        self.assertIsNone(self.days_until("TBD"))
        self.assertIsNone(self.days_until("Varies"))
        self.assertIsNone(self.days_until("Phase 1"))
        self.assertIsNone(self.days_until(None))  # type: ignore
        self.assertIsNone(self.days_until(""))

    def test_days_until_indian_verbose_format(self):
        from datetime import date, timedelta
        future = (date.today() + timedelta(days=30)).strftime("%d %B %Y")
        result = self.days_until(future)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 30, delta=1)  # type: ignore

    def test_format_date_none(self):
        result = self.format_date(None)
        self.assertIn("TBA", result)

    def test_format_date_phase_string_passthrough(self):
        result = self.format_date("Phase 2")
        self.assertEqual(result, "Phase 2")

    def test_status_completed(self):
        self.assertEqual(self.status("2000-01-01"), "✅ Completed")

    def test_status_upcoming(self):
        self.assertIn("Scheduled", self.status("2099-01-01"))


# ─────────────────────────────────────────────────────────────────────────────
class TestLocationUtils(unittest.TestCase):
    """Location parsing and country detection tests."""

    def setUp(self):
        from utils.location_utils import parse_location, detect_country_from_input
        self.parse = parse_location
        self.detect = detect_country_from_input

    def test_pin_700001_maps_to_wb(self):
        result = self.parse("700001")
        self.assertEqual(result["state_code"], "WB")

    def test_pin_400001_maps_to_mh(self):
        result = self.parse("400001")
        self.assertEqual(result["state_code"], "MH")

    def test_state_name_normalized(self):
        result = self.parse("west bengal")
        self.assertEqual(result["normalized"], "West Bengal")

    def test_detect_country_pin(self):
        self.assertEqual(self.detect("700001"), "IN")

    def test_detect_country_state_name(self):
        self.assertEqual(self.detect("Maharashtra"), "IN")

    def test_detect_country_default_india(self):
        self.assertEqual(self.detect("RandomText"), "IN")


if __name__ == "__main__":
    print("🇮🇳 Starting India-Centric CivicPulse Test Suite…")
    unittest.main(verbosity=2)
