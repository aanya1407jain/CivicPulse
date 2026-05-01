"""
CivicPulse — Test Suite: UI Components
=======================================
Covers render_election_quiz(), render_checklist(), render_india_map().

All Streamlit calls are patched so tests run without a running Streamlit server.
"""

from __future__ import annotations

import sys
import os
import unittest
from unittest.mock import MagicMock, patch, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# Shared Streamlit mock — patch before any component import touches it
# ---------------------------------------------------------------------------

def _make_ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=ctx)
    ctx.__exit__ = MagicMock(return_value=False)
    return ctx


def _make_st_mock() -> MagicMock:
    """Return a MagicMock that satisfies common st.* usage patterns."""
    st = MagicMock()
    st.session_state = {}

    def _columns(spec):
        """Return exactly as many ctx mocks as columns requested."""
        n = len(spec) if hasattr(spec, '__len__') else int(spec)
        return [_make_ctx() for _ in range(n)]

    st.columns.side_effect = _columns
    st.tabs.return_value   = [_make_ctx()] * 12
    return st


# ===========================================================================
#  1. render_election_quiz()
# ===========================================================================

class TestElectionQuizData(unittest.TestCase):
    """Pure-Python tests on QUIZ_QUESTIONS — no Streamlit needed."""

    def setUp(self):
        from components.election_quiz import QUIZ_QUESTIONS, CATEGORY_COLORS
        self.questions     = QUIZ_QUESTIONS
        self.cat_colors    = CATEGORY_COLORS

    # ── data integrity ──────────────────────────────────────────────────────

    def test_at_least_ten_questions(self):
        self.assertGreaterEqual(len(self.questions), 10)

    def test_every_question_has_required_keys(self):
        required = {"q", "options", "answer", "explanation", "category"}
        for q in self.questions:
            self.assertTrue(required.issubset(q.keys()),
                            f"Missing keys in question: {q.get('q', '?')}")

    def test_every_answer_is_among_options(self):
        for q in self.questions:
            self.assertIn(q["answer"], q["options"],
                          f"Correct answer not in options for: {q['q']}")

    def test_each_question_has_four_options(self):
        for q in self.questions:
            self.assertEqual(len(q["options"]), 4,
                             f"Expected 4 options for: {q['q']}")

    def test_all_categories_have_a_color(self):
        for q in self.questions:
            self.assertIn(q["category"], self.cat_colors,
                          f"No color mapping for category: {q['category']}")

    def test_no_duplicate_questions(self):
        texts = [q["q"] for q in self.questions]
        self.assertEqual(len(texts), len(set(texts)), "Duplicate question text found")

    # ── known factual answers ───────────────────────────────────────────────

    def test_voting_age_answer(self):
        q = next(q for q in self.questions if "minimum age" in q["q"].lower())
        self.assertEqual(q["answer"], "18 years")

    def test_nota_answer(self):
        q = next(q for q in self.questions if "NOTA" in q["q"])
        self.assertEqual(q["answer"], "None Of The Above")

    def test_epic_answer(self):
        q = next(q for q in self.questions if "EPIC" in q["q"])
        self.assertEqual(q["answer"], "Electoral Photo Identity Card")

    def test_article_324_answer(self):
        q = next(q for q in self.questions
                 if "Election Commission" in q["q"] and "article" in q["q"].lower())
        self.assertEqual(q["answer"], "Article 324")

    def test_helpline_answer(self):
        q = next(q for q in self.questions if "helpline" in q["q"].lower())
        self.assertEqual(q["answer"], "1950")


