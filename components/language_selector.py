"""
CivicPulse — Google Translate Language Selector
================================================
Wires the Google Translate API Key from settings to a language picker
(Hindi / Bengali / Tamil / English) so the app serves non-English voters.

FIX: API key is read via os.getenv() at call-time (not module import time)
so that secrets injected by HuggingFace Spaces / GitHub Actions are always
picked up, regardless of import order.

Usage
-----
    from components.language_selector import T
    st.markdown(T("Hello voter"))
"""

from __future__ import annotations
import os
import json
import urllib.request
import streamlit as st

# Supported languages: display name → BCP-47 code
SUPPORTED_LANGUAGES: dict[str, str] = {
    "English":           "en",
    "हिंदी (Hindi)":    "hi",
    "বাংলা (Bengali)":  "bn",
    "தமிழ் (Tamil)":    "ta",
}

_LANG_CODES = {v: k for k, v in SUPPORTED_LANGUAGES.items()}

# Session-state cache key
_CACHE_KEY = "_translate_cache"


def _api_key() -> str:
    """Read the API key fresh from the environment on every call.
    This ensures HuggingFace / GitHub secrets are always visible,
    even if settings.py was imported before the env was populated."""
    return os.getenv("GOOGLE_TRANSLATE_API_KEY", "").strip()


def _get_cache() -> dict:
    if _CACHE_KEY not in st.session_state:
        st.session_state[_CACHE_KEY] = {}
    return st.session_state[_CACHE_KEY]


def translate_text(text: str, target_lang: str) -> str:
    """
    Translate *text* to *target_lang* using Google Cloud Translate v2 REST.
    Caches results in session_state to avoid redundant API calls.
    Falls back to original text on any error.
    """
    key = _api_key()

    if not key or target_lang == "en" or not text or not text.strip():
        return text

    cache = _get_cache()
    cache_key = (text, target_lang)
    if cache_key in cache:
        return cache[cache_key]

    try:
        url = (
            "https://translation.googleapis.com/language/translate/v2"
            f"?key={key}"
        )
        payload = json.dumps({
            "q":      text,
            "source": "en",
            "target": target_lang,
            "format": "text",
        }).encode("utf-8")

        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())

        translated = data["data"]["translations"][0]["translatedText"]
        cache[cache_key] = translated
        return translated

    except Exception as exc:
        # Log so developers can see what's going wrong
        import logging
        logging.getLogger(__name__).warning("translate_text failed: %s", exc)
        return text  # always degrade gracefully


def get_current_language() -> str:
    """Return the BCP-47 code stored in session_state, defaulting to 'en'."""
    return st.session_state.get("language", "en")


def render_translated(text: str) -> str:
    """Translate *text* into the active UI language."""
    return translate_text(text, get_current_language())


# Short alias — the only symbol most components need
T = render_translated


def render_language_selector() -> None:
    """
    Render a compact language-picker widget.
    Stores chosen language in st.session_state["language"] and reruns.
    """
    lang_names   = list(SUPPORTED_LANGUAGES.keys())
    current_code = get_current_language()
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
        # Clear translation cache so new language is fetched fresh
        st.session_state[_CACHE_KEY] = {}
        st.session_state["language"] = chosen_code
        st.rerun()

    # Status badge
    if chosen_code != "en":
        if _api_key():
            st.markdown(
                f'<div style="font-size:0.65rem;color:#27C96E;font-weight:700;'
                f'margin-top:2px;">🌐 {chosen_name} active</div>',
                unsafe_allow_html=True,
            )
        else:
            _inject_google_translate_element(chosen_code)
            st.markdown(
                '<div style="font-size:0.62rem;color:#FF6B1A;font-weight:600;'
                'margin-top:2px;">Add GOOGLE_TRANSLATE_API_KEY for full translation</div>',
                unsafe_allow_html=True,
            )


def _inject_google_translate_element(target_lang: str) -> None:
    """Fallback: free Google Translate widget (no API key required)."""
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
