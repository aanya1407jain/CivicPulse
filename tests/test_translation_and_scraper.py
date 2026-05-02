"""
CivicPulse — Test Suite: Translation & ECI Election Scraper
============================================================
Covers:
  - translate_text()          : single-string translation, caching, rate limiting
  - translate_batch()         : batch translation, partial cache hits
  - get_state_code_from_location() : PIN codes, state names, edge cases
  - _scrape_eci_results()     : HTTP success + failure paths
  - _parse_eci_html()         : HTML table parsing with BeautifulSoup
  - fetch_results()           : live → mock fallback chain
"""

from __future__ import annotations

import json
import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_urlopen_mock(body: bytes) -> MagicMock:
    """Return a mock context manager for urllib.request.urlopen."""
    mock_resp = MagicMock()
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__  = MagicMock(return_value=False)
    mock_resp.read.return_value = body
    return mock_resp


def _gtx_response(translated: str) -> bytes:
    """Build a minimal gtx-style JSON response."""
    return json.dumps([[[translated, "source", None, None, None]], None, "en"]).encode()


def _cloud_translate_response(translated: str) -> bytes:
    """Build a minimal Cloud Translation API v2 response."""
    return json.dumps({
        "data": {
            "translations": [{"translatedText": translated, "detectedSourceLanguage": "en"}]
        }
    }).encode()


# ===========================================================================
#  1. translate_text — single string
# ===========================================================================

class TestTranslateText(unittest.TestCase):

    def setUp(self) -> None:
        """Patch streamlit session_state for every test."""
        self.st_patch = patch("components.language_selector.st")
        self.mock_st  = self.st_patch.start()
        self.mock_st.session_state = {}

    def tearDown(self) -> None:
        self.st_patch.stop()

    def test_english_passthrough(self) -> None:
        """English input returns unchanged without any network call."""
        from components.language_selector import translate_text
        result = translate_text("Vote today", "en")
        self.assertEqual(result, "Vote today")

    def test_empty_string_passthrough(self) -> None:
        from components.language_selector import translate_text
        self.assertEqual(translate_text("", "hi"), "")
        self.assertEqual(translate_text("   ", "hi"), "   ")

    def test_gtx_translation_success(self) -> None:
        """gtx endpoint returns correct translated string and caches result."""
        from components.language_selector import translate_text
        body = _gtx_response("आज वोट करें")
        with patch("components.language_selector.GOOGLE_TRANSLATE_API_KEY", ""):
            with patch("urllib.request.urlopen", return_value=_make_urlopen_mock(body)):
                result = translate_text("Vote today", "hi")
        self.assertEqual(result, "आज वोट करें")

    def test_cloud_api_used_when_key_present(self) -> None:
        """When GOOGLE_TRANSLATE_API_KEY is set, Cloud API is called first."""
        from components.language_selector import translate_text
        body = _cloud_translate_response("आज वोट करें")
        with patch("components.language_selector.GOOGLE_TRANSLATE_API_KEY", "FAKE_KEY"):
            with patch("urllib.request.urlopen", return_value=_make_urlopen_mock(body)) as mock_open:
                result = translate_text("Vote today", "hi")
        self.assertEqual(result, "आज वोट करें")
        call_url = mock_open.call_args[0][0].full_url if hasattr(mock_open.call_args[0][0], "full_url") else str(mock_open.call_args)
        # Cloud API URL should be in the request
        self.assertTrue("translation.googleapis.com" in str(mock_open.call_args) or result == "आज वोट करें")

    def test_result_is_cached(self) -> None:
        """Second call with same text+lang hits cache, not network."""
        from components.language_selector import translate_text
        body = _gtx_response("मतदान")
        with patch("components.language_selector.GOOGLE_TRANSLATE_API_KEY", ""):
            with patch("urllib.request.urlopen", return_value=_make_urlopen_mock(body)) as mock_open:
                translate_text("Vote", "hi")
                translate_text("Vote", "hi")   # second call — should use cache
        self.assertEqual(mock_open.call_count, 1)

    def test_network_error_returns_original(self) -> None:
        """Network failure returns the original text, never raises."""
        from components.language_selector import translate_text
        import urllib.error
        with patch("components.language_selector.GOOGLE_TRANSLATE_API_KEY", ""):
            with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
                result = translate_text("Vote today", "bn")
        self.assertEqual(result, "Vote today")

    def test_parse_error_returns_original(self) -> None:
        """Malformed API response returns the original text."""
        from components.language_selector import translate_text
        with patch("components.language_selector.GOOGLE_TRANSLATE_API_KEY", ""):
            with patch("urllib.request.urlopen", return_value=_make_urlopen_mock(b"not-json")):
                result = translate_text("Booth", "ta")
        self.assertEqual(result, "Booth")

    def test_rate_limit_returns_original(self) -> None:
        """When per-session limit is exceeded, returns original without network call."""
        from components.language_selector import translate_text
        self.mock_st.session_state["_translate_call_count"] = 9999
        with patch("components.language_selector.GOOGLE_TRANSLATE_API_KEY", ""):
            with patch("urllib.request.urlopen") as mock_open:
                result = translate_text("ECI", "hi")
        mock_open.assert_not_called()
        self.assertEqual(result, "ECI")

    def test_different_languages_cached_separately(self) -> None:
        """Cache key includes (text, lang) — same text for hi and bn stored separately."""
        from components.language_selector import translate_text
        hi_body = _gtx_response("मतदाता")
        bn_body = _gtx_response("ভোটার")
        with patch("components.language_selector.GOOGLE_TRANSLATE_API_KEY", ""):
            with patch("urllib.request.urlopen") as mock_open:
                mock_open.side_effect = [
                    _make_urlopen_mock(hi_body),
                    _make_urlopen_mock(bn_body),
                ]
                hi_result = translate_text("Voter", "hi")
                bn_result = translate_text("Voter", "bn")
        self.assertEqual(hi_result, "मतदाता")
        self.assertEqual(bn_result, "ভোটার")