class TestResetQuiz(unittest.TestCase):
    """Tests for _reset_quiz() session-state mutation."""

    def setUp(self):
        self._st_patcher = patch("components.election_quiz.st", _make_st_mock())
        self.mock_st = self._st_patcher.start()
        self.mock_st.session_state = {}  # fresh state
        from components.election_quiz import _reset_quiz, QUIZ_QUESTIONS
        self._reset_quiz   = _reset_quiz
        self._num_questions = len(QUIZ_QUESTIONS)

    def tearDown(self):
        self._st_patcher.stop()

    def test_reset_initializes_started_true(self):
        self._reset_quiz()
        self.assertTrue(self.mock_st.session_state["quiz_started"])

    def test_reset_done_is_false(self):
        self._reset_quiz()
        self.assertFalse(self.mock_st.session_state["quiz_done"])

    def test_reset_score_is_zero(self):
        self._reset_quiz()
        self.assertEqual(self.mock_st.session_state["quiz_score"], 0)

    def test_reset_picks_seven_questions(self):
        self._reset_quiz()
        self.assertEqual(len(self.mock_st.session_state["quiz_indices"]), 7)

    def test_reset_indices_are_valid(self):
        self._reset_quiz()
        for idx in self.mock_st.session_state["quiz_indices"]:
            self.assertGreaterEqual(idx, 0)
            self.assertLess(idx, self._num_questions)

    def test_reset_indices_are_unique(self):
        self._reset_quiz()
        idxs = self.mock_st.session_state["quiz_indices"]
        self.assertEqual(len(idxs), len(set(idxs)))

    def test_reset_clears_answers(self):
        self.mock_st.session_state["quiz_answers"] = {0: "old answer"}
        self._reset_quiz()
        self.assertEqual(self.mock_st.session_state["quiz_answers"], {})

    def test_reset_sets_current_to_zero(self):
        self.mock_st.session_state["quiz_current"] = 5
        self._reset_quiz()
        self.assertEqual(self.mock_st.session_state["quiz_current"], 0)


class TestRenderElectionQuiz(unittest.TestCase):
    """Smoke-tests for render_election_quiz() UI paths."""

    def _make_st(self, session_overrides=None):
        st = _make_st_mock()
        st.session_state = {
            "quiz_started": False,
            "quiz_done":    False,
        }
        if session_overrides:
            st.session_state.update(session_overrides)
        return st

    def test_welcome_screen_calls_button(self):
        st = self._make_st()
        with patch("components.election_quiz.st", st):
            from components import election_quiz
            election_quiz.render_election_quiz()
        st.button.assert_called()

    def test_started_active_quiz_shows_progress(self):
        st = self._make_st({
            "quiz_started":  True,
            "quiz_done":     False,
            "quiz_indices":  [0, 1, 2, 3, 4, 5, 6],
            "quiz_current":  0,
            "quiz_score":    0,
            "quiz_answers":  {},
        })
        with patch("components.election_quiz.st", st):
            from components import election_quiz
            election_quiz.render_election_quiz()
        st.progress.assert_called()

    def test_done_screen_shows_divider(self):
        st = self._make_st({
            "quiz_started":  True,
            "quiz_done":     True,
            "quiz_indices":  [0, 1, 2, 3, 4, 5, 6],
            "quiz_score":    5,
            "quiz_answers":  {i: "18 years" for i in range(7)},
        })
        with patch("components.election_quiz.st", st):
            from components import election_quiz
            election_quiz.render_election_quiz()
        st.divider.assert_called()


# ===========================================================================
#  2. render_checklist()
# ===========================================================================

class TestRenderChecklist(unittest.TestCase):
    """Tests for render_checklist() — covers step grouping and progress bar."""

    def _make_handler(self):
        from regions.base import ElectionStep, BaseRegionHandler

        class MockHandler(BaseRegionHandler):
            country_code = "IN"
            country_name = "India"
            flag = "🇮🇳"

            def get_election_data(self, location):
                return {}

            def get_checklist_steps(self):
                return [
                    ElectionStep("s1", "Verify Name",    "IN", "Check roll",    priority="urgent",   deadline="2026-04-01"),
                    ElectionStep("s2", "Carry Voter ID", "IN", "Bring EPIC",    priority="normal",   deadline="2026-04-17"),
                    ElectionStep("s3", "Know Candidate", "IN", "Read manifesto",priority="optional", deadline=""),
                ]

            def get_registration_url(self, location):
                return "https://voters.eci.gov.in/"

            def get_local_rules(self, jurisdiction):
                return []

        return MockHandler()

    def _election_data(self):
        return {
            "election_name":      "West Bengal Assembly 2026",
            "registration_url":   "https://voters.eci.gov.in/",
        }

    def _run(self, session_overrides=None):
        st = _make_st_mock()
        st.session_state = session_overrides or {}
        with patch("components.checklist.st", st):
            from components import checklist
            checklist.render_checklist(self._make_handler(), self._election_data())
        return st

    def test_progress_bar_is_shown(self):
        st = self._run()
        st.progress.assert_called()

    def test_progress_when_all_steps_checked(self):
        st = self._run({"checklist": {"s1": True, "s2": True, "s3": True}})
        # progress should be called with 1.0
        call_args = [c.args[0] for c in st.progress.call_args_list]
        self.assertIn(1.0, call_args)

    def test_progress_when_no_steps_checked(self):
        st = self._run({"checklist": {}})
        call_args = [c.args[0] for c in st.progress.call_args_list]
        self.assertIn(0.0, call_args)

    def test_link_button_voter_portal(self):
        st = self._run()
        urls = [c.args[1] if len(c.args) > 1 else c.kwargs.get("url", "")
                for c in st.link_button.call_args_list]
        self.assertTrue(
            any("eci.gov.in" in str(u) or "voters.eci" in str(u) for u in urls),
            "Expected ECI portal link not rendered",
        )

    def test_markdown_mentions_election_name(self):
        st = self._run()
        all_md = " ".join(
            str(c.args[0]) for c in st.markdown.call_args_list if c.args
        )
        self.assertIn("West Bengal", all_md)

    def test_checklist_session_state_initialized(self):
        st = _make_st_mock()
        st.session_state = {}  # empty
        with patch("components.checklist.st", st):
            from components import checklist
            checklist.render_checklist(self._make_handler(), self._election_data())
        self.assertIn("checklist", st.session_state)

    def test_divider_rendered(self):
        st = self._run()
        st.divider.assert_called()


