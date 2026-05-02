"""
CivicPulse — Language Selector
================================
Uses the free Google Translate endpoint (no API key required).
Same endpoint browsers use — works on HuggingFace Spaces, GitHub Actions, etc.

Usage:
    from components.language_selector import T
    st.markdown(T("Hello voter"))
"""

from __future__ import annotations
import json
import logging
import urllib.request
import urllib.parse
import streamlit as st

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES: dict[str, str] = {
    "English":           "en",
    "हिंदी (Hindi)":    "hi",
    "বাংলা (Bengali)":  "bn",
    "தமிழ் (Tamil)":    "ta",
}

_LANG_CODES = {v: k for k, v in SUPPORTED_LANGUAGES.items()}
_CACHE_KEY  = "_translate_cache"


def _get_cache() -> dict:
    if _CACHE_KEY not in st.session_state:
        st.session_state[_CACHE_KEY] = {}
    return st.session_state[_CACHE_KEY]


def translate_text(text: str, target_lang: str) -> str:
    """
    Translate text using the free Google Translate gtx endpoint.
    No API key needed. Results cached in session_state.
    Logs warnings on failure — never silently swallows errors.
    """
    if target_lang == "en" or not text or not text.strip():
        return text

    cache     = _get_cache()
    cache_key = (text, target_lang)
    if cache_key in cache:
        return cache[cache_key]

    try:
        params = urllib.parse.urlencode({
            "client": "gtx",
            "sl":     "en",
            "tl":     target_lang,
            "dt":     "t",
            "q":      text,
        })
        url = f"https://translate.googleapis.com/translate_a/single?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())

        translated = "".join(item[0] for item in data[0] if item[0])
        cache[cache_key] = translated
        return translated

    except urllib.error.URLError as exc:
        logger.warning("translate_text network error (lang=%s): %s", target_lang, exc)
        return text
    except (KeyError, IndexError, ValueError) as exc:
        logger.warning("translate_text parse error (lang=%s): %s", target_lang, exc)
        return text
    except Exception as exc:
        logger.warning("translate_text unexpected error (lang=%s): %s", target_lang, exc)
        return text


def get_current_language() -> str:
    """Return BCP-47 code from session_state, defaulting to 'en'."""
    return st.session_state.get("language", "en")


def render_translated(text: str) -> str:
    """Translate text into the active UI language."""
    return translate_text(text, get_current_language())


# Short alias — the only symbol most components need
T = render_translated


def render_language_selector() -> None:
    """
    Render a compact language-picker widget.
    Stores chosen language in st.session_state['language'] and reruns.
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
        help="Select your preferred language / अपनी भाषा चुनें",
    )
    chosen_code = SUPPORTED_LANGUAGES[chosen_name]

    if chosen_code != current_code:
        st.session_state[_CACHE_KEY] = {}   # clear cache on language change
        st.session_state["language"] = chosen_code
        st.rerun()

    if chosen_code != "en":
        st.markdown(
            f'<div style="font-size:0.65rem;color:#27C96E;font-weight:700;margin-top:2px;"'
            f' aria-live="polite" aria-label="Language active: {chosen_name}">'
            f'🌐 {chosen_name} active</div>',
            unsafe_allow_html=True,
        )
