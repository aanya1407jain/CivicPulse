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
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Shared mock factories ──────────────────────────────────────────────────────

def _make_st() -> MagicMock:
    st = MagicMock()
    st.session_state = {}
    return st


def _urlopen_mock(body: bytes) -> MagicMock:
    """Return a mock context-manager for urllib.request.urlopen."""
    mock_resp = MagicMock()
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__  = MagicMock(return_value=False)
    mock_resp.read.return_value = body
    return mock_resp


def _gtx_body(translated: str) -> bytes:
    return json.dumps([[[translated, "source", None, None, None]], None, "en"]).encode()


def _cloud_body(translated: str) -> bytes:
    return json.dumps({
        "data": {"translations": [{"translatedText": translated}]}
    }).encode()


def _civic_voterinfo_body() -> bytes:
    return json.dumps({
        "elections": [{
            "id": "900001",
            "name": "West Bengal Assembly Election 2026",
            "electionDay": "2026-04-23",
            "ocdDivisionId": "ocd-division/country:in/state:wb",
        }],
        "pollingLocations": [{
            "address": {"locationName": "Polling Station 1", "line1": "Main St"},
            "notes": "Bring ID",
        }],
    }).encode()


def _civic_representatives_body() -> bytes:
    return json.dumps({
        "offices": [{"name": "Member of Legislative Assembly", "officialIndices": [0]}],
        "officials": [{"name": "Test MLA", "party": "AITC"}],
    }).encode()


def _gemini_response_mock(text: str) -> MagicMock:
    mock = MagicMock()
    mock.text = text
    return mock


# ===========================================================================
#  1. Full location → election data flow
# ===========================================================================

class TestLocationToElectionDataFlow(unittest.TestCase):
    """Integration: PIN code → state code → mock results."""

    def test_wb_pin_resolves_to_wb_results(self) -> None:
        from services.election_scraper import get_state_code_from_location, fetch_results
        with patch("services.election_scraper._scrape_eci_results", return_value=None):
            sc      = get_state_code_from_location("700001")
            results = fetch_results(sc)
        self.assertEqual(sc, "WB")
        self.assertEqual(results["state"], "West Bengal")
        self.assertEqual(results["total_seats"], 294)
        fetch_results.clear()

    def test_tn_name_resolves_to_tn_results(self) -> None:
        from services.election_scraper import get_state_code_from_location, fetch_results
        with patch("services.election_scraper._scrape_eci_results", return_value=None):
            sc      = get_state_code_from_location("Tamil Nadu")
            results = fetch_results(sc)
        self.assertEqual(sc, "TN")
        self.assertEqual(results["total_seats"], 234)
        fetch_results.clear()

    def test_results_always_have_color(self) -> None:
        from services.election_scraper import fetch_results
        with patch("services.election_scraper._scrape_eci_results", return_value=None):
            results = fetch_results("WB")
        for party in results["parties"]:
            self.assertIn("color", party)
            self.assertTrue(party["color"].startswith("#"))
        fetch_results.clear()

    def test_results_always_have_total(self) -> None:
        from services.election_scraper import fetch_results
        with patch("services.election_scraper._scrape_eci_results", return_value=None):
            results = fetch_results("WB")
        for party in results["parties"]:
            self.assertIn("total", party)
            self.assertGreaterEqual(party["total"], 0)
        fetch_results.clear()

    def test_last_updated_is_populated(self) -> None:
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

    def setUp(self) -> None:
        from services.calendar_service import CalendarService
        self.svc = CalendarService()

    def test_full_election_data_generates_three_links(self) -> None:
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

    def test_missing_counting_day_generates_two_links(self) -> None:
        data  = {"jurisdiction": "Tamil Nadu", "poll_date": "2026-04-19"}
        links = self.svc.generate_reminder_links(data)
        self.assertEqual(len(links), 2)

    def test_gcal_link_has_correct_timezone(self) -> None:
        data  = {"jurisdiction": "Kerala", "poll_date": "2026-04-23"}
        links = self.svc.generate_reminder_links(data)
        for link in links:
            self.assertIn("Asia%2FKolkata", link["link"])

    def test_gcal_link_contains_emoji(self) -> None:
        link = self.svc.generate_gcal_link("Vote Today", "2026-04-23")
        self.assertIn("%F0%9F%97%B3", link)  # URL-encoded 🗳️


# ===========================================================================
#  3. Translation batch vs single consistency
# ===========================================================================

