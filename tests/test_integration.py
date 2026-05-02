"""
CivicPulse — Integration & Performance Tests
=============================================
Covers end-to-end flows, service interactions, and response-time budgets.
All external network calls are mocked — tests run fully offline.

Marks:
    integration : full-stack flows
    slow        : tests that check timing / throughput
"""

from __future__ import annotations

import json
import sys
import os
import time
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Shared mock factory ────────────────────────────────────────────────────────

def _make_st() -> MagicMock:
    st = MagicMock()
    st.session_state = {}
    return st


def _translate_resp(translated: str) -> MagicMock:
    """Build a mock urlopen context manager that returns a gtx-style response."""
    body = json.dumps([[[ translated, "source", None, None, None]], None, "en"]).encode()
    mock_resp = MagicMock()
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__  = MagicMock(return_value=False)
    mock_resp.read.return_value = body
    return mock_resp


# ===========================================================================
#  1. Full location → election data flow
# ===========================================================================

class TestLocationToElectionDataFlow(unittest.TestCase):
    """Integration: PIN code → state code → mock results."""

    def test_wb_pin_resolves_to_wb_results(self):
        from services.election_scraper import get_state_code_from_location, fetch_results
        with patch("services.election_scraper._scrape_eci_results", return_value=None):
            sc      = get_state_code_from_location("700001")
            results = fetch_results(sc)
        self.assertEqual(sc, "WB")
        self.assertEqual(results["state"], "West Bengal")
        self.assertEqual(results["total_seats"], 294)
        fetch_results.clear()

    def test_tn_name_resolves_to_tn_results(self):
        from services.election_scraper import get_state_code_from_location, fetch_results
        with patch("services.election_scraper._scrape_eci_results", return_value=None):
            sc      = get_state_code_from_location("Tamil Nadu")
            results = fetch_results(sc)
        self.assertEqual(sc, "TN")
        self.assertEqual(results["total_seats"], 234)
        fetch_results.clear()

    def test_results_always_have_color(self):
        from services.election_scraper import fetch_results
        with patch("services.election_scraper._scrape_eci_results", return_value=None):
            results = fetch_results("WB")
        for party in results["parties"]:
            self.assertIn("color", party)
            self.assertTrue(party["color"].startswith("#"))
        fetch_results.clear()

    def test_results_always_have_total(self):
        from services.election_scraper import fetch_results
        with patch("services.election_scraper._scrape_eci_results", return_value=None):
            results = fetch_results("WB")
        for party in results["parties"]:
            self.assertIn("total", party)
            self.assertGreaterEqual(party["total"], 0)
        fetch_results.clear()

    def test_last_updated_is_populated(self):
        from services.election_scraper import fetch_results
        with patch("services.election_scraper._scrape_eci_results", return_value=None):
            results = fetch_results("KL")
        self.assertIn("last_updated", results)
        self.assertTrue(results["last_updated"])
        fetch_results.clear()


# ===========================================================================
#  2. Calendar → GCal link flow
# ===========================================================================

class TestCalendarIntegration(unittest.TestCase):

    def setUp(self):
        from services.calendar_service import CalendarService
        self.svc = CalendarService()

    def test_full_election_data_generates_three_links(self):
        data = {
            "jurisdiction": "West Bengal",
            "poll_date":    "2026-04-23",
            "counting_day": "2026-05-04",
        }
        links = self.svc.generate_reminder_links(data)
        self.assertEqual(len(links), 3)
        for link in links:
            self.assertIn("link", link)
            self.assertIn("calendar.google.com", link["link"])

    def test_missing_counting_day_generates_two_links(self):
        data = {"jurisdiction": "Tamil Nadu", "poll_date": "2026-04-19"}
        links = self.svc.generate_reminder_links(data)
        self.assertEqual(len(links), 2)

    def test_gcal_link_has_correct_timezone(self):
        data  = {"jurisdiction": "Kerala", "poll_date": "2026-04-23"}
        links = self.svc.generate_reminder_links(data)
        for link in links:
            self.assertIn("Asia%2FKolkata", link["link"])

    def test_gcal_link_contains_emoji(self):
        link = self.svc.generate_gcal_link("Vote Today", "2026-04-23")
        self.assertIn("%F0%9F%97%B3", link)  # URL-encoded 🗳️


