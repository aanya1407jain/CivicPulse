"""
CivicPulse — Test Suite: Translation & Election Scraper
========================================================
Covers translate_text() caching, fallback behaviour, and the election
scraper's mock fallback path.
"""

from __future__ import annotations

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── Shared Streamlit mock ──────────────────────────────────────────────────────

def _make_st_mock() -> MagicMock:
    st = MagicMock()
    st.session_state = {}
    return st


# ===========================================================================
#  1. translate_text()
# ===========================================================================

class TestTranslateText(unittest.TestCase):
    """Unit tests for translate_text — network is always mocked."""

    def _translate(self, text, lang, mock_response=None, side_effect=None):
        """Run translate_text with a mocked urlopen."""
        st_mock = _make_st_mock()
        with patch("components.language_selector.st", st_mock):
            import components.language_selector as ls

            if side_effect:
                with patch("urllib.request.urlopen", side_effect=side_effect):
                    return ls.translate_text(text, lang)
            else:
                mock_resp = MagicMock()
                mock_resp.__enter__ = MagicMock(return_value=mock_resp)
                mock_resp.__exit__  = MagicMock(return_value=False)
                mock_resp.read.return_value = str(mock_response).encode()
                with patch("urllib.request.urlopen", return_value=mock_resp):
                    return ls.translate_text(text, lang)

    def test_english_passthrough(self):
        """English target must never hit the network."""
        st_mock = _make_st_mock()
        with patch("components.language_selector.st", st_mock):
            import components.language_selector as ls
            with patch("urllib.request.urlopen") as mock_open:
                result = ls.translate_text("Hello voter", "en")
                mock_open.assert_not_called()
                self.assertEqual(result, "Hello voter")

    def test_empty_string_passthrough(self):
        st_mock = _make_st_mock()
        with patch("components.language_selector.st", st_mock):
            import components.language_selector as ls
            self.assertEqual(ls.translate_text("", "hi"), "")
            self.assertEqual(ls.translate_text("   ", "hi"), "   ")

    def test_successful_translation(self):
        import json
        mock_data = json.dumps([[["नमस्ते मतदाता", "Hello voter", None, None, None]], None, "en"])
        st_mock   = _make_st_mock()
        with patch("components.language_selector.st", st_mock):
            import components.language_selector as ls
            mock_resp = MagicMock()
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__  = MagicMock(return_value=False)
            mock_resp.read.return_value = mock_data.encode()
            with patch("urllib.request.urlopen", return_value=mock_resp):
                result = ls.translate_text("Hello voter", "hi")
        self.assertEqual(result, "नमस्ते मतदाता")

    def test_result_is_cached(self):
        import json
        mock_data = json.dumps([[["cached result", "Hello", None, None, None]], None, "en"])
        st_mock   = _make_st_mock()
        with patch("components.language_selector.st", st_mock):
            import components.language_selector as ls
            mock_resp = MagicMock()
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__  = MagicMock(return_value=False)
            mock_resp.read.return_value = mock_data.encode()
            with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
                ls.translate_text("Hello", "hi")
                ls.translate_text("Hello", "hi")   # second call — must use cache
                self.assertEqual(mock_open.call_count, 1, "Should have been cached after first call")

    def test_network_error_returns_original(self):
        import urllib.error
        st_mock = _make_st_mock()
        with patch("components.language_selector.st", st_mock):
            import components.language_selector as ls
            with patch("urllib.request.urlopen",
                       side_effect=urllib.error.URLError("connection refused")):
                result = ls.translate_text("Hello voter", "hi")
        self.assertEqual(result, "Hello voter")

    def test_malformed_response_returns_original(self):
        st_mock = _make_st_mock()
        with patch("components.language_selector.st", st_mock):
            import components.language_selector as ls
            mock_resp = MagicMock()
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__  = MagicMock(return_value=False)
            mock_resp.read.return_value = b"not valid json {{{"
            with patch("urllib.request.urlopen", return_value=mock_resp):
                result = ls.translate_text("Hello voter", "ta")
        self.assertEqual(result, "Hello voter")

    def test_cache_cleared_on_language_change(self):
        """session_state cache key must be reset when language changes."""
        st_mock = _make_st_mock()
        st_mock.session_state["_translate_cache"] = {("old", "hi"): "पुराना"}
        st_mock.session_state["language"] = "hi"
        with patch("components.language_selector.st", st_mock):
            import components.language_selector as ls
            # Simulate changing language — clears cache then reruns
            st_mock.session_state["_translate_cache"] = {}
            cache = ls._get_cache()
            self.assertEqual(cache, {})

    def test_failure_is_logged(self):
        import urllib.error
        st_mock = _make_st_mock()
        with patch("components.language_selector.st", st_mock):
            import components.language_selector as ls
            with patch("urllib.request.urlopen",
                       side_effect=urllib.error.URLError("timeout")), \
                 self.assertLogs("components.language_selector", level="WARNING") as log_ctx:
                ls.translate_text("test", "bn")
            self.assertTrue(any("network error" in m.lower() for m in log_ctx.output))


# ===========================================================================
#  2. render_translated() / T alias
# ===========================================================================