class TestRenderStep(unittest.TestCase):
    """Unit tests for _render_step() internal helper."""

    def _make_step(self, priority="urgent", deadline="2026-04-01", url="https://eci.gov.in/"):
        from regions.base import ElectionStep
        return ElectionStep(
            id="test_step",
            title="Test Step",
            jurisdiction="IN",
            description="Do something important.",
            url=url,
            deadline=deadline,
            priority=priority,
        )

    def test_urgent_step_renders_without_exception(self):
        st = _make_st_mock()
        st.session_state = {"checklist": {}}
        with patch("components.checklist.st", st):
            from components.checklist import _render_step
            from services.calendar_service import CalendarService
            _render_step(self._make_step(priority="urgent"), CalendarService())
        # No exception = pass

    def test_optional_step_no_calendar_link(self):
        """Optional steps without a deadline should not call link_button for calendar."""
        st = _make_st_mock()
        st.session_state = {"checklist": {}}
        with patch("components.checklist.st", st):
            from components.checklist import _render_step
            from services.calendar_service import CalendarService
            _render_step(self._make_step(priority="optional", deadline=""), CalendarService())
        # link_button may be called for the ECI portal URL, but not for calendar
        gcal_calls = [
            c for c in st.link_button.call_args_list
            if "calendar.google.com" in str(c)
        ]
        self.assertEqual(len(gcal_calls), 0)

    def test_checked_step_shows_done_icon(self):
        st = _make_st_mock()
        st.session_state = {"checklist": {"test_step": True}}
        with patch("components.checklist.st", st):
            from components.checklist import _render_step
            from services.calendar_service import CalendarService
            _render_step(self._make_step(), CalendarService())
        all_md = " ".join(str(c.args[0]) for c in st.markdown.call_args_list if c.args)
        self.assertIn("✅", all_md)


# ===========================================================================
#  3. render_india_map()
# ===========================================================================

class TestAllIndiaData(unittest.TestCase):
    """Data-integrity tests on ALL_INDIA_DATA — no Streamlit needed."""

    def setUp(self):
        from components.india_map import ALL_INDIA_DATA, STATUS_COLORS, STATUS_LABELS, REGIONS
        self.data          = ALL_INDIA_DATA
        self.status_colors = STATUS_COLORS
        self.status_labels = STATUS_LABELS
        self.regions       = REGIONS

    def test_at_least_28_states(self):
        states = [v for v in self.data.values() if v["type"] == "State"]
        self.assertGreaterEqual(len(states), 28)

    def test_all_entries_have_required_fields(self):
        required = {"type", "region", "ruling_party", "ruling_color",
                    "total_seats", "status", "capital"}
        for name, d in self.data.items():
            self.assertTrue(required.issubset(d.keys()),
                            f"Missing fields for: {name}")

    def test_all_status_values_have_color(self):
        for name, d in self.data.items():
            self.assertIn(d["status"], self.status_colors,
                          f"Unknown status '{d['status']}' for {name}")

    def test_all_status_values_have_label(self):
        for name, d in self.data.items():
            self.assertIn(d["status"], self.status_labels,
                          f"No label for status '{d['status']}' for {name}")

    def test_states_with_assembly_have_nonzero_seats(self):
        for name, d in self.data.items():
            if d["status"] != "no_assembly":
                self.assertGreater(d["total_seats"], 0,
                                   f"{name} should have >0 seats")

    def test_no_assembly_uts_have_zero_seats(self):
        for name, d in self.data.items():
            if d["status"] == "no_assembly":
                self.assertEqual(d["total_seats"], 0,
                                 f"{name} has no assembly but non-zero seats")

    def test_wb_data_correctness(self):
        wb = self.data["West Bengal"]
        self.assertEqual(wb["total_seats"], 294)
        self.assertEqual(wb["ruling_party"], "AITC")
        self.assertEqual(wb["status"], "completed")
        self.assertEqual(wb["capital"], "Kolkata")

    def test_ruling_colors_are_valid_hex(self):
        import re
        hex_re = re.compile(r"^#[0-9A-Fa-f]{6}$")
        for name, d in self.data.items():
            self.assertTrue(hex_re.match(d["ruling_color"]),
                            f"Invalid hex color for {name}: {d['ruling_color']}")

    def test_all_regions_match_regions_list(self):
        for name, d in self.data.items():
            self.assertIn(d["region"], self.regions,
                          f"Unknown region '{d['region']}' for {name}")

    def test_regions_list_starts_with_all_regions(self):
        self.assertEqual(self.regions[0], "All Regions")


