"""
CivicPulse — India-Centric Location & Validation Utilities
==========================================================
Localized for Indian PIN codes, States, and Contact Formats.
"""
from __future__ import annotations
import re

def detect_country_from_input(location: str) -> str | None:
    """
    Heuristic country detection. 
    Prioritizes Indian 6-digit PIN codes for the hackathon.
    """
    loc = location.replace(" ", "").upper().strip()
    
    # regex for 6-digit Indian PIN
    india_pincodes = re.compile(r"^\d{6}$")
    # regex for US Zip (Fallback)
    us_zip = re.compile(r"^\d{5}(-\d{4})?$")

    if india_pincodes.match(loc):
        return "IN"
    
    # Keywords check for Indian States
    indian_states = ["MAHARASHTRA", "TAMIL NADU", "WEST BENGAL", "KERALA", "ASSAM", "DELHI", "KARNATAKA"]
    if any(state in loc for state in indian_states):
        return "IN"
        
    if us_zip.match(loc):
        return "US"
        
    return "IN"  # Default fallback for your India-centric app

def parse_location(location: str) -> dict:
    """
    Parse a location string and attempt to map PIN codes to Indian States.
    """
    normalized = location.strip().title()
    loc_data = {"raw": location, "normalized": normalized, "state_code": "DEFAULT"}
    
    # Indian PIN Code to State Mapping (First 2 digits)
    pin_match = re.search(r"(\d{2})\d{4}", location.replace(" ", ""))
    if pin_match:
        prefix = pin_match.group(1)
        mapping = {
            "70": "WB", "71": "WB", "72": "WB", "73": "WB", "74": "WB", # West Bengal
            "60": "TN", "61": "TN", "62": "TN", "63": "TN", "64": "TN", # Tamil Nadu
            "67": "KL", "68": "KL", "69": "KL",                         # Kerala
            "78": "AS",                                                 # Assam
            "40": "MH", "41": "MH", "42": "MH", "43": "MH", "44": "MH", # Maharashtra
            "11": "DL"                                                  # Delhi
        }
        loc_data["state_code"] = mapping.get(prefix, "DEFAULT")
        
    return loc_data

# ── Input Validators ──────────────────────────────────────────────────────────

def validate_location_input(location: str | None) -> bool:
    """Validates if input is a valid Indian State name or 6-digit PIN."""
    if not location or not location.strip():
        return False
    
    clean_loc = location.replace(" ", "").strip()
    
    # Check if it's a 6-digit PIN code
    if clean_loc.isdigit() and len(clean_loc) == 6:
        return True
        
    # Otherwise check length for state/city names
    return 2 <= len(location.strip()) <= 100

def validate_email(email: str) -> bool:
    """Standard email validation."""
    pattern = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
    return bool(pattern.match(email.strip()))

def validate_phone(phone: str) -> bool:
    """
    Validates Indian phone numbers.
    Supports +91 prefix and 10-digit mobile numbers.
    """
    # Remove all non-digit characters
    digits = re.sub(r"\D", "", phone)
    
    # If starts with 91 and is 12 digits total
    if len(digits) == 12 and digits.startswith("91"):
        return True
    
    # Standard 10-digit Indian mobile
    return len(digits) == 10 and digits[0] in "6789"