"""
CivicPulse — India-Centric Location & Validation Utilities
==========================================================
Localized for Indian PIN codes, States, and Contact Formats.
"""
from __future__ import annotations
import html
import re


# ── Country Detection ─────────────────────────────────────────────────────────

def detect_country_from_input(location: str) -> str:
    """
    Heuristic country detection.
    Prioritizes Indian 6-digit PIN codes and known state names.
    Defaults to 'IN' for this India-centric application.
    """
    loc = location.replace(" ", "").upper().strip()

    if re.fullmatch(r"\d{6}", loc):
        return "IN"

    indian_states = [
        "MAHARASHTRA", "TAMILNADU", "WESTBENGAL", "KERALA", "ASSAM",
        "DELHI", "KARNATAKA", "GUJARAT", "RAJASTHAN", "UTTARPRADESH",
        "MADHYAPRADESH", "BIHAR", "ODISHA", "TELANGANA", "ANDHRAPRADESH",
        "PUNJAB", "HARYANA", "JHARKHAND", "CHHATTISGARH", "UTTARAKHAND",
        "HIMACHALPRADESH", "GOAA", "GOA", "PUDUCHERRY", "MANIPUR",
        "MEGHALAYA", "MIZORAM", "NAGALAND", "TRIPURA", "SIKKIM",
        "ARUNACHALPRADESH",
    ]
    if any(state in loc.replace(" ", "") for state in indian_states):
        return "IN"

    # US zip (5 digits) — fallback
    if re.fullmatch(r"\d{5}(-\d{4})?", loc):
        return "US"

    return "IN"  # Default for this India-centric app


# ── PIN → State Mapping ────────────────────────────────────────────────────────

_PIN_PREFIX_TO_STATE: dict[str, str] = {
    # West Bengal
    "70": "WB", "71": "WB", "72": "WB", "73": "WB", "74": "WB",
    # Tamil Nadu
    "60": "TN", "61": "TN", "62": "TN", "63": "TN", "64": "TN",
    # Kerala
    "67": "KL", "68": "KL", "69": "KL",
    # Assam
    "78": "AS",
    # Maharashtra
    "40": "MH", "41": "MH", "42": "MH", "43": "MH", "44": "MH",
    # Delhi
    "11": "DL",
    # Karnataka
    "56": "KA", "57": "KA", "58": "KA",
    # Gujarat
    "36": "GJ", "37": "GJ", "38": "GJ", "39": "GJ",
    # Rajasthan
    "30": "RJ", "31": "RJ", "32": "RJ", "33": "RJ", "34": "RJ",
    # Uttar Pradesh
    "20": "UP", "21": "UP", "22": "UP", "23": "UP", "24": "UP", "25": "UP",
    # Bihar
    "80": "BR", "81": "BR", "82": "BR", "83": "BR", "84": "BR", "85": "BR",
    # Puducherry
    "60": "PY",  # overlaps with TN — kept as-is for demo
}

_STATE_NAME_TO_CODE: dict[str, str] = {
    "west bengal": "WB", "tamil nadu": "TN", "kerala": "KL",
    "assam": "AS", "maharashtra": "MH", "delhi": "DL",
    "karnataka": "KA", "gujarat": "GJ", "rajasthan": "RJ",
    "uttar pradesh": "UP", "bihar": "BR", "puducherry": "PY",
    "odisha": "OD", "telangana": "TS", "andhra pradesh": "AP",
    "punjab": "PB", "haryana": "HR", "jharkhand": "JH",
    "chhattisgarh": "CG", "uttarakhand": "UK", "goa": "GA",
    "himachal pradesh": "HP", "manipur": "MN", "meghalaya": "ML",
    "mizoram": "MZ", "nagaland": "NL", "tripura": "TR",
    "sikkim": "SK", "arunachal pradesh": "AR",
}


def parse_location(location: str) -> dict:
    """
    Parse a location string and map PIN codes or state names to state codes.
    Returns a dict with keys: raw, normalized, state_code.
    """
    normalized = location.strip().title()
    loc_data: dict[str, str] = {
        "raw": location,
        "normalized": normalized,
        "state_code": "DEFAULT",
    }

    # Try PIN code first
    pin_match = re.search(r"(\d{2})\d{4}", location.replace(" ", ""))
    if pin_match:
        prefix = pin_match.group(1)
        loc_data["state_code"] = _PIN_PREFIX_TO_STATE.get(prefix, "DEFAULT")
        return loc_data

    # Try state name
    lower = location.strip().lower()
    for name, code in _STATE_NAME_TO_CODE.items():
        if name in lower:
            loc_data["state_code"] = code
            break

    return loc_data


# ── Validators (also re-exported from validators.py) ──────────────────────────

def validate_location_input(location: str | None) -> bool:
    """
    Validate that the input is a meaningful Indian location:
    - A 6-digit PIN code, OR
    - A state / city name 2–100 characters long.
    """
    if not location or not location.strip():
        return False
    clean = location.strip()
    if re.fullmatch(r"\d{6}", clean):
        return True
    if clean.isdigit():
        return False
    return bool(re.fullmatch(r"[A-Za-z\s\-\.]{2,100}", clean))


def validate_email(email: str) -> bool:
    """Standard email validation."""
    if not email or not email.strip():
        return False
    return bool(re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$").match(email.strip()))


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


def sanitize_text(value: str) -> str:
    """HTML-escape a user-supplied string before unsafe_allow_html injection."""
    if not isinstance(value, str):
        value = str(value)
    return html.escape(value, quote=True)