class TestRenderIndiaMap(unittest.TestCase):
    """Smoke-tests for render_india_map() Streamlit output."""

    def _run(self, search="", region="All Regions", status="All", state_select="— Select to view details —"):
        st = _make_st_mock()
        st.session_state = {}
        st.text_input.return_value  = search
        st.selectbox.side_effect    = [region, status, state_select]
        with patch("components.india_map.st", st):
            from components import india_map
            india_map.render_india_map()
        return st

    def test_renders_four_metrics(self):
        st = self._run()
        self.assertEqual(st.metric.call_count, 4)

    def test_renders_divider(self):
        st = self._run()
        st.divider.assert_called()

    def test_renders_column_cards(self):
        st = self._run()
        st.markdown.assert_called()

    def test_link_button_to_eci(self):
        st = self._run()
        urls = [str(c) for c in st.link_button.call_args_list]
        self.assertTrue(any("eci.gov.in" in u for u in urls))

    def test_state_card_shown_when_state_selected(self):
        st = _make_st_mock()
        st.session_state = {}
        st.text_input.return_value  = ""
        # selectbox side_effect: region, status, state_select
        st.selectbox.side_effect    = ["All Regions", "All", "West Bengal"]
        with patch("components.india_map.st", st):
            from components import india_map
            india_map.render_india_map()
        # _state_info_card emits markdown with state name
        all_md = " ".join(str(c.args[0]) for c in st.markdown.call_args_list if c.args)
        self.assertIn("West Bengal", all_md)

    def test_search_filter_reduces_cards(self):
        """Searching for 'West Bengal' should render fewer cards than no filter."""
        # Count markdown calls with 'card' content for no filter
        st_all = self._run()
        calls_all = st_all.markdown.call_count

        # Now search for one specific state
        st_filtered = self._run(search="West Bengal")
        calls_filtered = st_filtered.markdown.call_count

        self.assertLessEqual(calls_filtered, calls_all)


class TestStateInfoCard(unittest.TestCase):
    """Unit tests for _state_info_card() internal helper."""

    def _run_card(self, state_name):
        st = _make_st_mock()
        with patch("components.india_map.st", st):
            from components.india_map import _state_info_card
            _state_info_card(state_name)
        return st

    def test_known_state_renders_markdown(self):
        st = self._run_card("Kerala")
        st.markdown.assert_called()

    def test_unknown_state_shows_warning(self):
        st = self._run_card("Neverland")
        st.warning.assert_called()

    def test_no_assembly_ut_skips_seat_grid(self):
        st = self._run_card("Ladakh")
        all_md = " ".join(str(c.args[0]) for c in st.markdown.call_args_list if c.args)
        # Should mention 'No Assembly' or 'Lt. Governor'
        self.assertTrue(
            "No Assembly" in all_md or "Lt. Governor" in all_md or "no_assembly" in all_md
        )

    def test_state_card_contains_capital(self):
        st = self._run_card("Tamil Nadu")
        all_md = " ".join(str(c.args[0]) for c in st.markdown.call_args_list if c.args)
        self.assertIn("Chennai", all_md)


if __name__ == "__main__":
    unittest.main()
