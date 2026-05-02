"""
CivicPulse — Language Selector
================================
Priority 1: Official Google Cloud Translation API (when GOOGLE_TRANSLATE_API_KEY is set).
Priority 2: Free Google Translate gtx endpoint (no key required) — fallback.
Results cached in session_state — cleared on language change.

Security:
- Per-session call counter limits translation requests (RATE_LIMIT in settings).
- Injects lang= and dir= attributes for WCAG 3.1.1 compliance on language switch.
"""

from __future__ import annotations
import json
import logging
import urllib.request
import urllib.parse
import streamlit as st

from config.settings import GOOGLE_TRANSLATE_API_KEY, RATE_LIMIT

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES: dict[str, str] = {
    "English":           "en",
    "हिंदी (Hindi)":    "hi",
    "বাংলা (Bengali)":  "bn",
    "தமிழ் (Tamil)":    "ta",
}

# RTL languages — inject dir="rtl" for correct text direction
_RTL_LANGS: set[str] = {"ar", "ur", "fa", "he"}

_LANG_CODES = {v: k for k, v in SUPPORTED_LANGUAGES.items()}
_CACHE_KEY  = "_translate_cache"
_BATCH_KEY  = "_translate_batch_queue"
_CALL_COUNT_KEY = "_translate_call_count"

# Official Cloud Translation API endpoint
_CLOUD_TRANSLATE_URL = "https://translation.googleapis.com/language/translate/v2"


def _get_cache() -> dict:
    if _CACHE_KEY not in st.session_state:
        st.session_state[_CACHE_KEY] = {}
    return st.session_state[_CACHE_KEY]


def _get_call_count() -> int:
    return st.session_state.get(_CALL_COUNT_KEY, 0)


def _increment_call_count() -> None:
    st.session_state[_CALL_COUNT_KEY] = _get_call_count() + 1


def _rate_limit_exceeded() -> bool:
    """Check per-session translation rate limit."""
    limit = RATE_LIMIT.get("translate_calls_per_session", 500)
    return _get_call_count() >= limit


def _translate_via_cloud_api(text: str, target_lang: str) -> str | None:
    """
    Translate using the official Google Cloud Translation API v2.
    Returns translated string on success, None on any failure.
    Only called when GOOGLE_TRANSLATE_API_KEY is configured.
    """
    if not GOOGLE_TRANSLATE_API_KEY:
        return None
    try:
        payload = json.dumps({
            "q":      text,
            "source": "en",
            "target": target_lang,
            "format": "text",
        }).encode("utf-8")
        url = f"{_CLOUD_TRANSLATE_URL}?key={GOOGLE_TRANSLATE_API_KEY}"
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        timeout = RATE_LIMIT.get("translate_timeout_seconds", 5)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
        return data["data"]["translations"][0]["translatedText"]
    except Exception as exc:
        logger.warning("Cloud Translate API failed (lang=%s): %s", target_lang, exc)
        return None


def _translate_via_gtx(text: str, target_lang: str) -> str | None:
    """
    Translate using the free Google Translate gtx endpoint.
    No API key required. Returns translated string or None on failure.
    """
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
        timeout = RATE_LIMIT.get("translate_timeout_seconds", 5)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
        return "".join(item[0] for item in data[0] if item[0])
    except Exception as exc:
        logger.warning("gtx translate failed (lang=%s): %s", target_lang, exc)
        return None


def translate_text(text: str, target_lang: str) -> str:
    """
    Translate a single string.
    Uses Cloud Translation API when key is present, falls back to gtx.
    Results cached in session_state. Rate-limited per session.
    """
    if target_lang == "en" or not text or not text.strip():
        return text

    if _rate_limit_exceeded():
        logger.warning("translate_text: per-session rate limit reached")
        return text

    cache     = _get_cache()
    cache_key = (text, target_lang)
    if cache_key in cache:
        return cache[cache_key]

    _increment_call_count()

    # Try Cloud API first (official, higher quality)
    translated = _translate_via_cloud_api(text, target_lang)

    # Fall back to gtx if cloud API unavailable or fails
    if translated is None:
        translated = _translate_via_gtx(text, target_lang)

    if translated:
        cache[cache_key] = translated
        return translated

    return text