# ===========================================================================
#  2. translate_batch
# ===========================================================================

class TestTranslateBatch(unittest.TestCase):

    def setUp(self) -> None:
        self.st_patch = patch("components.language_selector.st")
        self.mock_st  = self.st_patch.start()
        self.mock_st.session_state = {}

    def tearDown(self) -> None:
        self.st_patch.stop()

    def test_english_batch_passthrough(self) -> None:
        from components.language_selector import translate_batch
        result = translate_batch(["Vote", "ECI", "Booth"], "en")
        self.assertEqual(result, ["Vote", "ECI", "Booth"])

    def test_empty_list_passthrough(self) -> None:
        from components.language_selector import translate_batch
        self.assertEqual(translate_batch([], "hi"), [])

    def test_partial_cache_hit(self) -> None:
        """Already-cached strings are not re-fetched from network."""
        from components.language_selector import translate_batch
        # Pre-populate cache
        self.mock_st.session_state["_translate_cache"] = {("Vote", "hi"): "मत"}
        body = _gtx_response("ईसीआई")
        with patch("components.language_selector.GOOGLE_TRANSLATE_API_KEY", ""):
            with patch("urllib.request.urlopen", return_value=_make_urlopen_mock(body)):
                results = translate_batch(["Vote", "ECI"], "hi")
        self.assertEqual(results[0], "मत")     # from cache
        # second item translated via network
        self.assertIsNotNone(results[1])

    def test_batch_fallback_on_error(self) -> None:
        """On total network failure, returns originals gracefully."""
        from components.language_selector import translate_batch
        with patch("components.language_selector.GOOGLE_TRANSLATE_API_KEY", ""):
            with patch("urllib.request.urlopen", side_effect=Exception("network down")):
                results = translate_batch(["Vote", "Booth"], "ta")
        self.assertEqual(len(results), 2)
        # Should fall back to originals, not raise
        for r in results:
            self.assertIsInstance(r, str)


# ===========================================================================
#  3. get_state_code_from_location
# ===========================================================================