class TestTranslationBatchConsistency(unittest.TestCase):
    """Integration: batch translate should give same results as individual calls."""

    def _make_mock_resp(self, translated: str) -> MagicMock:
        return _urlopen_mock(_gtx_body(translated))

    def test_single_translate_cached_after_call(self) -> None:
        st_mock = _make_st()
        with patch("components.language_selector.st", st_mock), \
             patch("components.language_selector.GOOGLE_TRANSLATE_API_KEY", ""), \
             patch("urllib.request.urlopen", return_value=self._make_mock_resp("नमस्ते")):
            import components.language_selector as ls
            result = ls.translate_text("Hello", "hi")
        self.assertEqual(result, "नमस्ते")
        self.assertIn(("Hello", "hi"), st_mock.session_state.get("_translate_cache", {}))

    def test_english_never_hits_network(self) -> None:
        st_mock = _make_st()
        with patch("components.language_selector.st", st_mock), \
             patch("urllib.request.urlopen") as mock_open:
            import components.language_selector as ls
            ls.translate_text("Hello", "en")
            mock_open.assert_not_called()

    def test_empty_batch_returns_empty(self) -> None:
        st_mock = _make_st()
        with patch("components.language_selector.st", st_mock):
            import components.language_selector as ls
            result = ls.translate_batch([], "hi")
        self.assertEqual(result, [])

    def test_english_batch_passthrough(self) -> None:
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

    def test_xss_blocked_in_sanitize_and_validate(self) -> None:
        from utils.validators import sanitize_and_validate
        result = sanitize_and_validate('<img src=x onerror=alert(1)>')
        self.assertNotIn("<img", result)
        self.assertNotIn("onerror", result)

    def test_sql_injection_escaped(self) -> None:
        from utils.validators import sanitize_and_validate
        result = sanitize_and_validate("'; DROP TABLE voters; --")
        self.assertNotIn("<", result)

    def test_long_input_truncated_to_max(self) -> None:
        from utils.validators import sanitize_and_validate
        result = sanitize_and_validate("a" * 500, max_length=200)
        self.assertLessEqual(len(result), 200)

    def test_valid_pin_accepted(self) -> None:
        from utils.validators import validate_location_input
        self.assertTrue(validate_location_input("700001"))
        self.assertTrue(validate_location_input("600001"))

    def test_invalid_pin_rejected(self) -> None:
        from utils.validators import validate_location_input
        self.assertFalse(validate_location_input("12345"))    # 5 digits
        self.assertFalse(validate_location_input("1234567"))  # 7 digits
        self.assertFalse(validate_location_input(""))
        self.assertFalse(validate_location_input(None))       # type: ignore

    def test_state_name_accepted(self) -> None:
        from utils.validators import validate_location_input
        self.assertTrue(validate_location_input("West Bengal"))
        self.assertTrue(validate_location_input("Tamil Nadu"))

    def test_email_validation(self) -> None:
        from utils.validators import validate_email
        self.assertTrue(validate_email("voter@india.in"))
        self.assertFalse(validate_email("not-an-email"))
        self.assertFalse(validate_email(""))

    def test_indian_phone_validation(self) -> None:
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

    def test_location_parse_under_10ms(self) -> None:
        from utils.location_utils import parse_location
        start = time.perf_counter()
        for _ in range(100):
            parse_location("West Bengal")
        elapsed = (time.perf_counter() - start) / 100
        self.assertLess(elapsed, 0.01, f"parse_location too slow: {elapsed:.4f}s")

    def test_validate_location_under_1ms(self) -> None:
        from utils.validators import validate_location_input
        start = time.perf_counter()
        for _ in range(1000):
            validate_location_input("700001")
        elapsed = (time.perf_counter() - start) / 1000
        self.assertLess(elapsed, 0.001, f"validate_location_input too slow: {elapsed:.6f}s")

    def test_sanitize_text_under_1ms(self) -> None:
        from utils.location_utils import sanitize_text
        start = time.perf_counter()
        for _ in range(1000):
            sanitize_text('<script>alert("xss")</script>')
        elapsed = (time.perf_counter() - start) / 1000
        self.assertLess(elapsed, 0.001, f"sanitize_text too slow: {elapsed:.6f}s")

    def test_normalize_date_under_1ms(self) -> None:
        from services.calendar_service import CalendarService
        svc   = CalendarService()
        start = time.perf_counter()
        for _ in range(1000):
            svc._normalize_date("23 April 2026")
        elapsed = (time.perf_counter() - start) / 1000
        self.assertLess(elapsed, 0.001, f"_normalize_date too slow: {elapsed:.6f}s")

    def test_state_code_lookup_under_1ms(self) -> None:
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

    def setUp(self) -> None:
        from services.civic_api import CivicAPIService
        self.svc = CivicAPIService()

    def test_india_fallback_has_required_keys(self) -> None:
        data = self.svc._get_fallback_india_data()
        for key in ("election_name", "country_name", "next_election_date", "requirements"):
            self.assertIn(key, data)

    def test_india_requirements_is_list(self) -> None:
        data = self.svc._get_fallback_india_data()
        self.assertIsInstance(data["requirements"], list)
        self.assertGreater(len(data["requirements"]), 0)

    def test_get_polling_locations_returns_list(self) -> None:
        locs = self.svc.get_polling_locations("Kolkata")
        self.assertIsInstance(locs, list)
        self.assertGreater(len(locs), 0)

    def test_get_polling_locations_have_required_keys(self) -> None:
        locs = self.svc.get_polling_locations("Chennai")
        for loc in locs:
            self.assertIn("name", loc)
            self.assertIn("accessible", loc)
            self.assertIn("hours", loc)

    def test_no_api_key_returns_none_for_representatives(self) -> None:
        from services.civic_api import CivicAPIService
        svc    = CivicAPIService(api_key="")
        result = svc.get_representatives("West Bengal, India")
        self.assertIsNone(result)

    def test_voter_info_has_eci_links(self) -> None:
        info = self.svc.get_voter_info("700001")
        self.assertEqual(info["status"], "success")
        self.assertIn("eci.gov.in", info.get("voter_portal", "") + info.get("booth_locator", ""))

    # ── NEW: mock-based Google API path tests ────────────────────────────────

    def test_civic_voterinfo_api_called_with_key(self) -> None:
        """When a key is present and address is non-India, Civic API voterinfo is called."""
        from services.civic_api import CivicAPIService, _fetch_civic_api
        _fetch_civic_api.clear()
        body = _civic_voterinfo_body()
        with patch("services.civic_api.GOOGLE_CIVIC_API_KEY", "FAKE_KEY"), \
             patch("urllib.request.urlopen", return_value=_urlopen_mock(body)) as mock_open:
            svc    = CivicAPIService(api_key="FAKE_KEY")
            result = svc.get_election_details("US", "New York, USA")
        self.assertIsNotNone(result)
        self.assertIn("election_name", result)
        self.assertEqual(result["source"], "google_civic_api")
        _fetch_civic_api.clear()

    def test_civic_voterinfo_parsed_correctly(self) -> None:
        """_parse_civic_election extracts election_name and next_election_date."""
        from services.civic_api import CivicAPIService
        svc  = CivicAPIService()
        data = json.loads(_civic_voterinfo_body())
        result = svc._parse_civic_election(data)
        self.assertEqual(result["election_name"], "West Bengal Assembly Election 2026")
        self.assertEqual(result["next_election_date"], "2026-04-23")
        self.assertEqual(result["source"], "google_civic_api")

    def test_civic_representatives_api_called_with_key(self) -> None:
        """Representatives endpoint is called when API key is present."""
        from services.civic_api import _fetch_civic_representatives
        _fetch_civic_representatives.clear()
        body = _civic_representatives_body()
        with patch("services.civic_api.GOOGLE_CIVIC_API_KEY", "FAKE_KEY"), \
             patch("urllib.request.urlopen", return_value=_urlopen_mock(body)):
            result = _fetch_civic_representatives("London, UK")
        self.assertIsNotNone(result)
        self.assertIn("officials", result)
        _fetch_civic_representatives.clear()

    def test_civic_api_http_error_falls_back_gracefully(self) -> None:
        """HTTP error during Civic API call returns None without raising."""
        from services.civic_api import _fetch_civic_api
        _fetch_civic_api.clear()
        import urllib.error
        with patch("services.civic_api.GOOGLE_CIVIC_API_KEY", "FAKE_KEY"), \
             patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError(
                 url="", code=403, msg="Forbidden", hdrs=None, fp=None  # type: ignore
             )):
            result = _fetch_civic_api("Some Address")
        self.assertIsNone(result)
        _fetch_civic_api.clear()

    def test_civic_voterinfo_routing_india_skips_api(self) -> None:
        """India country code skips Civic API and returns local data directly."""
        from services.civic_api import CivicAPIService, _fetch_civic_api
        _fetch_civic_api.clear()
        svc = CivicAPIService(api_key="FAKE_KEY")
        with patch("services.civic_api._fetch_civic_api") as mock_fetch, \
             patch("services.civic_api._load_local_json", return_value={"country_data": {}}):
            svc.get_election_details("IN", "West Bengal")
        mock_fetch.assert_not_called()
        _fetch_civic_api.clear()