def translate_batch(texts: list[str], target_lang: str) -> list[str]:
    """
    Translate multiple strings efficiently.
    Uses Cloud API batch if key present, else gtx multi-query.
    Falls back to individual translate_text() calls on any error.
    """
    if target_lang == "en" or not texts:
        return texts

    cache    = _get_cache()
    results  = [""] * len(texts)
    uncached: list[tuple[int, str]] = []

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

    if _rate_limit_exceeded():
        for orig_i, text in uncached:
            results[orig_i] = text
        return results

    # Try Cloud API batch
    if GOOGLE_TRANSLATE_API_KEY:
        try:
            payload = json.dumps({
                "q":      [t for _, t in uncached],
                "source": "en",
                "target": target_lang,
                "format": "text",
            }).encode("utf-8")
            url = f"{_CLOUD_TRANSLATE_URL}?key={GOOGLE_TRANSLATE_API_KEY}"
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            timeout = RATE_LIMIT.get("translate_timeout_seconds", 5)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
            translations = data["data"]["translations"]
            for batch_i, (orig_i, text) in enumerate(uncached):
                t = translations[batch_i]["translatedText"] if batch_i < len(translations) else text
                cache[(text, target_lang)] = t
                results[orig_i] = t
            _increment_call_count()
            return results
        except Exception as exc:
            logger.warning("Cloud batch translate failed: %s — falling back to gtx", exc)

    # gtx multi-query batch
    try:
        base = (
            f"https://translate.googleapis.com/translate_a/single"
            f"?client=gtx&sl=en&tl={target_lang}&dt=t"
        )
        for _, text in uncached:
            base += "&q=" + urllib.parse.quote(text, safe="")

        req = urllib.request.Request(base, headers={"User-Agent": "Mozilla/5.0"})
        timeout = RATE_LIMIT.get("translate_timeout_seconds", 5)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw  = resp.read()
            data = json.loads(raw)

        all_translated = [
            "".join(seg[0] for seg in block if seg[0])
            for block in data[0]
            if isinstance(block, list)
        ]

        for batch_i, (orig_i, text) in enumerate(uncached):
            translated = all_translated[batch_i] if batch_i < len(all_translated) else text
            cache[(text, target_lang)] = translated
            results[orig_i] = translated
        _increment_call_count()

    except Exception as exc:
        logger.warning("translate_batch gtx failed (lang=%s): %s — falling back", target_lang, exc)
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
    """
    Compact language-picker widget.
    Injects lang= and dir= HTML attributes for WCAG 3.1.1 compliance.
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
        # Clear translation cache and reset counter on language change
        st.session_state[_CACHE_KEY] = {}
        st.session_state[_CALL_COUNT_KEY] = 0
        st.session_state["language"] = chosen_code
        st.rerun()

    # WCAG 3.1.1 — inject lang attribute so screen readers use the correct voice
    dir_attr = "rtl" if chosen_code in _RTL_LANGS else "ltr"
    st.markdown(
        f'<html lang="{chosen_code}" dir="{dir_attr}">',
        unsafe_allow_html=True,
    )

    if chosen_code != "en":
        api_badge = " · Cloud API" if GOOGLE_TRANSLATE_API_KEY else ""
        st.markdown(
            f'<div style="font-size:0.65rem;color:#27C96E;font-weight:700;margin-top:2px;"'
            f' aria-live="polite" aria-label="Language active: {chosen_name}">'
            f'🌐 {chosen_name} active{api_badge}</div>',
            unsafe_allow_html=True,
        )