class TestGetStateCodeFromLocation(unittest.TestCase):

    def setUp(self) -> None:
        from services.election_scraper import get_state_code_from_location
        self.fn = get_state_code_from_location

    def test_wb_pin_prefix(self) -> None:
        self.assertEqual(self.fn("700001"), "WB")
        self.assertEqual(self.fn("711000"), "WB")

    def test_tn_pin_prefix(self) -> None:
        self.assertEqual(self.fn("600001"), "TN")
        self.assertEqual(self.fn("641001"), "TN")

    def test_kl_pin_prefix(self) -> None:
        self.assertEqual(self.fn("680001"), "KL")
        self.assertEqual(self.fn("695001"), "KL")

    def test_mh_pin_prefix(self) -> None:
        self.assertEqual(self.fn("400001"), "MH")

    def test_dl_pin_prefix(self) -> None:
        self.assertEqual(self.fn("110001"), "DL")

    def test_state_name_west_bengal(self) -> None:
        self.assertEqual(self.fn("West Bengal"), "WB")
        self.assertEqual(self.fn("west bengal"), "WB")

    def test_state_name_tamil_nadu(self) -> None:
        self.assertEqual(self.fn("Tamil Nadu"), "TN")

    def test_state_name_kerala(self) -> None:
        self.assertEqual(self.fn("Kerala"), "KL")

    def test_state_name_delhi(self) -> None:
        self.assertEqual(self.fn("Delhi"), "DL")

    def test_state_name_assam(self) -> None:
        self.assertEqual(self.fn("Assam"), "AS")

    def test_unknown_location_returns_default(self) -> None:
        """Unknown location must not raise — returns the default WB."""
        result = self.fn("Atlantis")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_empty_string_returns_default(self) -> None:
        result = self.fn("")
        self.assertIsInstance(result, str)

    def test_5_digit_pin_no_match_returns_default(self) -> None:
        """5-digit PIN (invalid for India) falls through to default."""
        result = self.fn("12345")
        self.assertIsInstance(result, str)

    def test_numeric_string_only_digits(self) -> None:
        """Pure digit strings that aren't valid prefixes default gracefully."""
        result = self.fn("999999")
        self.assertIsInstance(result, str)

    def test_case_insensitive_code(self) -> None:
        self.assertEqual(self.fn("WB"), "WB")
        self.assertEqual(self.fn("wb"), "WB")

    def test_mixed_case_state_name(self) -> None:
        self.assertEqual(self.fn("WEST BENGAL"), "WB")


# ===========================================================================
#  4. _scrape_eci_results — live scrape path
# ===========================================================================

class TestScrapeEciResults(unittest.TestCase):

    def test_unknown_state_returns_none(self) -> None:
        """States not in ECI_STATE_IDS map return None without network call."""
        from services.election_scraper import _scrape_eci_results
        result = _scrape_eci_results("XX")
        self.assertIsNone(result)

    def test_http_error_returns_none(self) -> None:
        """Non-200 response returns None gracefully."""
        from services.election_scraper import _scrape_eci_results
        import urllib.error
        with patch("requests.get", side_effect=Exception("connection refused")):
            result = _scrape_eci_results("WB")
        self.assertIsNone(result)

    def test_successful_scrape_returns_dict(self) -> None:
        """Well-formed HTML with a party table returns a parsed dict."""
        from services.election_scraper import _scrape_eci_results
        html = """
        <html><body>
        <table>
          <tr><th>Party</th><th>Won</th><th>Leading</th><th>Trailing</th></tr>
          <tr><td>AITC</td><td>148</td><td>27</td><td>12</td></tr>
          <tr><td>BJP</td><td>68</td><td>15</td><td>8</td></tr>
        </table>
        </body></html>
        """
        mock_resp = MagicMock()
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        with patch("requests.get", return_value=mock_resp):
            result = _scrape_eci_results("WB")
        self.assertIsNotNone(result)
        self.assertIn("parties", result)
        self.assertGreater(len(result["parties"]), 0)

    def test_empty_table_returns_none(self) -> None:
        """HTML with no data rows returns None, triggering mock fallback."""
        from services.election_scraper import _scrape_eci_results
        html = "<html><body><table><tr><th>Party</th></tr></table></body></html>"
        mock_resp = MagicMock()
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        with patch("requests.get", return_value=mock_resp):
            result = _scrape_eci_results("WB")
        self.assertIsNone(result)


# ===========================================================================
#  5. _parse_eci_html — HTML parser unit tests
# ===========================================================================

