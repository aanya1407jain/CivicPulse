"""
CivicPulse — Test Suite: India-Centric API Services
===================================================
Covers CalendarService, CivicAPIService, MapsService, GoogleAuthService.
Includes file-I/O mocking, edge cases, and None-safety checks.
"""

import unittest
import sys
import os
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ─────────────────────────────────────────────────────────────────────────────
class TestCalendarServiceIndia(unittest.TestCase):
    """Tests for the India-localized CalendarService."""

    def setUp(self):
        from services.calendar_service import CalendarService
        self.svc = CalendarService()

    def test_timezone_is_ist(self):
        self.assertEqual(self.svc.timezone, "Asia/Kolkata")

    def test_gcal_link_contains_ist(self):
        link = self.svc.generate_gcal_link("Vote TN", "2026-04-23", "Tamil Nadu Polls")
        self.assertIn("ctz=Asia%2FKolkata", link)
        self.assertIn("20260423", link)

    def test_normalize_verbose_indian_format(self):
        self.assertEqual(self.svc._normalize_date("April 23, 2026"), "2026-04-23")

    def test_normalize_eci_day_first_format(self):
        self.assertEqual(self.svc._normalize_date("23 April 2026"), "2026-04-23")

    def test_normalize_iso_format(self):
        self.assertEqual(self.svc._normalize_date("2026-04-23"), "2026-04-23")

    def test_normalize_dd_mm_yyyy(self):
        self.assertEqual(self.svc._normalize_date("23-04-2026"), "2026-04-23")

    def test_normalize_returns_none_for_tba(self):
        """TBA / Phase strings must not silently return today — they return None."""
        self.assertIsNone(self.svc._normalize_date("TBA"))
        self.assertIsNone(self.svc._normalize_date("Phase 2"))
        self.assertIsNone(self.svc._normalize_date("Varies"))
        self.assertIsNone(self.svc._normalize_date(""))
        self.assertIsNone(self.svc._normalize_date(None))  # type: ignore

    def test_gcal_link_returns_hash_for_bad_date(self):
        link = self.svc.generate_gcal_link("Test", "not-a-date")
        self.assertEqual(link, "#")

    def test_india_reminder_events_all_three(self):
        data = {
            "jurisdiction": "West Bengal",
            "poll_date": "2026-04-23",
            "counting_day": "2026-05-04",
        }
        events = self.svc._build_india_reminder_events(data)
        summaries = [e["summary"] for e in events]
        self.assertTrue(any("VOTE" in s for s in summaries))
        self.assertTrue(any("Dry Day" in s for s in summaries))
        self.assertTrue(any("Results" in s for s in summaries))

    def test_dry_day_is_one_day_before_poll(self):
        data = {"jurisdiction": "Tamil Nadu", "poll_date": "2026-04-23"}
        events = self.svc._build_india_reminder_events(data)
        dry_event = next(e for e in events if "Dry Day" in e["summary"])
        self.assertEqual(dry_event["_date"], "2026-04-22")

    def test_no_events_for_empty_data(self):
        events = self.svc._build_india_reminder_events({})
        self.assertEqual(events, [])


# ─────────────────────────────────────────────────────────────────────────────
class TestCivicAPIServiceIndia(unittest.TestCase):
    """Tests for the India-localized CivicAPIService."""

    def setUp(self):
        from services.civic_api import CivicAPIService
        self.svc = CivicAPIService()

    def test_fallback_returns_india_data(self):
        data = self.svc._get_fallback_india_data()
        self.assertEqual(data["country_name"], "India")   # type: ignore[index]

    def test_voter_info_links_to_eci(self):
        info = self.svc.get_voter_info("Mumbai")
        self.assertIn("voters.eci.gov.in", info["voter_portal"])
        self.assertIn("electoralsearch.eci.gov.in", info["booth_locator"])

    def test_polling_locations_non_empty(self):
        locs = self.svc.get_polling_locations("Chennai")
        self.assertGreater(len(locs), 0)
        for loc in locs:
            self.assertIn("name", loc)
            self.assertIn("address", loc)

    @patch("builtins.open", mock_open(read_data='{"country_data": {}}'))
    def test_get_election_details_missing_country_uses_fallback(self):
        """When the JSON has no entry for the country, fallback is returned."""
        from services import civic_api
        # Clear the Streamlit cache for this test
        try:
            civic_api._load_local_json.clear()
        except AttributeError:
            pass
        data = self.svc.get_election_details("XY")
        self.assertIn("country_name", data)

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_get_election_details_file_missing_uses_fallback(self, _mock):
        from services import civic_api
        try:
            civic_api._load_local_json.clear()
        except AttributeError:
            pass
        data = self.svc.get_election_details("IN")
        self.assertIn("country_name", data)


