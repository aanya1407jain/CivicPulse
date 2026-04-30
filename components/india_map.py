"""
CivicPulse — Interactive India Map Component
=============================================
Clickable state map showing election schedule, phase dates, and party strength.
Uses SVG-based India map rendered via Streamlit HTML component.
"""

from __future__ import annotations
import streamlit as st
from utils.location_utils import sanitize_text

# ── State election data ────────────────────────────────────────────────────────
INDIA_STATE_ELECTION_DATA = {
     "West Bengal": {
        "type": "State",
        "region": "East India",
        "phase": "Phase I & II Complete",
        "polling_date": "April 17 & 29, 2026",
        "counting_date": "May 4, 2026",
        "total_seats": 294,
        "ruling_party": "AITC",
        "ruling_color": "#00843D",
        "opposition": "BJP",
        "key_contest": "AITC vs BJP",
        "last_election_year": 2021,
        "last_winner_seats": "AITC 213 / BJP 77",
        "last_turnout": "82.2%",
        "next_election_due": "2026",
        "status": "completed",
        "cm": "Mamata Banerjee (AITC)",
        "capital": "Kolkata",
    },
    "Assam": {
        "type": "State",
        "region": "Northeast India",
        "phase": "Phase I Complete",
        "polling_date": "April 5, 2026",
        "counting_date": "May 4, 2026",
        "total_seats": 126,
        "ruling_party": "BJP",
        "ruling_color": "#FF6600",
        "opposition": "INC + BPF",
        "key_contest": "BJP Alliance vs INC-BPF",
        "last_election_year": 2021,
        "last_winner_seats": "BJP 60 / INC 29 / AIUDF 16",
        "last_turnout": "82.5%",
        "next_election_due": "2026",
        "status": "completed",
        "cm": "Himanta Biswa Sarma (BJP)",
        "capital": "Dispur",
    },
    "Kerala": {
        "type": "State",
        "region": "South India",
        "phase": "Single Phase",
        "polling_date": "April 12, 2026",
        "counting_date": "May 4, 2026",
        "total_seats": 140,
        "ruling_party": "CPI(M) - LDF",
        "ruling_color": "#CC0000",
        "opposition": "INC - UDF",
        "key_contest": "LDF vs UDF",
        "last_election_year": 2021,
        "last_winner_seats": "LDF 99 / UDF 41",
        "last_turnout": "74.6%",
        "next_election_due": "2026",
        "status": "completed",
        "cm": "Pinarayi Vijayan (CPI-M)",
        "capital": "Thiruvananthapuram",
    },
    "Tamil Nadu": {
        "type": "State",
        "region": "South India",
        "phase": "Single Phase",
        "polling_date": "April 19, 2026",
        "counting_date": "May 4, 2026",
        "total_seats": 234,
        "ruling_party": "DMK",
        "ruling_color": "#CC0000",
        "opposition": "AIADMK + BJP",
        "key_contest": "DMK Alliance vs AIADMK",
        "last_election_year": 2021,
        "last_winner_seats": "DMK 133 / AIADMK 66",
        "last_turnout": "74.2%",
        "next_election_due": "2026",
        "status": "completed",
        "cm": "M. K. Stalin (DMK)",
        "capital": "Chennai",
    },
    "Puducherry": {
        "type": "UT with Legislature",
        "region": "South India",
        "phase": "Single Phase",
        "polling_date": "April 19, 2026",
        "counting_date": "May 4, 2026",
        "total_seats": 30,
        "ruling_party": "NR Congress-BJP",
        "ruling_color": "#FF6600",
        "opposition": "INC-DMK",
        "key_contest": "NR Congress vs DMK-INC",
        "last_election_year": 2021,
        "last_winner_seats": "NR Congress 10 / INC 2 / DMK 6",
        "last_turnout": "77.3%",
        "next_election_due": "2026",
        "status": "completed",
        "cm": "N. Rangasamy (NR Congress)",
        "capital": "Puducherry",
    },

    # ── STATES WITH ELECTIONS DUE IN 2027 ─────────────────────────────────────
    "Uttar Pradesh": {
        "type": "State",
        "region": "North India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Feb–Mar 2027 (est.)",
        "counting_date": "TBD",
        "total_seats": 403,
        "ruling_party": "BJP",
        "ruling_color": "#FF6600",
        "opposition": "SP + INC",
        "key_contest": "BJP vs Samajwadi Party",
        "last_election_year": 2022,
        "last_winner_seats": "BJP 255 / SP 111",
        "last_turnout": "61.0%",
        "next_election_due": "2027",
        "status": "not_due",
        "cm": "Yogi Adityanath (BJP)",
        "capital": "Lucknow",
    },
    "Punjab": {
        "type": "State",
        "region": "North India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Feb 2027 (est.)",
        "counting_date": "TBD",
        "total_seats": 117,
        "ruling_party": "AAP",
        "ruling_color": "#0080C7",
        "opposition": "INC + SAD",
        "key_contest": "AAP vs INC",
        "last_election_year": 2022,
        "last_winner_seats": "AAP 92 / INC 18",
        "last_turnout": "71.9%",
        "next_election_due": "2027",
        "status": "not_due",
        "cm": "Bhagwant Mann (AAP)",
        "capital": "Chandigarh",
    },
    "Uttarakhand": {
        "type": "State",
        "region": "North India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Feb 2027 (est.)",
        "counting_date": "TBD",
        "total_seats": 70,
        "ruling_party": "BJP",
        "ruling_color": "#FF6600",
        "opposition": "INC",
        "key_contest": "BJP vs INC",
        "last_election_year": 2022,
        "last_winner_seats": "BJP 47 / INC 19",
        "last_turnout": "65.4%",
        "next_election_due": "2027",
        "status": "not_due",
        "cm": "Pushkar Singh Dhami (BJP)",
        "capital": "Dehradun",
    },
    "Goa": {
        "type": "State",
        "region": "West India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Feb 2027 (est.)",
        "counting_date": "TBD",
        "total_seats": 40,
        "ruling_party": "BJP",
        "ruling_color": "#FF6600",
        "opposition": "INC + AAP",
        "key_contest": "BJP vs INC",
        "last_election_year": 2022,
        "last_winner_seats": "BJP 20 / INC 11 / AAP 2",
        "last_turnout": "78.9%",
        "next_election_due": "2027",
        "status": "not_due",
        "cm": "Pramod Sawant (BJP)",
        "capital": "Panaji",
    },
    "Manipur": {
        "type": "State",
        "region": "Northeast India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Feb–Mar 2027 (est.)",
        "counting_date": "TBD",
        "total_seats": 60,
        "ruling_party": "BJP",
        "ruling_color": "#FF6600",
        "opposition": "INC + NPP",
        "key_contest": "BJP vs INC",
        "last_election_year": 2022,
        "last_winner_seats": "BJP 32 / NPP 7 / INC 5",
        "last_turnout": "86.7%",
        "next_election_due": "2027",
        "status": "not_due",
        "cm": "N. Biren Singh (BJP)",
        "capital": "Imphal",
    },

    # ── STATES WITH ELECTIONS DUE IN 2028 ─────────────────────────────────────
    "Gujarat": {
        "type": "State",
        "region": "West India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Dec 2027 (est.)",
        "counting_date": "TBD",
        "total_seats": 182,
        "ruling_party": "BJP",
        "ruling_color": "#FF6600",
        "opposition": "INC + AAP",
        "key_contest": "BJP vs INC",
        "last_election_year": 2022,
        "last_winner_seats": "BJP 156 / INC 17 / AAP 5",
        "last_turnout": "63.3%",
        "next_election_due": "2027",
        "status": "not_due",
        "cm": "Bhupendra Patel (BJP)",
        "capital": "Gandhinagar",
    },
    "Himachal Pradesh": {
        "type": "State",
        "region": "North India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Nov 2027 (est.)",
        "counting_date": "TBD",
        "total_seats": 68,
        "ruling_party": "INC",
        "ruling_color": "#00BFFF",
        "opposition": "BJP",
        "key_contest": "INC vs BJP",
        "last_election_year": 2022,
        "last_winner_seats": "INC 40 / BJP 25",
        "last_turnout": "75.6%",
        "next_election_due": "2027",
        "status": "not_due",
        "cm": "Sukhvinder Singh Sukhu (INC)",
        "capital": "Shimla",
    },
    "Karnataka": {
        "type": "State",
        "region": "South India",
        "phase": "Not in 2026 cycle",
        "polling_date": "May 2028 (est.)",
        "counting_date": "TBD",
        "total_seats": 224,
        "ruling_party": "INC",
        "ruling_color": "#00BFFF",
        "opposition": "BJP + JD(S)",
        "key_contest": "INC vs BJP-JD(S)",
        "last_election_year": 2023,
        "last_winner_seats": "INC 135 / BJP 66 / JD(S) 19",
        "last_turnout": "73.2%",
        "next_election_due": "2028",
        "status": "not_due",
        "cm": "Siddaramaiah (INC)",
        "capital": "Bengaluru",
    },
    "Telangana": {
        "type": "State",
        "region": "South India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Dec 2028 (est.)",
        "counting_date": "TBD",
        "total_seats": 119,
        "ruling_party": "INC",
        "ruling_color": "#00BFFF",
        "opposition": "BRS + BJP",
        "key_contest": "INC vs BRS",
        "last_election_year": 2023,
        "last_winner_seats": "INC 64 / BRS 39 / BJP 8",
        "last_turnout": "72.8%",
        "next_election_due": "2028",
        "status": "not_due",
        "cm": "A. Revanth Reddy (INC)",
        "capital": "Hyderabad",
    },
    "Chhattisgarh": {
        "type": "State",
        "region": "Central India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Nov 2028 (est.)",
        "counting_date": "TBD",
        "total_seats": 90,
        "ruling_party": "BJP",
        "ruling_color": "#FF6600",
        "opposition": "INC",
        "key_contest": "BJP vs INC",
        "last_election_year": 2023,
        "last_winner_seats": "BJP 54 / INC 35",
        "last_turnout": "76.4%",
        "next_election_due": "2028",
        "status": "not_due",
        "cm": "Vishnu Deo Sai (BJP)",
        "capital": "Raipur",
    },
    "Madhya Pradesh": {
        "type": "State",
        "region": "Central India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Nov 2028 (est.)",
        "counting_date": "TBD",
        "total_seats": 230,
        "ruling_party": "BJP",
        "ruling_color": "#FF6600",
        "opposition": "INC",
        "key_contest": "BJP vs INC",
        "last_election_year": 2023,
        "last_winner_seats": "BJP 163 / INC 66",
        "last_turnout": "76.2%",
        "next_election_due": "2028",
        "status": "not_due",
        "cm": "Mohan Yadav (BJP)",
        "capital": "Bhopal",
    },
    "Rajasthan": {
        "type": "State",
        "region": "North India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Dec 2028 (est.)",
        "counting_date": "TBD",
        "total_seats": 200,
        "ruling_party": "BJP",
        "ruling_color": "#FF6600",
        "opposition": "INC",
        "key_contest": "BJP vs INC",
        "last_election_year": 2023,
        "last_winner_seats": "BJP 115 / INC 69",
        "last_turnout": "75.5%",
        "next_election_due": "2028",
        "status": "not_due",
        "cm": "Bhajan Lal Sharma (BJP)",
        "capital": "Jaipur",
    },
    "Mizoram": {
        "type": "State",
        "region": "Northeast India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Nov 2028 (est.)",
        "counting_date": "TBD",
        "total_seats": 40,
        "ruling_party": "ZPM",
        "ruling_color": "#9C27B0",
        "opposition": "MNF + BJP",
        "key_contest": "ZPM vs MNF",
        "last_election_year": 2023,
        "last_winner_seats": "ZPM 27 / MNF 10 / BJP 2",
        "last_turnout": "80.7%",
        "next_election_due": "2028",
        "status": "not_due",
        "cm": "Lalduhoma (ZPM)",
        "capital": "Aizawl",
    },

    # ── STATES WITH ELECTIONS DUE IN 2024–2025 (recently elected) ─────────────
    "Maharashtra": {
        "type": "State",
        "region": "West India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Nov 2024 (done)",
        "counting_date": "Nov 23, 2024",
        "total_seats": 288,
        "ruling_party": "BJP + Shinde Sena",
        "ruling_color": "#FF6600",
        "opposition": "MVA (INC+NCP+UBT Sena)",
        "key_contest": "Mahayuti vs MVA",
        "last_election_year": 2024,
        "last_winner_seats": "Mahayuti 230 / MVA 50",
        "last_turnout": "66.1%",
        "next_election_due": "2029",
        "status": "not_due",
        "cm": "Devendra Fadnavis (BJP)",
        "capital": "Mumbai",
    },
    "Jharkhand": {
        "type": "State",
        "region": "East India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Nov 2024 (done)",
        "counting_date": "Nov 23, 2024",
        "total_seats": 81,
        "ruling_party": "JMM + INC",
        "ruling_color": "#00BFFF",
        "opposition": "BJP + AJSU",
        "key_contest": "INDIA Alliance vs NDA",
        "last_election_year": 2024,
        "last_winner_seats": "JMM 34 / INC 16 / BJP 21",
        "last_turnout": "67.7%",
        "next_election_due": "2029",
        "status": "not_due",
        "cm": "Hemant Soren (JMM)",
        "capital": "Ranchi",
    },
    "Haryana": {
        "type": "State",
        "region": "North India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Oct 2024 (done)",
        "counting_date": "Oct 8, 2024",
        "total_seats": 90,
        "ruling_party": "BJP",
        "ruling_color": "#FF6600",
        "opposition": "INC",
        "key_contest": "BJP vs INC",
        "last_election_year": 2024,
        "last_winner_seats": "BJP 48 / INC 37",
        "last_turnout": "67.9%",
        "next_election_due": "2029",
        "status": "not_due",
        "cm": "Nayab Singh Saini (BJP)",
        "capital": "Chandigarh",
    },
    "Andhra Pradesh": {
        "type": "State",
        "region": "South India",
        "phase": "Not in 2026 cycle",
        "polling_date": "May 2024 (done)",
        "counting_date": "Jun 4, 2024",
        "total_seats": 175,
        "ruling_party": "TDP + JSP + BJP",
        "ruling_color": "#FFD700",
        "opposition": "YSRCP",
        "key_contest": "NDA vs YSRCP",
        "last_election_year": 2024,
        "last_winner_seats": "TDP 135 / YSRCP 11 / JSP 21",
        "last_turnout": "81.6%",
        "next_election_due": "2029",
        "status": "not_due",
        "cm": "N. Chandrababu Naidu (TDP)",
        "capital": "Amaravati",
    },
    "Odisha": {
        "type": "State",
        "region": "East India",
        "phase": "Not in 2026 cycle",
        "polling_date": "May 2024 (done)",
        "counting_date": "Jun 4, 2024",
        "total_seats": 147,
        "ruling_party": "BJP",
        "ruling_color": "#FF6600",
        "opposition": "BJD + INC",
        "key_contest": "BJP vs BJD",
        "last_election_year": 2024,
        "last_winner_seats": "BJP 78 / BJD 51 / INC 14",
        "last_turnout": "74.3%",
        "next_election_due": "2029",
        "status": "not_due",
        "cm": "Mohan Majhi (BJP)",
        "capital": "Bhubaneswar",
    },
    "Arunachal Pradesh": {
        "type": "State",
        "region": "Northeast India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Apr 2024 (done)",
        "counting_date": "Jun 4, 2024",
        "total_seats": 60,
        "ruling_party": "BJP",
        "ruling_color": "#FF6600",
        "opposition": "INC + NPP",
        "key_contest": "BJP dominates",
        "last_election_year": 2024,
        "last_winner_seats": "BJP 46 / NPP 5 / INC 1",
        "last_turnout": "83.5%",
        "next_election_due": "2029",
        "status": "not_due",
        "cm": "Pema Khandu (BJP)",
        "capital": "Itanagar",
    },
    "Sikkim": {
        "type": "State",
        "region": "Northeast India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Apr 2024 (done)",
        "counting_date": "Jun 4, 2024",
        "total_seats": 32,
        "ruling_party": "SKM",
        "ruling_color": "#9C27B0",
        "opposition": "SDF",
        "key_contest": "SKM vs SDF",
        "last_election_year": 2024,
        "last_winner_seats": "SKM 31 / SDF 1",
        "last_turnout": "79.9%",
        "next_election_due": "2029",
        "status": "not_due",
        "cm": "Prem Singh Tamang (SKM)",
        "capital": "Gangtok",
    },

    # ── REMAINING STATES ───────────────────────────────────────────────────────
    "Bihar": {
        "type": "State",
        "region": "East India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Oct–Nov 2025 (done)",
        "counting_date": "Nov 10, 2025",
        "total_seats": 243,
        "ruling_party": "JD(U) + BJP (NDA)",
        "ruling_color": "#FF6600",
        "opposition": "RJD + INC (INDIA)",
        "key_contest": "NDA vs INDIA Alliance",
        "last_election_year": 2020,
        "last_winner_seats": "NDA 125 / RJD 75 / INC 19",
        "last_turnout": "57.1%",
        "next_election_due": "2025",
        "status": "not_due",
        "cm": "Nitish Kumar (JD-U)",
        "capital": "Patna",
    },
    "Delhi": {
        "type": "UT with Legislature",
        "region": "North India",
        "phase": "Elected Feb 2025",
        "polling_date": "Feb 5, 2025 (done)",
        "counting_date": "Feb 8, 2025",
        "total_seats": 70,
        "ruling_party": "BJP",
        "ruling_color": "#FF6600",
        "opposition": "AAP + INC",
        "key_contest": "BJP vs AAP",
        "last_election_year": 2025,
        "last_winner_seats": "BJP 48 / AAP 22",
        "last_turnout": "60.5%",
        "next_election_due": "2030",
        "status": "not_due",
        "cm": "Rekha Gupta (BJP)",
        "capital": "New Delhi",
    },
    "Nagaland": {
        "type": "State",
        "region": "Northeast India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Feb 2023 (done)",
        "counting_date": "Mar 2, 2023",
        "total_seats": 60,
        "ruling_party": "NDPP + BJP",
        "ruling_color": "#FF6600",
        "opposition": "NPF + INC",
        "key_contest": "NDPP-BJP vs NPF",
        "last_election_year": 2023,
        "last_winner_seats": "NDPP 25 / BJP 12 / NPF 2",
        "last_turnout": "83.4%",
        "next_election_due": "2028",
        "status": "not_due",
        "cm": "Neiphiu Rio (NDPP)",
        "capital": "Kohima",
    },
    "Meghalaya": {
        "type": "State",
        "region": "Northeast India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Feb 2023 (done)",
        "counting_date": "Mar 2, 2023",
        "total_seats": 60,
        "ruling_party": "NPP + BJP",
        "ruling_color": "#9C27B0",
        "opposition": "INC + TMC",
        "key_contest": "NPP vs INC",
        "last_election_year": 2023,
        "last_winner_seats": "NPP 26 / INC 5 / BJP 2",
        "last_turnout": "85.9%",
        "next_election_due": "2028",
        "status": "not_due",
        "cm": "Conrad Sangma (NPP)",
        "capital": "Shillong",
    },
    "Tripura": {
        "type": "State",
        "region": "Northeast India",
        "phase": "Not in 2026 cycle",
        "polling_date": "Feb 2023 (done)",
        "counting_date": "Mar 2, 2023",
        "total_seats": 60,
        "ruling_party": "BJP + TIPRA Motha",
        "ruling_color": "#FF6600",
        "opposition": "CPI(M) + INC",
        "key_contest": "BJP vs CPI(M)",
        "last_election_year": 2023,
        "last_winner_seats": "BJP 32 / TIPRA 13 / CPI(M) 11",
        "last_turnout": "89.9%",
        "next_election_due": "2028",
        "status": "not_due",
        "cm": "Manik Saha (BJP)",
        "capital": "Agartala",
    },

    # ── UNION TERRITORIES WITH NO LEGISLATURE ─────────────────────────────────
    "Jammu & Kashmir": {
        "type": "UT with Legislature",
        "region": "North India",
        "phase": "Elected Sep–Oct 2024",
        "polling_date": "Sep–Oct 2024 (done)",
        "counting_date": "Oct 8, 2024",
        "total_seats": 90,
        "ruling_party": "NC + INC",
        "ruling_color": "#00BFFF",
        "opposition": "BJP + PDP",
        "key_contest": "NC vs BJP",
        "last_election_year": 2024,
        "last_winner_seats": "NC 42 / BJP 29 / INC 6",
        "last_turnout": "63.9%",
        "next_election_due": "2029",
        "status": "not_due",
        "cm": "Omar Abdullah (NC)",
        "capital": "Srinagar / Jammu",
    },
    "Ladakh": {
        "type": "UT without Legislature",
        "region": "North India",
        "phase": "No Assembly",
        "polling_date": "Governed by Lt. Governor",
        "counting_date": "N/A",
        "total_seats": 0,
        "ruling_party": "Central Govt.",
        "ruling_color": "#999999",
        "opposition": "N/A",
        "key_contest": "N/A",
        "last_election_year": 0,
        "last_winner_seats": "No Legislative Assembly",
        "last_turnout": "N/A",
        "next_election_due": "N/A",
        "status": "no_assembly",
        "cm": "Lt. Governor (Sinha)",
        "capital": "Leh",
    },
    "Chandigarh": {
        "type": "UT without Legislature",
        "region": "North India",
        "phase": "No Assembly",
        "polling_date": "Municipal elections only",
        "counting_date": "N/A",
        "total_seats": 0,
        "ruling_party": "Central Govt.",
        "ruling_color": "#999999",
        "opposition": "N/A",
        "key_contest": "N/A",
        "last_election_year": 0,
        "last_winner_seats": "No Legislative Assembly",
        "last_turnout": "N/A",
        "next_election_due": "N/A",
        "status": "no_assembly",
        "cm": "Administrator (UT)",
        "capital": "Chandigarh",
    },
    "Dadra & Nagar Haveli and Daman & Diu": {
        "type": "UT without Legislature",
        "region": "West India",
        "phase": "No Assembly",
        "polling_date": "Governed by Administrator",
        "counting_date": "N/A",
        "total_seats": 0,
        "ruling_party": "Central Govt.",
        "ruling_color": "#999999",
        "opposition": "N/A",
        "key_contest": "N/A",
        "last_election_year": 0,
        "last_winner_seats": "No Legislative Assembly",
        "last_turnout": "N/A",
        "next_election_due": "N/A",
        "status": "no_assembly",
        "cm": "Administrator (UT)",
        "capital": "Daman",
    },
    "Lakshadweep": {
        "type": "UT without Legislature",
        "region": "South India",
        "phase": "No Assembly",
        "polling_date": "Governed by Administrator",
        "counting_date": "N/A",
        "total_seats": 0,
        "ruling_party": "Central Govt.",
        "ruling_color": "#999999",
        "opposition": "N/A",
        "key_contest": "N/A",
        "last_election_year": 0,
        "last_winner_seats": "No Legislative Assembly",
        "last_turnout": "N/A",
        "next_election_due": "N/A",
        "status": "no_assembly",
        "cm": "Administrator (UT)",
        "capital": "Kavaratti",
    },
    "Andaman & Nicobar Islands": {
        "type": "UT without Legislature",
        "region": "East India",
        "phase": "No Assembly",
        "polling_date": "Governed by Lt. Governor",
        "counting_date": "N/A",
        "total_seats": 0,
        "ruling_party": "Central Govt.",
        "ruling_color": "#999999",
        "opposition": "N/A",
        "key_contest": "N/A",
        "last_election_year": 0,
        "last_winner_seats": "No Legislative Assembly",
        "last_turnout": "N/A",
        "next_election_due": "N/A",
        "status": "no_assembly",
        "cm": "Lt. Governor (UT)",
        "capital": "Port Blair",
    },
}