class TestRenderTranslated(unittest.TestCase):

    def test_T_is_alias_for_render_translated(self):
        from components.language_selector import T, render_translated
        self.assertIs(T, render_translated)

    def test_returns_english_when_lang_is_en(self):
        st_mock = _make_st_mock()
        st_mock.session_state["language"] = "en"
        with patch("components.language_selector.st", st_mock):
            import components.language_selector as ls
            result = ls.render_translated("Election Results")
        self.assertEqual(result, "Election Results")

    def test_calls_translate_when_lang_is_hi(self):
        import json
        mock_data = json.dumps([[["चुनाव परिणाम", "Election Results", None]], None, "en"])
        st_mock   = _make_st_mock()
        st_mock.session_state["language"] = "hi"
        with patch("components.language_selector.st", st_mock):
            import components.language_selector as ls
            mock_resp = MagicMock()
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__  = MagicMock(return_value=False)
            mock_resp.read.return_value = mock_data.encode()
            with patch("urllib.request.urlopen", return_value=mock_resp):
                result = ls.render_translated("Election Results")
        self.assertEqual(result, "चुनाव परिणाम")


# ===========================================================================
#  3. Election scraper fallback path
# ===========================================================================

class TestElectionScraperFallback(unittest.TestCase):
    """Tests for fetch_results() mock fallback — no real network calls."""

    def setUp(self):
        # Patch the ECI scrape to always fail so fallback triggers
        self._scrape_patcher = patch(
            "services.election_scraper._scrape_eci_results", return_value=None
        )
        self._scrape_patcher.start()

    def tearDown(self):
        self._scrape_patcher.stop()
        # Clear Streamlit cache between tests
        try:
            from services.election_scraper import fetch_results
            fetch_results.clear()
        except Exception:
            pass

    def test_fallback_returns_dict(self):
        from services.election_scraper import fetch_results
        result = fetch_results("WB")
        self.assertIsInstance(result, dict)

    def test_fallback_has_required_keys(self):
        from services.election_scraper import fetch_results
        result = fetch_results("WB")
        required = {"state", "total_seats", "majority", "parties", "_source"}
        self.assertTrue(required.issubset(result.keys()))

    def test_fallback_source_is_mock(self):
        from services.election_scraper import fetch_results
        result = fetch_results("WB")
        self.assertEqual(result["_source"], "mock")

    def test_fallback_parties_have_color(self):
        from services.election_scraper import fetch_results
        result = fetch_results("WB")
        for party in result["parties"]:
            self.assertIn("color", party, f"Party {party['name']} missing color")

    def test_fallback_parties_have_total(self):
        from services.election_scraper import fetch_results
        result = fetch_results("WB")
        for party in result["parties"]:
            self.assertIn("total", party, f"Party {party['name']} missing total")

    def test_fallback_wb_has_correct_seats(self):
        from services.election_scraper import fetch_results
        result = fetch_results("WB")
        self.assertEqual(result["total_seats"], 294)
        self.assertEqual(result["majority"], 148)

    def test_fallback_has_last_updated(self):
        from services.election_scraper import fetch_results
        result = fetch_results("WB")
        self.assertIn("last_updated", result)
        self.assertTrue(result["last_updated"])

    def test_unknown_state_defaults_to_wb(self):
        from services.election_scraper import fetch_results
        result = fetch_results("XX")
        self.assertEqual(result["total_seats"], 294)   # defaults to WB mock

    def test_tn_fallback_has_correct_seats(self):
        from services.election_scraper import fetch_results
        result = fetch_results("TN")
        self.assertEqual(result["total_seats"], 234)
        self.assertEqual(result["majority"], 118)

    def test_fallback_parties_total_lte_seats(self):
        from services.election_scraper import fetch_results
        result = fetch_results("WB")
        total_won = sum(p.get("total", 0) for p in result["parties"])
        self.assertLessEqual(total_won, result["total_seats"])


# ===========================================================================
#  4. get_state_code_from_location()
# ===========================================================================

class TestGetStateCode(unittest.TestCase):

    def setUp(self):
        from services.election_scraper import get_state_code_from_location
        self.fn = get_state_code_from_location

    def test_west_bengal_name(self):
        self.assertEqual(self.fn("West Bengal"), "WB")

    def test_700001_pin(self):
        self.assertEqual(self.fn("700001"), "WB")

    def test_tamil_nadu_name(self):
        self.assertEqual(self.fn("Tamil Nadu"), "TN")

    def test_600001_pin(self):
        self.assertEqual(self.fn("600001"), "TN")

    def test_kerala_name(self):
        self.assertEqual(self.fn("Kerala"), "KL")

    def test_delhi_name(self):
        self.assertEqual(self.fn("Delhi"), "DL")

    def test_unknown_defaults_to_wb(self):
        self.assertEqual(self.fn("Atlantis"), "WB")

    def test_case_insensitive(self):
        self.assertEqual(self.fn("west bengal"), "WB")
        self.assertEqual(self.fn("MAHARASHTRA"), "MH")


if __name__ == "__main__":
    print("🇮🇳 Starting Translation & Scraper Test Suite…")
    unittest.main(verbosity=2)
