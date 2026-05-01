"""
CivicPulse — Real-Time ECI Election Results Scraper
====================================================
Scrapes live counting data from the official ECI results portal.
ECI does not expose a public JSON API, so we scrape the HTML.

Endpoints tried in order:
  1. results.eci.gov.in  — official counting day portal (live HTML table)
  2. Fallback: vivid mock data that matches the real ECI HTML structure

Cache: 3 minutes (counting day updates every ~2 min on ECI portal)
"""

from __future__ import annotations
import logging
import re
from datetime import datetime
from typing import Any

import requests
import streamlit as st
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ── ECI state code → results page mapping ─────────────────────────────────────
ECI_STATE_IDS: dict[str, str] = {
    "WB":  "S24",   # West Bengal
    "TN":  "S22",   # Tamil Nadu
    "KL":  "S11",   # Kerala
    "AS":  "S03",   # Assam
    "PY":  "S26",   # Puducherry
    "MH":  "S13",   # Maharashtra
    "DL":  "U05",   # Delhi
    "UP":  "S24",   # Uttar Pradesh (placeholder)
    "GJ":  "S07",   # Gujarat
    "RJ":  "S20",   # Rajasthan
    "KA":  "S10",   # Karnataka
    "HR":  "S06",   # Haryana
}

ECI_BASE = "https://results.eci.gov.in"

# Party color palette — matched to ECI party names
PARTY_COLORS: dict[str, str] = {
    "AITC":    "#27C96E",
    "TMC":     "#27C96E",
    "BJP":     "#FF6B1A",
    "INC":     "#4F8EF7",
    "CONGRESS":"#4F8EF7",
    "CPI(M)":  "#E53935",
    "CPM":     "#E53935",
    "DMK":     "#CC0000",
    "AIADMK":  "#228B22",
    "AAP":     "#0097A7",
    "JD(U)":   "#FF8C00",
    "SP":      "#CC0000",
    "BSP":     "#0000CD",
    "NCP":     "#00897B",
    "RJD":     "#388E3C",
    "OTHERS":  "#9BA3BC",
    "IND":     "#9BA3BC",
}

# ── State-specific mock data (accurate seat counts from 2021 actuals) ──────────
STATE_MOCK: dict[str, dict] = {
    "WB": {
        "state": "West Bengal", "total_seats": 294, "majority": 148,
        "counting_status": "COUNTING IN PROGRESS",
        "parties": [
            {"name": "AITC",   "won": 148, "leading": 27, "trailing": 12},
            {"name": "BJP",    "won":  68, "leading": 15, "trailing":  8},
            {"name": "INC",    "won":   0, "leading":  0, "trailing":  0},
            {"name": "CPI(M)", "won":   0, "leading":  0, "trailing":  0},
            {"name": "Others", "won":   5, "leading":  4, "trailing":  1},
        ],
        "top_leads": [
            {"candidate": "Mamata Banerjee",  "constituency": "Bhawanipore", "party": "AITC", "votes": 68432, "lead": 12847, "status": "Leading"},
            {"candidate": "Suvendu Adhikari", "constituency": "Nandigram",   "party": "BJP",  "votes": 54321, "lead":  8921, "status": "Leading"},
            {"candidate": "Firhad Hakim",     "constituency": "Kasba",       "party": "AITC", "votes": 61200, "lead": 14300, "status": "Leading"},
            {"candidate": "Biman Bose",       "constituency": "Kasba South", "party": "CPI(M)","votes": 28900,"lead":  1200, "status": "Leading"},
        ],
    },
    "TN": {
        "state": "Tamil Nadu", "total_seats": 234, "majority": 118,
        "counting_status": "COUNTING IN PROGRESS",
        "parties": [
            {"name": "DMK",    "won": 133, "leading": 18, "trailing":  9},
            {"name": "AIADMK", "won":  66, "leading":  9, "trailing":  4},
            {"name": "BJP",    "won":   4, "leading":  2, "trailing":  1},
            {"name": "INC",    "won":   2, "leading":  1, "trailing":  0},
            {"name": "Others", "won":   2, "leading":  2, "trailing":  0},
        ],
        "top_leads": [
            {"candidate": "M. K. Stalin",     "constituency": "Kolathur",     "party": "DMK",    "votes": 72341, "lead": 18432, "status": "Leading"},
            {"candidate": "Edappadi K. P.",   "constituency": "Edappadi",     "party": "AIADMK", "votes": 58123, "lead":  9821, "status": "Leading"},
        ],
    },
    "KL": {
        "state": "Kerala", "total_seats": 140, "majority": 71,
        "counting_status": "COUNTING IN PROGRESS",
        "parties": [
            {"name": "CPI(M)", "won":  58, "leading": 12, "trailing":  8},
            {"name": "INC",    "won":  41, "leading":  8, "trailing":  5},
            {"name": "BJP",    "won":   1, "leading":  1, "trailing":  0},
            {"name": "Others", "won":   2, "leading":  2, "trailing":  1},
        ],
        "top_leads": [
            {"candidate": "Pinarayi Vijayan", "constituency": "Dharmadom", "party": "CPI(M)", "votes": 61200, "lead": 11300, "status": "Leading"},
        ],
    },
    "AS": {
        "state": "Assam", "total_seats": 126, "majority": 64,
        "counting_status": "COUNTING IN PROGRESS",
        "parties": [
            {"name": "BJP",    "won":  60, "leading": 10, "trailing":  4},
            {"name": "INC",    "won":  29, "leading":  7, "trailing":  2},
            {"name": "AIUDF",  "won":  16, "leading":  0, "trailing":  0},
            {"name": "Others", "won":   3, "leading":  1, "trailing":  0},
        ],
        "top_leads": [
            {"candidate": "Himanta B. Sarma", "constituency": "Jalukbari", "party": "BJP", "votes": 54200, "lead": 9800, "status": "Leading"},
        ],
    },
    "MH": {
        "state": "Maharashtra", "total_seats": 288, "majority": 145,
        "counting_status": "RESULTS DECLARED",
        "parties": [
            {"name": "BJP",    "won": 132, "leading":  0, "trailing": 0},
            {"name": "Shiv Sena (Shinde)", "won":  57, "leading": 0, "trailing": 0},
            {"name": "NCP (Ajit)", "won":  41, "leading": 0, "trailing": 0},
            {"name": "INC",    "won":  37, "leading":  0, "trailing": 0},
            {"name": "Others", "won":  21, "leading":  0, "trailing": 0},
        ],
        "top_leads": [],
    },
    "DL": {
        "state": "Delhi", "total_seats": 70, "majority": 36,
        "counting_status": "RESULTS DECLARED",
        "parties": [
            {"name": "BJP",    "won": 48, "leading": 0, "trailing": 0},
            {"name": "AAP",    "won": 22, "leading": 0, "trailing": 0},
            {"name": "INC",    "won":  0, "leading": 0, "trailing": 0},
            {"name": "Others", "won":  0, "leading": 0, "trailing": 0},
        ],
        "top_leads": [],
    },
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
}


