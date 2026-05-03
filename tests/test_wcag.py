"""
CivicPulse — Test Suite: WCAG Contrast Checker
===============================================
Tests the _relative_luminance, _contrast_ratio, and run_wcag_contrast_audit
functions in components/theme.py.
"""

from __future__ import annotations
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestRelativeLuminance(unittest.TestCase):

    def test_black_is_zero(self) -> None:
        from components.theme import _relative_luminance
        self.assertAlmostEqual(_relative_luminance("#000000"), 0.0, places=5)

    def test_white_is_one(self) -> None:
        from components.theme import _relative_luminance
        self.assertAlmostEqual(_relative_luminance("#FFFFFF"), 1.0, places=5)

    def test_mid_grey(self) -> None:
        from components.theme import _relative_luminance
        # #808080 → approximately 0.216
        val = _relative_luminance("#808080")
        self.assertGreater(val, 0.1)
        self.assertLess(val, 0.3)

    def test_shorthand_hex(self) -> None:
        from components.theme import _relative_luminance
        # #FFF should equal #FFFFFF
        self.assertAlmostEqual(
            _relative_luminance("#FFF"),
            _relative_luminance("#FFFFFF"),
            places=5,
        )

    def test_pure_red(self) -> None:
        from components.theme import _relative_luminance
        val = _relative_luminance("#FF0000")
        self.assertAlmostEqual(val, 0.2126, places=3)

    def test_pure_green(self) -> None:
        from components.theme import _relative_luminance
        val = _relative_luminance("#00FF00")
        self.assertAlmostEqual(val, 0.7152, places=3)

    def test_pure_blue(self) -> None:
        from components.theme import _relative_luminance
        val = _relative_luminance("#0000FF")
        self.assertAlmostEqual(val, 0.0722, places=3)


class TestContrastRatio(unittest.TestCase):

    def test_black_on_white_is_21(self) -> None:
        from components.theme import _contrast_ratio
        ratio = _contrast_ratio("#000000", "#FFFFFF")
        self.assertAlmostEqual(ratio, 21.0, places=1)

    def test_white_on_black_is_21(self) -> None:
        from components.theme import _contrast_ratio
        # Symmetric
        self.assertAlmostEqual(
            _contrast_ratio("#FFFFFF", "#000000"),
            _contrast_ratio("#000000", "#FFFFFF"),
            places=5,
        )

    def test_same_color_is_1(self) -> None:
        from components.theme import _contrast_ratio
        self.assertAlmostEqual(_contrast_ratio("#AABBCC", "#AABBCC"), 1.0, places=5)

    def test_orange_on_dark_exceeds_3(self) -> None:
        from components.theme import _contrast_ratio
        # #FF6B1A (orange) on #0D0F14 (dark bg) — large text must be ≥ 3:1
        ratio = _contrast_ratio("#FF6B1A", "#0D0F14")
        self.assertGreater(ratio, 3.0)

    def test_white_on_orange_button_exceeds_4_5(self) -> None:
        from components.theme import _contrast_ratio
        # White text on orange button must pass normal text threshold
        ratio = _contrast_ratio("#FFFFFF", "#FF6B1A")
        self.assertGreater(ratio, 4.5)

    def test_primary_text_on_bg_exceeds_7(self) -> None:
        from components.theme import _contrast_ratio
        # #E8EAF0 on #0D0F14 — should be well above AA
        ratio = _contrast_ratio("#E8EAF0", "#0D0F14")
        self.assertGreater(ratio, 7.0)


class TestWcagAudit(unittest.TestCase):

    def test_audit_returns_dict(self) -> None:
        from components.theme import run_wcag_contrast_audit
        result = run_wcag_contrast_audit()
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)

    def test_audit_keys_are_strings(self) -> None:
        from components.theme import run_wcag_contrast_audit
        result = run_wcag_contrast_audit()
        for k in result:
            self.assertIsInstance(k, str)

    def test_audit_values_are_floats(self) -> None:
        from components.theme import run_wcag_contrast_audit
        result = run_wcag_contrast_audit()
        for v in result.values():
            self.assertIsInstance(v, float)
            self.assertGreater(v, 1.0)   # ratio is always > 1

    def test_primary_text_pair_present(self) -> None:
        from components.theme import run_wcag_contrast_audit
        result = run_wcag_contrast_audit()
        self.assertIn("text on bg", result)

    def test_white_on_orange_passes_aa(self) -> None:
        from components.theme import run_wcag_contrast_audit
        result = run_wcag_contrast_audit()
        self.assertGreater(result["white on orange btn"], 4.5)

    def test_primary_text_passes_aaa(self) -> None:
        from components.theme import run_wcag_contrast_audit
        result = run_wcag_contrast_audit()
        # Primary text should clear AAA (7:1)
        self.assertGreater(result["text on bg"], 7.0)

    def test_all_critical_pairs_pass_aa(self) -> None:
        """Strict AA check: no critical pair should be below 3:1."""
        from components.theme import run_wcag_contrast_audit
        result = run_wcag_contrast_audit()
        # Every pair returned should at minimum clear 3:1 (large text threshold)
        critical = [k for k in result if "text3" not in k]  # text3 is intentional low-contrast
        for label in critical:
            self.assertGreater(
                result[label], 3.0,
                msg=f"Contrast too low for '{label}': {result[label]:.2f}:1"
            )

    def test_audit_does_not_raise(self) -> None:
        from components.theme import run_wcag_contrast_audit
        try:
            run_wcag_contrast_audit()
        except Exception as exc:
            self.fail(f"run_wcag_contrast_audit() raised unexpectedly: {exc}")

    def test_module_import_runs_audit(self) -> None:
        """_WCAG_RESULTS is populated at import time."""
        from components.theme import _WCAG_RESULTS
        self.assertIsInstance(_WCAG_RESULTS, dict)
        self.assertGreater(len(_WCAG_RESULTS), 5)


if __name__ == "__main__":
    print("🎨 Running WCAG Contrast Checker Tests…")
    unittest.main(verbosity=2)