# ===========================================================================
#  7. Gemini AI — mock-based API path tests
# ===========================================================================

class TestGeminiAPIIntegration(unittest.TestCase):
    """All Gemini calls are mocked — no real API key needed."""

    def _make_model_mock(self, response_text: str) -> MagicMock:
        model = MagicMock()
        model.generate_content.return_value = _gemini_response_mock(response_text)
        return model

    def test_gemini_model_called_with_correct_prompt_structure(self) -> None:
        """generate_content is called exactly once with voter context prefix."""
        model = self._make_model_mock("You can vote at your nearest booth.")
        with patch("app._get_gemini_model", return_value=model), \
             patch("app.GOOGLE_API_KEY", "FAKE"), \
             patch("app.SECURITY", {"max_input_length": 200}), \
             patch("app.st") as mock_st:
            mock_st.session_state = {"gemini_token_count": 0}
            import app
            result = app._call_gemini("How do I vote?", {"election_name": "WB Election"})
        model.generate_content.assert_called_once()
        call_args = str(model.generate_content.call_args)
        self.assertIn("How do I vote?", call_args)
        self.assertIn("WB Election", call_args)

    def test_gemini_rate_limit_blocks_after_20_queries(self) -> None:
        """Once gemini_token_count >= 20, returns rate-limit message without calling API."""
        model = self._make_model_mock("Should not be called")
        with patch("app._get_gemini_model", return_value=model), \
             patch("app.GOOGLE_API_KEY", "FAKE"), \
             patch("app.SECURITY", {"max_input_length": 200}), \
             patch("app.INDIA", {"VOTER_HELPLINE": "1950"}), \
             patch("app.st") as mock_st:
            mock_st.session_state = {"gemini_token_count": 20}
            import app
            result = app._call_gemini("Any question", {})
        model.generate_content.assert_not_called()
        self.assertIn("limit", result.lower())

    def test_gemini_input_too_long_blocked(self) -> None:
        """Input exceeding max_input_length returns warning without calling API."""
        model = self._make_model_mock("Should not be called")
        with patch("app._get_gemini_model", return_value=model), \
             patch("app.GOOGLE_API_KEY", "FAKE"), \
             patch("app.SECURITY", {"max_input_length": 10}), \
             patch("app.st") as mock_st:
            mock_st.session_state = {"gemini_token_count": 0}
            import app
            result = app._call_gemini("This input is too long for the limit", {})
        model.generate_content.assert_not_called()
        self.assertIn("long", result.lower())

    def test_gemini_none_model_returns_warning(self) -> None:
        """When _get_gemini_model returns None, returns friendly error without crashing."""
        with patch("app._get_gemini_model", return_value=None), \
             patch("app.GOOGLE_API_KEY", "FAKE"), \
             patch("app.SECURITY", {"max_input_length": 200}), \
             patch("app.st") as mock_st:
            mock_st.session_state = {"gemini_token_count": 0}
            import app
            result = app._call_gemini("How do I vote?", {})
        self.assertIn("unavailable", result.lower())

    def test_gemini_api_exception_returns_friendly_error(self) -> None:
        """API exception is caught and returns a user-friendly message."""
        model = MagicMock()
        model.generate_content.side_effect = Exception("API quota exceeded")
        with patch("app._get_gemini_model", return_value=model), \
             patch("app.GOOGLE_API_KEY", "FAKE"), \
             patch("app.SECURITY", {"max_input_length": 200}), \
             patch("app.INDIA", {"VOTER_HELPLINE": "1950"}), \
             patch("app.st") as mock_st:
            mock_st.session_state = {"gemini_token_count": 0}
            import app
            result = app._call_gemini("How do I vote?", {})
        self.assertIn("Error", result)
        self.assertNotIn("Traceback", result)

    def test_gemini_token_count_increments(self) -> None:
        """Each successful call increments gemini_token_count by 1."""
        model = self._make_model_mock("Here is your answer.")
        session = {"gemini_token_count": 3}
        with patch("app._get_gemini_model", return_value=model), \
             patch("app.GOOGLE_API_KEY", "FAKE"), \
             patch("app.SECURITY", {"max_input_length": 200}), \
             patch("app.st") as mock_st:
            mock_st.session_state = session
            import app
            app._call_gemini("Question", {"election_name": "Test"})
        self.assertEqual(session["gemini_token_count"], 4)