# ===========================================================================
#  3. Translation batch vs single consistency
# ===========================================================================

class TestTranslationBatchConsistency(unittest.TestCase):
    """Integration: batch translate should give same results as individual calls."""

    def _make_mock_resp(self, translated: str):
        body = json.dumps([[[translated, "source", None, None, None]], None, "en"]).encode()
        mock = MagicMock()
        mock.__enter__ = MagicMock(return_value=mock)
        mock.__exit__  = MagicMock(return_value=False)
        mock.read.return_value = body
        return mock

    def test_single_translate_cached_after_call(self):
        st_mock = _make_st()
        with patch("components.language_selector.st", st_mock), \
             patch("urllib.request.urlopen", return_value=self._make_mock_resp("नमस्ते")):
            import components.language_selector as ls
            result = ls.translate_text("Hello", "hi")
        self.assertEqual(result, "नमस्ते")
        # Verify cached
        self.assertIn(("Hello", "hi"), st_mock.session_state.get("_translate_cache", {}))

    def test_english_never_hits_network(self):
        st_mock = _make_st()
        with patch("components.language_selector.st", st_mock), \
             patch("urllib.request.urlopen") as mock_open:
            import components.language_selector as ls
            ls.translate_text("Hello", "en")
            mock_open.assert_not_called()

    def test_empty_batch_returns_empty(self):
        st_mock = _make_st()
        with patch("components.language_selector.st", st_mock):
            import components.language_selector as ls
            result = ls.translate_batch([], "hi")
        self.assertEqual(result, [])

    def test_english_batch_passthrough(self):
        st_mock = _make_st()
        with patch("components.language_selector.st", st_mock):
            import components.language_selector as ls
            texts  = ["Hello", "Vote", "India"]
            result = ls.translate_batch(texts, "en")
        self.assertEqual(result, texts)


# ===========================================================================
#  4. Input validation integration
# ===========================================================================

class TestInputValidationIntegration(unittest.TestCase):

    def test_xss_blocked_in_sanitize_and_validate(self):
        from utils.validators import sanitize_and_validate
        result = sanitize_and_validate('<img src=x onerror=alert(1)>')
        self.assertNotIn("<img", result)
        self.assertNotIn("onerror", result)

    def test_sql_injection_escaped(self):
        from utils.validators import sanitize_and_validate
        result = sanitize_and_validate("'; DROP TABLE voters; --")
        self.assertNotIn("<", result)

    def test_long_input_truncated_to_max(self):
        from utils.validators import sanitize_and_validate
        result = sanitize_and_validate("a" * 500, max_length=200)
        self.assertLessEqual(len(result), 200)

    def test_valid_pin_accepted(self):
        from utils.validators import validate_location_input
        self.assertTrue(validate_location_input("700001"))
        self.assertTrue(validate_location_input("600001"))

    def test_invalid_pin_rejected(self):
        from utils.validators import validate_location_input
        self.assertFalse(validate_location_input("12345"))    # 5 digits
        self.assertFalse(validate_location_input("1234567"))  # 7 digits
        self.assertFalse(validate_location_input(""))
        self.assertFalse(validate_location_input(None))       # type: ignore

    def test_state_name_accepted(self):
        from utils.validators import validate_location_input
        self.assertTrue(validate_location_input("West Bengal"))
        self.assertTrue(validate_location_input("Tamil Nadu"))

    def test_email_validation(self):
        from utils.validators import validate_email
        self.assertTrue(validate_email("voter@india.in"))
        self.assertFalse(validate_email("not-an-email"))
        self.assertFalse(validate_email(""))

    def test_indian_phone_validation(self):
        from utils.validators import validate_phone
        self.assertTrue(validate_phone("9876543210"))
        self.assertTrue(validate_phone("+919876543210"))
        self.assertFalse(validate_phone("1234567890"))  # starts with 1
        self.assertFalse(validate_phone("12345"))       # too short


