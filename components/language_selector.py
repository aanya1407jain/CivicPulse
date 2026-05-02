"""
CivicPulse — Language Selector
================================
Uses the free Google Translate endpoint (no API key required).
Batches multiple strings into a single API call for efficiency.
Results cached in session_state — cleared on language change.
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
_BATCH_KEY  = "_translate_batch_queue"


def _get_cache() -> dict:
    if _CACHE_KEY not in st.session_state:
        st.session_state[_CACHE_KEY] = {}
    return st.session_state[_CACHE_KEY]


def translate_text(text: str, target_lang: str) -> str:
    """
    Translate a single string using the free Google Translate gtx endpoint.
    No API key needed. Results cached in session_state.
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


def translate_batch(texts: list[str], target_lang: str) -> list[str]:
    """
    Translate multiple strings in a single HTTP request — far more efficient
    than calling translate_text() in a loop.
    Falls back to individual calls on any error.
    """
    if target_lang == "en" or not texts:
        return texts

    cache      = _get_cache()
    results    = [""] * len(texts)
    uncached   = []   # (original_index, text)

    for i, text in enumerate(texts):
        if not text or not text.strip():
            results[i] = text
            continue
        key = (text, target_lang)
        if key in cache:
            results[i] = cache[key]
        else:
            uncached.append((i, text))

    if not uncached:
        return results

    # Build a single request with multiple q= params
    try:
        base = (
            f"https://translate.googleapis.com/translate_a/single"
            f"?client=gtx&sl=en&tl={target_lang}&dt=t"
        )
        for _, text in uncached:
            base += "&q=" + urllib.parse.quote(text, safe="")

        req = urllib.request.Request(base, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw  = resp.read()
            data = json.loads(raw)

        # gtx returns nested list — flatten all translation segments
        all_translated = [
            "".join(seg[0] for seg in block if seg[0])
            for block in data[0]
            if isinstance(block, list)
        ]

        for batch_i, (orig_i, text) in enumerate(uncached):
            translated = all_translated[batch_i] if batch_i < len(all_translated) else text
            cache[(text, target_lang)] = translated
            results[orig_i] = translated

    except Exception as exc:
        logger.warning("translate_batch failed (lang=%s): %s — falling back", target_lang, exc)
        for orig_i, text in uncached:
            results[orig_i] = translate_text(text, target_lang)

    return results


def get_current_language() -> str:
    """Return BCP-47 code from session_state, defaulting to 'en'."""
    return st.session_state.get("language", "en")


def render_translated(text: str) -> str:
    """Translate text into the active UI language."""
    return translate_text(text, get_current_language())


# Short alias — the only symbol most components need
T = render_translated


def render_language_selector() -> None:
    """Compact language-picker widget."""
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
        st.session_state[_CACHE_KEY] = {}
        st.session_state["language"] = chosen_code
        st.rerun()

    if chosen_code != "en":
        st.markdown(
            f'<div style="font-size:0.65rem;color:#27C96E;font-weight:700;margin-top:2px;"'
            f' aria-live="polite" aria-label="Language active: {chosen_name}">'
            f'🌐 {chosen_name} active</div>',
            unsafe_allow_html=True,
        )