STATUS_COLORS = {
    "completed": "#0E6B06",
    "live": "#C62828",
    "upcoming": "#2D3561",
    "not_voting": "#CCCCCC",
}


def _state_info_card(state: str) -> None:
    """Render detailed info card for a selected state."""
    data = INDIA_STATE_ELECTION_DATA.get(state)
    if not data:
        st.info(f"No 2026 election data available for **{state}**.")
        return

    status_color = STATUS_COLORS.get(data["status"], "#999")
    status_labels = {"completed": "✅ Voting Complete", "live": "🔴 LIVE", "upcoming": "📅 Upcoming"}
    status_text = status_labels.get(data["status"], "—")

    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg, #FAFAF8, #FFFFFF);
                    border-radius:16px;padding:20px;border:1px solid #E8E4DC;
                    border-top:5px solid {data['ruling_color']};
                    box-shadow:0 4px 16px rgba(26,26,46,0.08);">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
                <div style="flex:1;">
                    <div style="font-weight:800;font-size:1.2rem;color:#1A1A2E;">
                        🗳️ {sanitize_text(state)}
                    </div>
                    <div style="color:#5C5C7A;font-size:0.85rem;margin-top:2px;">
                        {data['total_seats']} Assembly Seats · {sanitize_text(data['key_contest'])}
                    </div>
                </div>
                <div style="background:{status_color}18;border:1px solid {status_color}40;
                             color:{status_color};font-weight:700;font-size:0.8rem;
                             padding:6px 14px;border-radius:20px;white-space:nowrap;">
                    {status_text}
                </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                <div style="background:#F5F3EF;border-radius:10px;padding:12px;">
                    <div style="font-size:0.72rem;color:#9090A8;font-weight:700;
                                text-transform:uppercase;letter-spacing:0.05em;">Phase</div>
                    <div style="font-weight:700;color:#1A1A2E;font-size:0.88rem;margin-top:4px;">
                        {sanitize_text(data['phase'])}
                    </div>
                </div>
                <div style="background:#F5F3EF;border-radius:10px;padding:12px;">
                    <div style="font-size:0.72rem;color:#9090A8;font-weight:700;
                                text-transform:uppercase;letter-spacing:0.05em;">Counting</div>
                    <div style="font-weight:700;color:#1A1A2E;font-size:0.88rem;margin-top:4px;">
                        {sanitize_text(data['counting_date'])}
                    </div>
                </div>
                <div style="background:#F5F3EF;border-radius:10px;padding:12px;">
                    <div style="font-size:0.72rem;color:#9090A8;font-weight:700;
                                text-transform:uppercase;letter-spacing:0.05em;">Ruling Party</div>
                    <div style="font-weight:700;font-size:0.88rem;margin-top:4px;
                                color:{data['ruling_color']};">
                        {sanitize_text(data['ruling_party'])}
                    </div>
                </div>
                <div style="background:#F5F3EF;border-radius:10px;padding:12px;">
                    <div style="font-size:0.72rem;color:#9090A8;font-weight:700;
                                text-transform:uppercase;letter-spacing:0.05em;">2021 Turnout</div>
                    <div style="font-weight:700;color:#1A1A2E;font-size:0.88rem;margin-top:4px;">
                        {sanitize_text(data['turnout_2021'])}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_india_map() -> None:
    """Render the interactive India state election map."""
    st.markdown("### 🗺️ India Election Map — 2026 Assembly Polls")
    st.caption(
        "Select a state below to view election schedule, phase details, and party strength. "
        "States highlighted are holding 2026 Assembly Elections."
    )

    # ── State Selector (interactive dropdown acting as map clickthrough) ────────
    col_select, col_legend = st.columns([2, 1])

    with col_select:
        voting_states = list(INDIA_STATE_ELECTION_DATA.keys())
        selected_state = st.selectbox(
            "🔍 Select an Election State",
            ["— Choose a State —"] + voting_states,
            key="india_map_state_select",
        )

    with col_legend:
        st.markdown(
            """
            <div style="background:#FAFAF8;border-radius:12px;padding:14px;
                        border:1px solid #E8E4DC;font-size:0.78rem;">
                <div style="font-weight:700;color:#1A1A2E;margin-bottom:8px;">
                    🗺️ Map Legend
                </div>
                <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
                    <div style="width:12px;height:12px;background:#0E6B06;border-radius:50%;"></div>
                    <span style="color:#5C5C7A;">Voting Completed</span>
                </div>
                <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
                    <div style="width:12px;height:12px;background:#C62828;border-radius:50%;"></div>
                    <span style="color:#5C5C7A;">Live / Counting</span>
                </div>
                <div style="display:flex;align-items:center;gap:6px;">
                    <div style="width:12px;height:12px;background:#CCCCCC;border-radius:50%;"></div>
                    <span style="color:#5C5C7A;">Not in 2026 cycle</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # ── State cards overview ───────────────────────────────────────────────────
    if selected_state and selected_state != "— Choose a State —":
        _state_info_card(selected_state)
    else:
        # Show all states in a grid overview
        st.markdown("#### 📋 All 2026 Election States at a Glance")
        cols = st.columns(2)
        for i, (state, data) in enumerate(INDIA_STATE_ELECTION_DATA.items()):
            with cols[i % 2]:
                status_color = STATUS_COLORS.get(data["status"], "#999")
                st.markdown(
                    f"""
                    <div style="background:#FFFFFF;border-radius:12px;padding:14px;
                                border:1px solid #E8E4DC;border-left:5px solid {data['ruling_color']};
                                margin-bottom:10px;box-shadow:0 1px 4px rgba(0,0,0,0.06);">
                        <div style="font-weight:700;color:#1A1A2E;font-size:0.95rem;">
                            {sanitize_text(state)}
                        </div>
                        <div style="font-size:0.78rem;color:#5C5C7A;margin:4px 0;">
                            {data['total_seats']} seats · {sanitize_text(data['polling_date'])}
                        </div>
                        <div style="display:flex;align-items:center;gap:8px;margin-top:6px;">
                            <span style="background:{data['ruling_color']}22;color:{data['ruling_color']};
                                         font-size:0.7rem;font-weight:700;padding:2px 8px;border-radius:20px;">
                                {sanitize_text(data['ruling_party'])}
                            </span>
                            <span style="background:{status_color}18;color:{status_color};
                                         font-size:0.7rem;font-weight:700;padding:2px 8px;border-radius:20px;">
                                ● {data['status'].title()}
                            </span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.divider()

    # ── ECI Schedule Link ──────────────────────────────────────────────────────
    st.link_button(
        "📅 Full Election Schedule on ECI Website →",
        "https://eci.gov.in/elections/",
        use_container_width=True,
    )
