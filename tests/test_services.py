"""
CivicPulse — Test Suite: India-Centric API Services
===================================================
Tests for India-localized CivicAPIService, CalendarService, 
and Mock GoogleAuthService.
"""

import unittest
import sys
import os
from datetime import datetime

# Ensure project root is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

class TestCalendarServiceIndia(unittest.TestCase):
    """Tests for Indian localized Calendar reminders."""

    def setUp(self):
        from services.calendar_service import CalendarService
        self.svc = CalendarService()

    def test_timezone_is_ist(self):
        """Verify the service defaults to Indian Standard Time."""
        self.assertEqual(self.svc.timezone, "Asia/Kolkata")

    def test_generate_gcal_link_with_ist(self):
        """Verify GCal links include the Indian timezone parameter."""
        link = self.svc.generate_gcal_link("Vote TN", "2026-04-23", "Tamil Nadu Polls")
        self.assertIn("ctz=Asia%2FKolkata", link)
        self.assertIn("20260423", link)

    def test_normalize_indian_date_formats(self):
        """Verify service handles 'April 23, 2026' and other ECI formats."""
        # Verbose Format
        self.assertEqual(self.svc._normalize_date("April 23, 2026"), "2026-04-23")
        # ECI Standard Format
        self.assertEqual(self.svc._normalize_date("23 April 2026"), "2026-04-23")
        # ISO Format
        self.assertEqual(self.svc._normalize_date("2026-04-23"), "2026-04-23")

    def test_india_reminder_logic(self):
        """Verify Dry Day and Poll Day events are generated for India."""
        election_data = {
            "jurisdiction": "West Bengal",
            "poll_date": "2026-04-23",
            "counting_day": "2026-05-04"
        }
        events = self.svc._build_india_reminder_events(election_data)
        summaries = [e["summary"] for e in events]
        
        self.assertTrue(any("VOTE" in s for s in summaries))
        self.assertTrue(any("Dry Day" in s for s in summaries))
        self.assertTrue(any("Results" in s for s in summaries))


class TestCivicAPIServiceIndia(unittest.TestCase):
    """Tests for the India-localized Civic Data service."""

    def setUp(self):
        from services.civic_api import CivicAPIService
        self.svc = CivicAPIService()

    def test_get_election_details_india_fallback(self):
        """Ensure service returns ECI details for India."""
        data = self.svc.get_election_details("IN")
        self.assertEqual(data["country_name"], "India")
        # Check for ECI Helpline
        self.assertEqual(data.get("helpline"), "1950")

    def test_voter_info_links_to_eci(self):
        """Verify voter info points to official Indian portals."""
        info = self.svc.get_voter_info("Mumbai")
        self.assertIn("voters.eci.gov.in", info["voter_portal"])
        self.assertIn("electoralsearch.eci.gov.in", info["booth_locator"])


class TestMapsServiceIndia(unittest.TestCase):
    """Tests for India-centric Mapping features."""

    def setUp(self):
        from services.maps_service import MapsService
        self.svc = MapsService(api_key="MOCK_KEY")

    def test_geocoding_appends_india(self):
        """The service should bias searches toward India."""
        # Note: We can't test actual API calls without a key, 
        # so we check the fallback/logic structure
        result = self.svc.geocode("Mumbai")
        self.assertIsNotNone(result)
        self.assertIn("India", result["formatted_address"])

    def test_eci_portal_link(self):
        """Verify helper returns the correct ECI portal."""
        url = self.svc.get_eci_booth_locator_url()
        self.assertEqual(url, "https://electoralsearch.eci.gov.in/")


class TestGoogleAuthServiceMock(unittest.TestCase):
    """Tests for the Mock Auth service used in the hackathon."""

    def setUp(self):
        from services.google_auth import GoogleAuthService
        self.svc = GoogleAuthService()

    def test_mock_user_profile(self):
        """Verify the mock profile returns an Indian user for the demo."""
        profile = self.svc.get_user_info("any_token")
        self.assertEqual(profile["name"], "Arjun Sharma")
        self.assertIn(".in", profile["email"])

    def test_mock_login_url(self):
        """Verify the mock login returns the custom local anchor."""
        url, state = self.svc.get_authorization_url()
        self.assertEqual(url, "#mock_login")
        self.assertIsNotNone(state)


if __name__ == "__main__":
    print("🇮🇳 Starting India-Centric Services Test Suite...")
    unittest.main(verbosity=2)