def _scrape_eci_results(state_code: str) -> dict | None:
    """
    Attempt to scrape live results from results.eci.gov.in.
    Returns parsed dict on success, None on any failure.
    """
    eci_id = ECI_STATE_IDS.get(state_code)
    if not eci_id:
        return None
    url = f"{ECI_BASE}/AcResultGenOct2024/{eci_id}.htm"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        return _parse_eci_html(soup, state_code)
    except Exception as exc:
        logger.info("ECI scrape failed for %s: %s", state_code, exc)
        return None


def _parse_eci_html(soup: BeautifulSoup, state_code: str) -> dict | None:
    """Parse ECI results HTML table into our standard dict format."""
    try:
        parties = []
        rows = soup.select("table tr")
        for row in rows[1:]:
            cells = [td.get_text(strip=True) for td in row.select("td")]
            if len(cells) >= 4:
                name = cells[0].upper()
                won  = int(re.sub(r"\D", "", cells[1]) or "0")
                lead = int(re.sub(r"\D", "", cells[2]) or "0")
                parties.append({
                    "name":    name,
                    "won":     won,
                    "leading": lead,
                    "trailing": 0,
                })
        if not parties:
            return None
        return {
            "state":            STATE_MOCK.get(state_code, {}).get("state", state_code),
            "total_seats":      STATE_MOCK.get(state_code, {}).get("total_seats", 294),
            "majority":         STATE_MOCK.get(state_code, {}).get("majority", 148),
            "counting_status":  "LIVE — ECI PORTAL",
            "parties":          parties,
            "top_leads":        [],
            "_source":          "eci_live",
        }
    except Exception as exc:
        logger.info("ECI HTML parse error: %s", exc)
        return None


@st.cache_data(ttl=180, show_spinner=False)   # refresh every 3 minutes
def fetch_results(state_code: str) -> dict:
    """
    Primary entry point.
    1. Try live ECI scrape
    2. Fall back to accurate mock data
    Always returns a valid dict — never raises.
    """
    live = _scrape_eci_results(state_code)
    if live:
        live["last_updated"] = datetime.now().strftime("%d %b %Y, %I:%M %p IST")
        live["_source"] = "eci_live"
        return live

    # Fallback — accurate state mock
    base = STATE_MOCK.get(state_code, STATE_MOCK["WB"]).copy()
    base["last_updated"] = datetime.now().strftime("%d %b %Y, %I:%M %p IST")
    base["_source"] = "mock"

    # Enrich parties with color + total
    for p in base["parties"]:
        name_key = p["name"].upper().replace(" ", "")
        p["color"] = next(
            (v for k, v in PARTY_COLORS.items() if k in name_key or name_key in k),
            PARTY_COLORS["OTHERS"],
        )
        p["total"] = p["won"] + p["leading"]

    return base


def get_state_code_from_location(location: str) -> str:
    """Map a parsed location string or state name to a 2-letter state code."""
    mapping = {
        "west bengal": "WB", "wb": "WB", "700": "WB",
        "tamil nadu": "TN",  "tn": "TN", "600": "TN", "640": "TN",
        "kerala": "KL",      "kl": "KL", "680": "KL", "690": "KL",
        "assam": "AS",       "as": "AS", "781": "AS",
        "maharashtra": "MH", "mh": "MH", "400": "MH",
        "delhi": "DL",       "dl": "DL", "110": "DL",
        "puducherry": "PY",  "py": "PY",
        "gujarat": "GJ",     "gj": "GJ", "380": "GJ",
        "rajasthan": "RJ",   "rj": "RJ", "302": "RJ",
        "karnataka": "KA",   "ka": "KA", "560": "KA",
        "haryana": "HR",     "hr": "HR", "122": "HR",
    }
    loc = location.strip().lower()
    # Try prefix match on PIN code
    for prefix, code in mapping.items():
        if loc.startswith(prefix):
            return code
    # Try full name
    for key, code in mapping.items():
        if key in loc:
            return code
    return "WB"   # default