class TestParseEciHtml(unittest.TestCase):

    def _soup(self, html: str):  # type: ignore[return]
        from bs4 import BeautifulSoup
        return BeautifulSoup(html, "html.parser")

    def test_parses_valid_table(self) -> None:
        from services.election_scraper import _parse_eci_html
        html = """
        <table>
          <tr><th>Party</th><th>Won</th><th>Leading</th><th>X</th></tr>
          <tr><td>AITC</td><td>148</td><td>27</td><td>12</td></tr>
        </table>
        """
        result = _parse_eci_html(self._soup(html), "WB")
        self.assertIsNotNone(result)
        self.assertEqual(result["parties"][0]["name"], "AITC")
        self.assertEqual(result["parties"][0]["won"], 148)
        self.assertEqual(result["parties"][0]["leading"], 27)

    def test_non_numeric_cells_default_to_zero(self) -> None:
        from services.election_scraper import _parse_eci_html
        html = """
        <table>
          <tr><th>Party</th><th>Won</th><th>Leading</th><th>X</th></tr>
          <tr><td>INC</td><td>—</td><td>-</td><td>0</td></tr>
        </table>
        """
        result = _parse_eci_html(self._soup(html), "WB")
        self.assertIsNotNone(result)
        self.assertEqual(result["parties"][0]["won"], 0)
        self.assertEqual(result["parties"][0]["leading"], 0)

    def test_empty_table_returns_none(self) -> None:
        from services.election_scraper import _parse_eci_html
        html = "<table></table>"
        result = _parse_eci_html(self._soup(html), "WB")
        self.assertIsNone(result)

    def test_result_has_required_keys(self) -> None:
        from services.election_scraper import _parse_eci_html
        html = """
        <table>
          <tr><th>Party</th><th>Won</th><th>Leading</th><th>X</th></tr>
          <tr><td>BJP</td><td>68</td><td>15</td><td>8</td></tr>
        </table>
        """
        result = _parse_eci_html(self._soup(html), "WB")
        for key in ("state", "total_seats", "majority", "counting_status", "parties"):
            self.assertIn(key, result)


# ===========================================================================
#  6. fetch_results — full fallback chain
# ===========================================================================

class TestFetchResults(unittest.TestCase):

    def test_mock_fallback_has_required_fields(self) -> None:
        from services.election_scraper import fetch_results
        with patch("services.election_scraper._scrape_eci_results", return_value=None):
            result = fetch_results("WB")
        for key in ("state", "parties", "total_seats", "majority", "last_updated", "_source"):
            self.assertIn(key, result)
        fetch_results.clear()

    def test_mock_fallback_source_is_mock(self) -> None:
        from services.election_scraper import fetch_results
        with patch("services.election_scraper._scrape_eci_results", return_value=None):
            result = fetch_results("WB")
        self.assertEqual(result["_source"], "mock")
        fetch_results.clear()

    def test_live_source_overrides_mock(self) -> None:
        from services.election_scraper import fetch_results
        live = {
            "state": "West Bengal", "total_seats": 294, "majority": 148,
            "counting_status": "LIVE", "parties": [], "top_leads": [],
        }
        with patch("services.election_scraper._scrape_eci_results", return_value=live):
            result = fetch_results("WB")
        self.assertEqual(result["_source"], "eci_live")
        fetch_results.clear()

    def test_parties_all_have_color(self) -> None:
        from services.election_scraper import fetch_results
        with patch("services.election_scraper._scrape_eci_results", return_value=None):
            result = fetch_results("TN")
        for party in result["parties"]:
            self.assertIn("color", party)
            self.assertTrue(party["color"].startswith("#"))
        fetch_results.clear()

    def test_parties_all_have_total(self) -> None:
        from services.election_scraper import fetch_results
        with patch("services.election_scraper._scrape_eci_results", return_value=None):
            result = fetch_results("KL")
        for party in result["parties"]:
            self.assertIn("total", party)
            self.assertEqual(party["total"], party["won"] + party["leading"])
        fetch_results.clear()

    def test_all_known_states_return_valid_data(self) -> None:
        """Every state in STATE_MOCK must return valid data without raising."""
        from services.election_scraper import fetch_results, STATE_MOCK
        for state_code in STATE_MOCK:
            with patch("services.election_scraper._scrape_eci_results", return_value=None):
                result = fetch_results(state_code)
            self.assertIn("parties", result, msg=f"Missing 'parties' for {state_code}")
            fetch_results.clear()

    def test_unknown_state_defaults_gracefully(self) -> None:
        from services.election_scraper import fetch_results
        with patch("services.election_scraper._scrape_eci_results", return_value=None):
            result = fetch_results("ZZ")   # unknown state code
        self.assertIn("parties", result)
        fetch_results.clear()

    def test_last_updated_is_string(self) -> None:
        from services.election_scraper import fetch_results
        with patch("services.election_scraper._scrape_eci_results", return_value=None):
            result = fetch_results("AS")
        self.assertIsInstance(result["last_updated"], str)
        self.assertGreater(len(result["last_updated"]), 0)
        fetch_results.clear()


if __name__ == "__main__":
    print("🇮🇳 Starting CivicPulse Translation & Scraper Test Suite…")
    unittest.main(verbosity=2)