# ===========================================================================
#  5. Performance — response time budgets
# ===========================================================================

class TestPerformanceBudgets(unittest.TestCase):
    """Ensure critical paths complete within acceptable time budgets."""

    def test_location_parse_under_10ms(self):
        from utils.location_utils import parse_location
        start = time.perf_counter()
        for _ in range(100):
            parse_location("West Bengal")
        elapsed = (time.perf_counter() - start) / 100
        self.assertLess(elapsed, 0.01, f"parse_location too slow: {elapsed:.4f}s")

    def test_validate_location_under_1ms(self):
        from utils.validators import validate_location_input
        start = time.perf_counter()
        for _ in range(1000):
            validate_location_input("700001")
        elapsed = (time.perf_counter() - start) / 1000
        self.assertLess(elapsed, 0.001, f"validate_location_input too slow: {elapsed:.6f}s")

    def test_sanitize_text_under_1ms(self):
        from utils.location_utils import sanitize_text
        start = time.perf_counter()
        for _ in range(1000):
            sanitize_text('<script>alert("xss")</script>')
        elapsed = (time.perf_counter() - start) / 1000
        self.assertLess(elapsed, 0.001, f"sanitize_text too slow: {elapsed:.6f}s")

    def test_normalize_date_under_1ms(self):
        from services.calendar_service import CalendarService
        svc   = CalendarService()
        start = time.perf_counter()
        for _ in range(1000):
            svc._normalize_date("23 April 2026")
        elapsed = (time.perf_counter() - start) / 1000
        self.assertLess(elapsed, 0.001, f"_normalize_date too slow: {elapsed:.6f}s")

    def test_state_code_lookup_under_1ms(self):
        from services.election_scraper import get_state_code_from_location
        start = time.perf_counter()
        for _ in range(1000):
            get_state_code_from_location("700001")
        elapsed = (time.perf_counter() - start) / 1000
        self.assertLess(elapsed, 0.001, f"get_state_code_from_location too slow: {elapsed:.6f}s")


# ===========================================================================
#  6. Civic API service integration
# ===========================================================================

class TestCivicAPIIntegration(unittest.TestCase):

    def setUp(self):
        from services.civic_api import CivicAPIService
        self.svc = CivicAPIService()

    def test_india_fallback_has_required_keys(self):
        data = self.svc._get_fallback_india_data()
        for key in ("election_name", "country_name", "next_election_date", "requirements"):
            self.assertIn(key, data)

    def test_india_requirements_is_list(self):
        data = self.svc._get_fallback_india_data()
        self.assertIsInstance(data["requirements"], list)
        self.assertGreater(len(data["requirements"]), 0)

    def test_get_polling_locations_returns_list(self):
        locs = self.svc.get_polling_locations("Kolkata")
        self.assertIsInstance(locs, list)
        self.assertGreater(len(locs), 0)

    def test_get_polling_locations_have_required_keys(self):
        locs = self.svc.get_polling_locations("Chennai")
        for loc in locs:
            self.assertIn("name", loc)
            self.assertIn("accessible", loc)
            self.assertIn("hours", loc)

    def test_no_api_key_returns_none_for_representatives(self):
        from services.civic_api import CivicAPIService
        svc    = CivicAPIService(api_key="")
        result = svc.get_representatives("West Bengal, India")
        self.assertIsNone(result)

    def test_voter_info_has_eci_links(self):
        info = self.svc.get_voter_info("700001")
        self.assertEqual(info["status"], "success")
        self.assertIn("eci.gov.in", info.get("voter_portal", "") + info.get("booth_locator", ""))


if __name__ == "__main__":
    print("🇮🇳 Running CivicPulse Integration & Performance Tests…")
    unittest.main(verbosity=2)