# ─────────────────────────────────────────────────────────────────────────────
class TestMapsServiceIndia(unittest.TestCase):
    """Tests for the India-centric MapsService."""

    def setUp(self):
        from services.maps_service import MapsService
        self.svc = MapsService(api_key="MOCK_KEY")
        self.no_key_svc = MapsService(api_key="")

    def test_geocode_appends_india(self):
        result = self.svc.geocode("Mumbai")
        self.assertIsNotNone(result)
        self.assertIn("India", result["formatted_address"])  # type: ignore

    def test_geocode_fallback_without_key(self):
        result = self.no_key_svc.geocode("Chennai")
        self.assertIsNotNone(result)
        self.assertIn("India", result["formatted_address"])  # type: ignore

    def test_eci_portal_url(self):
        url = self.svc.get_eci_booth_locator_url()
        self.assertEqual(url, "https://electoralsearch.eci.gov.in/")

    def test_embed_url_with_key(self):
        url = self.svc.get_embed_url("schools near Mumbai")
        self.assertIn("maps.googleapis.com", url)
        self.assertIn("MOCK_KEY", url)

    def test_embed_url_without_key(self):
        """embed URL should degrade gracefully without a key."""
        url = self.no_key_svc.get_embed_url("schools near Mumbai")
        self.assertIn("maps.google.com", url)
        self.assertIn("output=embed", url)

    def test_directions_link_format(self):
        link = self.svc.get_directions_link("Block 4, Chennai")
        self.assertIn("maps.google.com/maps/dir", link)

    def test_find_nearby_places_no_key_returns_empty(self):
        """Without an API key, nearby search should return [] gracefully."""
        results = self.no_key_svc.find_nearby_places(13.08, 80.27)
        self.assertEqual(results, [])


# ─────────────────────────────────────────────────────────────────────────────
class TestGoogleAuthService(unittest.TestCase):
    """Tests for the Google Auth service (mock mode)."""

    def setUp(self):
        from services.google_auth import GoogleAuthService
        # Force mock mode by not passing real credentials
        self.svc = GoogleAuthService(client_id="", client_secret="")

    def test_mock_user_profile_is_indian(self):
        profile = self.svc.get_user_info("any_token")
        self.assertIn(".in", profile["email"])

    def test_mock_login_url(self):
        url, state = self.svc.get_authorization_url()
        self.assertEqual(url, "#mock_login")
        self.assertIsNotNone(state)
        self.assertGreater(len(state), 8)

    def test_mock_token_exchange(self):
        tokens = self.svc.exchange_code_for_tokens("fake_code")
        self.assertIn("access_token", tokens)

    def test_revoke_mock_token(self):
        self.assertTrue(self.svc.revoke_token("mock_access_token"))


# ─────────────────────────────────────────────────────────────────────────────
class TestValidators(unittest.TestCase):
    """Edge-case tests for validators."""

    def setUp(self):
        from utils.validators import validate_location_input, validate_phone, sanitize_text
        self.validate_loc = validate_location_input
        self.validate_phone = validate_phone
        self.sanitize = sanitize_text

    def test_valid_6_digit_pin(self):
        self.assertTrue(self.validate_loc("400001"))
        self.assertTrue(self.validate_loc("700001"))

    def test_valid_state_name(self):
        self.assertTrue(self.validate_loc("Maharashtra"))
        self.assertTrue(self.validate_loc("West Bengal"))

    def test_5_digit_pin_invalid(self):
        self.assertFalse(self.validate_loc("12345"))

    def test_7_digit_pin_invalid(self):
        self.assertFalse(self.validate_loc("1234567"))

    def test_too_short_invalid(self):
        self.assertFalse(self.validate_loc("A"))
        self.assertFalse(self.validate_loc("12"))

    def test_none_invalid(self):
        self.assertFalse(self.validate_loc(None))  # type: ignore

    def test_empty_string_invalid(self):
        self.assertFalse(self.validate_loc(""))
        self.assertFalse(self.validate_loc("   "))

    def test_valid_phone_10_digit(self):
        self.assertTrue(self.validate_phone("9876543210"))
        self.assertTrue(self.validate_phone("6234567890"))

    def test_valid_phone_with_country_code(self):
        self.assertTrue(self.validate_phone("+919876543210"))

    def test_invalid_phone_starts_with_1(self):
        self.assertFalse(self.validate_phone("1234567890"))

    def test_sanitize_xss(self):
        result = self.sanitize('<script>alert("xss")</script>')
        self.assertNotIn("<script>", result)
        self.assertIn("&lt;script&gt;", result)

    def test_sanitize_normal_text_unchanged(self):
        self.assertEqual(self.sanitize("West Bengal"), "West Bengal")


if __name__ == "__main__":
    print("🇮🇳 Starting India-Centric Services Test Suite…")
    unittest.main(verbosity=2)