# ===========================================================================
#  8. Google Cloud Translate API — mock-based path tests
# ===========================================================================

class TestCloudTranslateAPIIntegration(unittest.TestCase):
    """Verify the Cloud Translation API is used when key is present."""

    def test_cloud_api_endpoint_called_when_key_set(self) -> None:
        """Cloud Translation endpoint is called (not gtx) when key is configured."""
        st_mock = _make_st()
        body    = _cloud_body("मतदाता")
        with patch("components.language_selector.st", st_mock), \
             patch("components.language_selector.GOOGLE_TRANSLATE_API_KEY", "FAKE_KEY"), \
             patch("urllib.request.urlopen", return_value=_urlopen_mock(body)) as mock_open:
            import components.language_selector as ls
            result = ls.translate_text("Voter", "hi")
        self.assertEqual(result, "मतदाता")
        called_url = str(mock_open.call_args)
        self.assertIn("translation.googleapis.com", called_url)

    def test_gtx_fallback_when_cloud_key_absent(self) -> None:
        """gtx endpoint is used when no Cloud API key is configured."""
        st_mock = _make_st()
        body    = _gtx_body("मतदाता")
        with patch("components.language_selector.st", st_mock), \
             patch("components.language_selector.GOOGLE_TRANSLATE_API_KEY", ""), \
             patch("urllib.request.urlopen", return_value=_urlopen_mock(body)) as mock_open:
            import components.language_selector as ls
            result = ls.translate_text("Voter", "hi")
        self.assertEqual(result, "मतदाता")
        called_url = str(mock_open.call_args)
        self.assertIn("translate.googleapis.com", called_url)

    def test_cloud_api_failure_falls_back_to_gtx(self) -> None:
        """When Cloud API raises, gtx is tried next and result returned."""
        st_mock   = _make_st()
        gtx_body  = _gtx_body("मतदाता")

        def side_effect(req, timeout=5):  # type: ignore[no-untyped-def]
            url = req.full_url if hasattr(req, "full_url") else str(req)
            if "translation.googleapis.com" in url:
                raise Exception("Cloud API down")
            return _urlopen_mock(gtx_body)

        with patch("components.language_selector.st", st_mock), \
             patch("components.language_selector.GOOGLE_TRANSLATE_API_KEY", "FAKE_KEY"), \
             patch("urllib.request.urlopen", side_effect=side_effect):
            import components.language_selector as ls
            result = ls.translate_text("Voter", "hi")
        self.assertEqual(result, "मतदाता")

    def test_cloud_batch_api_called_when_key_set(self) -> None:
        """Cloud batch endpoint is used for translate_batch when key is present."""
        st_mock = _make_st()
        body = json.dumps({
            "data": {
                "translations": [
                    {"translatedText": "मतदाता"},
                    {"translatedText": "बूथ"},
                ]
            }
        }).encode()
        with patch("components.language_selector.st", st_mock), \
             patch("components.language_selector.GOOGLE_TRANSLATE_API_KEY", "FAKE_KEY"), \
             patch("urllib.request.urlopen", return_value=_urlopen_mock(body)) as mock_open:
            import components.language_selector as ls
            results = ls.translate_batch(["Voter", "Booth"], "hi")
        self.assertEqual(results, ["मतदाता", "बूथ"])
        called_url = str(mock_open.call_args)
        self.assertIn("translation.googleapis.com", called_url)

    def test_lang_attribute_injected_on_switch(self) -> None:
        """render_language_selector injects lang= HTML attribute when non-English."""
        st_mock = _make_st()
        st_mock.session_state["language"] = "hi"
        st_mock.selectbox.return_value    = "हिंदी (Hindi)"
        with patch("components.language_selector.st", st_mock):
            import components.language_selector as ls
            ls.render_language_selector()
        # Check that st.markdown was called with lang="hi"
        calls = [str(c) for c in st_mock.markdown.call_args_list]
        self.assertTrue(
            any('lang="hi"' in c for c in calls),
            "Expected lang='hi' to be injected via st.markdown"
        )

    def test_translate_rate_limit_resets_on_language_change(self) -> None:
        """Switching language resets the per-session call counter to 0."""
        st_mock = _make_st()
        st_mock.session_state["language"]              = "en"
        st_mock.session_state["_translate_call_count"] = 150
        st_mock.selectbox.return_value = "हिंदी (Hindi)"
        with patch("components.language_selector.st", st_mock):
            import components.language_selector as ls
            try:
                ls.render_language_selector()
            except Exception:
                pass  # st.rerun() raises in test context — expected
        self.assertEqual(st_mock.session_state.get("_translate_call_count", 0), 0)


