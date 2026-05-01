"""
CivicPulse — Google Translate Language Selector
================================================
Wires the Google Translate API Key from settings to a language picker
(Hindi / Bengali / Tamil / English) so the app serves non-English voters.

Usage
-----
Call render_language_selector() anywhere in the UI.
The component stores the chosen language code in st.session_state["language"]
and injects the Google Translate element script when a non-English language
is selected, OR activates the Translate API directly if the key is available.
"""

from __future__ import annotations
import streamlit as st
from config.settings import GOOGLE_TRANSLATE_API_KEY

# Supported languages: display name → BCP-47 code
SUPPORTED_LANGUAGES: dict[str, str] = {
    "English":  "en",
    "हिंदी (Hindi)":   "hi",
    "বাংলা (Bengali)": "bn",
    "தமிழ் (Tamil)":   "ta",
}

_LANG_CODES = {v: k for k, v in SUPPORTED_LANGUAGES.items()}


def translate_text(text: str, target_lang: str) -> str:
    """
    Translate *text* to *target_lang* using the Google Cloud Translate v2 REST API.
    Returns the original text on any failure (graceful degradation).

    Parameters
    ----------
    text        : Source text (assumed English).
    target_lang : BCP-47 language code, e.g. "hi", "bn", "ta".
    """
    if not GOOGLE_TRANSLATE_API_KEY or target_lang == "en" or not text:
        return text

    try:
        import urllib.request
        import urllib.parse
        import json

        url = (
            "https://translation.googleapis.com/language/translate/v2"
            f"?key={GOOGLE_TRANSLATE_API_KEY}"
        )
        payload = json.dumps({
            "q":      text,
            "source": "en",
            "target": target_lang,
            "format": "text",
        }).encode("utf-8")

        req  = urllib.request.Request(url, data=payload,
                                      headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        return data["data"]["translations"][0]["translatedText"]

    except Exception:
        return text  # always fall back gracefully


def get_current_language() -> str:
    """Return the BCP-47 code stored in session_state, defaulting to 'en'."""
    return st.session_state.get("language", "en")


def render_language_selector() -> None:
    """
    Render a compact language selector that:
    1. Stores the chosen language in st.session_state["language"].
    2. If a non-English language is selected AND no API key is set,
       injects the Google Translate element widget as a fallback.
    3. Shows a ✅ confirmation badge for active non-English mode.
    """
    lang_names = list(SUPPORTED_LANGUAGES.keys())
    current_code = get_current_language()
    # Reverse-map code → display name
    current_name = _LANG_CODES.get(current_code, "English")
    try:
        current_idx = lang_names.index(current_name)
    except ValueError:
        current_idx = 0

    chosen_name = st.selectbox(
        "🌐 Language",
        lang_names,
        index=current_idx,
        key="lang_selector",
        label_visibility="collapsed",
        help="Select your preferred language",
    )
    chosen_code = SUPPORTED_LANGUAGES[chosen_name]

    if chosen_code != current_code:
        st.session_state["language"] = chosen_code
        st.rerun()

    # ── Non-English feedback ──────────────────────────────────────────────────
    if chosen_code != "en":
        if GOOGLE_TRANSLATE_API_KEY:
            st.markdown(
                f'<div style="font-size:0.65rem;color:#27C96E;font-weight:700;'
                f'margin-top:2px;">🌐 {chosen_name} active</div>',
                unsafe_allow_html=True,
            )
        else:
            # Inject Google Translate element as zero-cost fallback
            _inject_google_translate_element(chosen_code)
            st.markdown(
                '<div style="font-size:0.62rem;color:#FF6B1A;font-weight:600;'
                'margin-top:2px;">Add GOOGLE_TRANSLATE_API_KEY for full translation</div>',
                unsafe_allow_html=True,
            )


def render_translated(text: str) -> str:
    """
    Convenience helper: translate *text* using the active session language.
    Returns translated string (or original if language is English / API unavailable).
    """
    lang = get_current_language()
    return translate_text(text, lang)


def _inject_google_translate_element(target_lang: str) -> None:
    """
    Inject the Google Translate Element widget (free, no API key needed).
    Falls back gracefully to in-page translation via the public JS widget.
    """
    html = f"""
    <div id="google_translate_element" style="display:none;"></div>
    <script type="text/javascript">
    function googleTranslateElementInit() {{
        new google.translate.TranslateElement({{
            pageLanguage: 'en',
            includedLanguages: 'hi,bn,ta,en',
            layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
            autoDisplay: true,
        }}, 'google_translate_element');
        // Auto-select the target language
        setTimeout(function() {{
            var sel = document.querySelector('.goog-te-combo');
            if (sel) {{
                sel.value = '{target_lang}';
                sel.dispatchEvent(new Event('change'));
            }}
        }}, 800);
    }}
    </script>
    <script type="text/javascript"
        src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit">
    </script>
    """
    st.markdown(html, unsafe_allow_html=True)
