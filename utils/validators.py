"""
CivicPulse — Input Validators & Sanitizers
==========================================
All user-supplied strings must pass through sanitize_text() before
being injected into unsafe_allow_html blocks.
"""

from __future__ import annotations
import html
import re


# ── XSS Sanitizer (call before ANY unsafe_allow_html injection) ───────────────

def sanitize_text(value: str) -> str:
    """
    Escape HTML special characters in any user-supplied string so it
    cannot be used for Cross-Site Scripting (XSS) when injected via
    unsafe_allow_html=True.

    Examples
    --------
    >>> sanitize_text('<script>alert(1)</script>')
    '&lt;script&gt;alert(1)&lt;/script&gt;'
    >>> sanitize_text('West Bengal')
    'West Bengal'
    """
    if not isinstance(value, str):
        value = str(value)
    return html.escape(value, quote=True)


# ── Location Validators ───────────────────────────────────────────────────────

def validate_location_input(location: str | None) -> bool:
    """
    Validate that the input is a meaningful Indian location:
    - A 6-digit PIN code, OR
    - A state / city name between 2 and 100 characters.

    Returns False for None, empty strings, too-short values (<2 chars),
    and pure-digit strings that are not exactly 6 digits.
    """
    if not location or not location.strip():
        return False

    clean = location.strip()

    # 6-digit Indian PIN code
    if re.fullmatch(r"\d{6}", clean):
        return True

    # Reject other purely numeric strings (too short / too long PINs)
    if clean.isdigit():
        return False

    # State / city name: 2–100 characters, letters / spaces / hyphens only
    if re.fullmatch(r"[A-Za-z\s\-\.]{2,100}", clean):
        return True

    return False


# ── Contact Validators ────────────────────────────────────────────────────────

def validate_email(email: str) -> bool:
    """Standard email validation."""
    if not email or not email.strip():
        return False
    pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    return bool(pattern.match(email.strip()))


def validate_phone(phone: str) -> bool:
    """
    Validate Indian mobile numbers.
    Accepts +91 prefix (12 digits) or plain 10-digit numbers
    starting with 6, 7, 8, or 9.
    """
    if not phone:
        return False
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 12 and digits.startswith("91"):
        return digits[2] in "6789"
    return len(digits) == 10 and digits[0] in "6789"


# ── Re-exports (keep old import path working) ─────────────────────────────────
from .location_utils import validate_location_input   # noqa: F811, E402

__all__ = [
    "sanitize_text",
    "validate_location_input",
    "validate_email",
    "validate_phone",
]