# ===========================================================================
#  9. Property-style tests — invariants that must hold for all inputs
# ===========================================================================

class TestInvariants(unittest.TestCase):
    """
    Property-based style tests: verify invariants hold across many inputs.
    Replaces hypothesis dependency with deterministic parameterised checks.
    """

    _PIN_PREFIXES = [
        "110", "400", "600", "700", "411", "500",
        "302", "226", "380", "695", "641", "680",
    ]
    _STATE_NAMES = [
        "West Bengal", "Tamil Nadu", "Kerala", "Maharashtra",
        "Delhi", "Rajasthan", "Karnataka", "Gujarat", "Assam",
    ]
    _EDGE_CASES = ["", "   ", "abc", "999999", "12345", None]

    def test_validate_location_always_returns_bool(self) -> None:
        from utils.validators import validate_location_input
        for prefix in self._PIN_PREFIXES:
            pin = prefix + "001"
            self.assertIsInstance(validate_location_input(pin), bool)
        for name in self._STATE_NAMES:
            self.assertIsInstance(validate_location_input(name), bool)
        for edge in self._EDGE_CASES:
            self.assertIsInstance(validate_location_input(edge), bool)

    def test_get_state_code_never_raises(self) -> None:
        from services.election_scraper import get_state_code_from_location
        all_inputs = (
            [p + "001" for p in self._PIN_PREFIXES]
            + self._STATE_NAMES
            + [e for e in self._EDGE_CASES if e is not None]
        )
        for inp in all_inputs:
            try:
                result = get_state_code_from_location(inp)
                self.assertIsInstance(result, str)
            except Exception as exc:
                self.fail(f"get_state_code_from_location({inp!r}) raised: {exc}")

    def test_sanitize_text_never_raises(self) -> None:
        from utils.location_utils import sanitize_text
        evil_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE voters; --",
            "<img src=x onerror=alert(1)>",
            "A" * 10_000,
            "",
            "   ",
            "\x00\x01\x02",
            "Normal text",
        ]
        for inp in evil_inputs:
            try:
                result = sanitize_text(inp)
                self.assertIsInstance(result, str)
                self.assertNotIn("<script>", result)
            except Exception as exc:
                self.fail(f"sanitize_text raised on {inp[:40]!r}: {exc}")

    def test_translate_text_never_raises_for_any_input(self) -> None:
        st_mock = _make_st()
        import urllib.error
        with patch("components.language_selector.st", st_mock), \
             patch("components.language_selector.GOOGLE_TRANSLATE_API_KEY", ""), \
             patch("urllib.request.urlopen", side_effect=urllib.error.URLError("forced")):
            import components.language_selector as ls
            edge_inputs = ["", "   ", "A" * 1000, "Normal", "<script>"]
            for lang in ["hi", "bn", "ta", "en"]:
                for text in edge_inputs:
                    try:
                        result = ls.translate_text(text, lang)
                        self.assertIsInstance(result, str)
                    except Exception as exc:
                        self.fail(f"translate_text({text!r}, {lang!r}) raised: {exc}")

    def test_fetch_results_never_raises_for_known_states(self) -> None:
        from services.election_scraper import fetch_results, STATE_MOCK
        for code in STATE_MOCK:
            with patch("services.election_scraper._scrape_eci_results", return_value=None):
                try:
                    result = fetch_results(code)
                    self.assertIn("parties", result)
                    self.assertIn("total_seats", result)
                except Exception as exc:
                    self.fail(f"fetch_results({code!r}) raised: {exc}")
                finally:
                    fetch_results.clear()

    def test_polling_locations_always_accessible_flag(self) -> None:
        """Every polling location returned by the service has an 'accessible' flag."""
        from services.civic_api import CivicAPIService
        svc = CivicAPIService()
        locations = ["Kolkata", "Chennai", "Mumbai", "Delhi", "Kochi", "Jaipur"]
        for loc in locations:
            for station in svc.get_polling_locations(loc):
                self.assertIn("accessible", station,
                              msg=f"Missing 'accessible' for station in {loc}")
                self.assertIsInstance(station["accessible"], bool)


if __name__ == "__main__":
    print("🇮🇳 Running CivicPulse Integration & Performance Tests…")
    unittest.main(verbosity=2)
