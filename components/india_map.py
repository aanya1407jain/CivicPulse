"""
CivicPulse — Interactive India Map Component
=============================================
Complete data for all 28 States + 8 Union Territories of India.
Dark-theme version: all inline HTML uses dark palette.
"""

from __future__ import annotations
import streamlit as st
from utils.location_utils import sanitize_text

ALL_INDIA_DATA = {
    "West Bengal": {
        "type": "State", "region": "East India", "phase": "Phase I & II Complete",
        "polling_date": "April 17 & 29, 2026", "counting_date": "May 4, 2026",
        "total_seats": 294, "ruling_party": "AITC", "ruling_color": "#27C96E",
        "opposition": "BJP", "key_contest": "AITC vs BJP", "last_election_year": 2021,
        "last_winner_seats": "AITC 213 / BJP 77", "last_turnout": "82.2%",
        "next_election_due": "2026", "status": "completed",
        "cm": "Mamata Banerjee (AITC)", "capital": "Kolkata",
    },
    "Assam": {
        "type": "State", "region": "Northeast India", "phase": "Phase I Complete",
        "polling_date": "April 5, 2026", "counting_date": "May 4, 2026",
        "total_seats": 126, "ruling_party": "BJP", "ruling_color": "#FF6B1A",
        "opposition": "INC + BPF", "key_contest": "BJP Alliance vs INC-BPF", "last_election_year": 2021,
        "last_winner_seats": "BJP 60 / INC 29 / AIUDF 16", "last_turnout": "82.5%",
        "next_election_due": "2026", "status": "completed",
        "cm": "Himanta Biswa Sarma (BJP)", "capital": "Dispur",
    },
    "Kerala": {
        "type": "State", "region": "South India", "phase": "Single Phase",
        "polling_date": "April 12, 2026", "counting_date": "May 4, 2026",
        "total_seats": 140, "ruling_party": "CPI(M) - LDF", "ruling_color": "#F74F4F",
        "opposition": "INC - UDF", "key_contest": "LDF vs UDF", "last_election_year": 2021,
        "last_winner_seats": "LDF 99 / UDF 41", "last_turnout": "74.6%",
        "next_election_due": "2026", "status": "completed",
        "cm": "Pinarayi Vijayan (CPI-M)", "capital": "Thiruvananthapuram",
    },
    "Tamil Nadu": {
        "type": "State", "region": "South India", "phase": "Single Phase",
        "polling_date": "April 19, 2026", "counting_date": "May 4, 2026",
        "total_seats": 234, "ruling_party": "DMK", "ruling_color": "#F74F4F",
        "opposition": "AIADMK + BJP", "key_contest": "DMK Alliance vs AIADMK", "last_election_year": 2021,
        "last_winner_seats": "DMK 133 / AIADMK 66", "last_turnout": "74.2%",
        "next_election_due": "2026", "status": "completed",
        "cm": "M. K. Stalin (DMK)", "capital": "Chennai",
    },
    "Puducherry": {
        "type": "UT with Legislature", "region": "South India", "phase": "Single Phase",
        "polling_date": "April 19, 2026", "counting_date": "May 4, 2026",
        "total_seats": 30, "ruling_party": "NR Congress-BJP", "ruling_color": "#FF6B1A",
        "opposition": "INC-DMK", "key_contest": "NR Congress vs DMK-INC", "last_election_year": 2021,
        "last_winner_seats": "NR Congress 10 / INC 2 / DMK 6", "last_turnout": "77.3%",
        "next_election_due": "2026", "status": "completed",
        "cm": "N. Rangasamy (NR Congress)", "capital": "Puducherry",
    },
    "Uttar Pradesh": {
        "type": "State", "region": "North India", "phase": "Not in 2026 cycle",
        "polling_date": "Feb–Mar 2027 (est.)", "counting_date": "TBD",
        "total_seats": 403, "ruling_party": "BJP", "ruling_color": "#FF6B1A",
        "opposition": "SP + INC", "key_contest": "BJP vs Samajwadi Party", "last_election_year": 2022,
        "last_winner_seats": "BJP 255 / SP 111", "last_turnout": "61.0%",
        "next_election_due": "2027", "status": "not_due",
        "cm": "Yogi Adityanath (BJP)", "capital": "Lucknow",
    },
    "Punjab": {
        "type": "State", "region": "North India", "phase": "Not in 2026 cycle",
        "polling_date": "Feb 2027 (est.)", "counting_date": "TBD",
        "total_seats": 117, "ruling_party": "AAP", "ruling_color": "#4F8EF7",
        "opposition": "INC + SAD", "key_contest": "AAP vs INC", "last_election_year": 2022,
        "last_winner_seats": "AAP 92 / INC 18", "last_turnout": "71.9%",
        "next_election_due": "2027", "status": "not_due",
        "cm": "Bhagwant Mann (AAP)", "capital": "Chandigarh",
    },
    "Uttarakhand": {
        "type": "State", "region": "North India", "phase": "Not in 2026 cycle",
        "polling_date": "Feb 2027 (est.)", "counting_date": "TBD",
        "total_seats": 70, "ruling_party": "BJP", "ruling_color": "#FF6B1A",
        "opposition": "INC", "key_contest": "BJP vs INC", "last_election_year": 2022,
        "last_winner_seats": "BJP 47 / INC 19", "last_turnout": "65.4%",
        "next_election_due": "2027", "status": "not_due",
        "cm": "Pushkar Singh Dhami (BJP)", "capital": "Dehradun",
    },
    "Goa": {
        "type": "State", "region": "West India", "phase": "Not in 2026 cycle",
        "polling_date": "Feb 2027 (est.)", "counting_date": "TBD",
        "total_seats": 40, "ruling_party": "BJP", "ruling_color": "#FF6B1A",
        "opposition": "INC + AAP", "key_contest": "BJP vs INC", "last_election_year": 2022,
        "last_winner_seats": "BJP 20 / INC 11 / AAP 2", "last_turnout": "78.9%",
        "next_election_due": "2027", "status": "not_due",
        "cm": "Pramod Sawant (BJP)", "capital": "Panaji",
    },
    "Manipur": {
        "type": "State", "region": "Northeast India", "phase": "Not in 2026 cycle",
        "polling_date": "Feb–Mar 2027 (est.)", "counting_date": "TBD",
        "total_seats": 60, "ruling_party": "BJP", "ruling_color": "#FF6B1A",
        "opposition": "INC + NPP", "key_contest": "BJP vs INC", "last_election_year": 2022,
        "last_winner_seats": "BJP 32 / NPP 7 / INC 5", "last_turnout": "86.7%",
        "next_election_due": "2027", "status": "not_due",
        "cm": "N. Biren Singh (BJP)", "capital": "Imphal",
    },
    "Gujarat": {
        "type": "State", "region": "West India", "phase": "Not in 2026 cycle",
        "polling_date": "Dec 2027 (est.)", "counting_date": "TBD",
        "total_seats": 182, "ruling_party": "BJP", "ruling_color": "#FF6B1A",
        "opposition": "INC + AAP", "key_contest": "BJP vs INC", "last_election_year": 2022,
        "last_winner_seats": "BJP 156 / INC 17 / AAP 5", "last_turnout": "63.3%",
        "next_election_due": "2027", "status": "not_due",
        "cm": "Bhupendra Patel (BJP)", "capital": "Gandhinagar",
    },
    "Himachal Pradesh": {
        "type": "State", "region": "North India", "phase": "Not in 2026 cycle",
        "polling_date": "Nov 2027 (est.)", "counting_date": "TBD",
        "total_seats": 68, "ruling_party": "INC", "ruling_color": "#4F8EF7",
        "opposition": "BJP", "key_contest": "INC vs BJP", "last_election_year": 2022,
        "last_winner_seats": "INC 40 / BJP 25", "last_turnout": "75.6%",
        "next_election_due": "2027", "status": "not_due",
        "cm": "Sukhvinder Singh Sukhu (INC)", "capital": "Shimla",
    },
    "Karnataka": {
        "type": "State", "region": "South India", "phase": "Not in 2026 cycle",
        "polling_date": "May 2028 (est.)", "counting_date": "TBD",
        "total_seats": 224, "ruling_party": "INC", "ruling_color": "#4F8EF7",
        "opposition": "BJP + JD(S)", "key_contest": "INC vs BJP-JD(S)", "last_election_year": 2023,
        "last_winner_seats": "INC 135 / BJP 66 / JD(S) 19", "last_turnout": "73.2%",
        "next_election_due": "2028", "status": "not_due",
        "cm": "Siddaramaiah (INC)", "capital": "Bengaluru",
    },
    "Telangana": {
        "type": "State", "region": "South India", "phase": "Not in 2026 cycle",
        "polling_date": "Dec 2028 (est.)", "counting_date": "TBD",
        "total_seats": 119, "ruling_party": "INC", "ruling_color": "#4F8EF7",
        "opposition": "BRS + BJP", "key_contest": "INC vs BRS", "last_election_year": 2023,
        "last_winner_seats": "INC 64 / BRS 39 / BJP 8", "last_turnout": "72.8%",
        "next_election_due": "2028", "status": "not_due",
        "cm": "A. Revanth Reddy (INC)", "capital": "Hyderabad",
    },
    "Chhattisgarh": {
        "type": "State", "region": "Central India", "phase": "Not in 2026 cycle",
        "polling_date": "Nov 2028 (est.)", "counting_date": "TBD",
        "total_seats": 90, "ruling_party": "BJP", "ruling_color": "#FF6B1A",
        "opposition": "INC", "key_contest": "BJP vs INC", "last_election_year": 2023,
        "last_winner_seats": "BJP 54 / INC 35", "last_turnout": "76.4%",
        "next_election_due": "2028", "status": "not_due",
        "cm": "Vishnu Deo Sai (BJP)", "capital": "Raipur",
    },
    "Madhya Pradesh": {
        "type": "State", "region": "Central India", "phase": "Not in 2026 cycle",
        "polling_date": "Nov 2028 (est.)", "counting_date": "TBD",
        "total_seats": 230, "ruling_party": "BJP", "ruling_color": "#FF6B1A",
        "opposition": "INC", "key_contest": "BJP vs INC", "last_election_year": 2023,
        "last_winner_seats": "BJP 163 / INC 66", "last_turnout": "76.2%",
        "next_election_due": "2028", "status": "not_due",
        "cm": "Mohan Yadav (BJP)", "capital": "Bhopal",
    },
    "Rajasthan": {
        "type": "State", "region": "North India", "phase": "Not in 2026 cycle",
        "polling_date": "Dec 2028 (est.)", "counting_date": "TBD",
        "total_seats": 200, "ruling_party": "BJP", "ruling_color": "#FF6B1A",
        "opposition": "INC", "key_contest": "BJP vs INC", "last_election_year": 2023,
        "last_winner_seats": "BJP 115 / INC 69", "last_turnout": "75.5%",
        "next_election_due": "2028", "status": "not_due",
        "cm": "Bhajan Lal Sharma (BJP)", "capital": "Jaipur",
    },
    "Mizoram": {
        "type": "State", "region": "Northeast India", "phase": "Not in 2026 cycle",
        "polling_date": "Nov 2028 (est.)", "counting_date": "TBD",
        "total_seats": 40, "ruling_party": "ZPM", "ruling_color": "#C084FC",
        "opposition": "MNF + BJP", "key_contest": "ZPM vs MNF", "last_election_year": 2023,
        "last_winner_seats": "ZPM 27 / MNF 10 / BJP 2", "last_turnout": "80.7%",
        "next_election_due": "2028", "status": "not_due",
        "cm": "Lalduhoma (ZPM)", "capital": "Aizawl",
    },
    "Maharashtra": {
        "type": "State", "region": "West India", "phase": "Not in 2026 cycle",
        "polling_date": "Nov 2024 (done)", "counting_date": "Nov 23, 2024",
        "total_seats": 288, "ruling_party": "BJP + Shinde Sena", "ruling_color": "#FF6B1A",
        "opposition": "MVA (INC+NCP+UBT Sena)", "key_contest": "Mahayuti vs MVA", "last_election_year": 2024,
        "last_winner_seats": "Mahayuti 230 / MVA 50", "last_turnout": "66.1%",
        "next_election_due": "2029", "status": "not_due",
        "cm": "Devendra Fadnavis (BJP)", "capital": "Mumbai",
    },
    "Jharkhand": {
        "type": "State", "region": "East India", "phase": "Not in 2026 cycle",
        "polling_date": "Nov 2024 (done)", "counting_date": "Nov 23, 2024",
        "total_seats": 81, "ruling_party": "JMM + INC", "ruling_color": "#4F8EF7",
        "opposition": "BJP + AJSU", "key_contest": "INDIA Alliance vs NDA", "last_election_year": 2024,
        "last_winner_seats": "JMM 34 / INC 16 / BJP 21", "last_turnout": "67.7%",
        "next_election_due": "2029", "status": "not_due",
        "cm": "Hemant Soren (JMM)", "capital": "Ranchi",
    },
    "Haryana": {
        "type": "State", "region": "North India", "phase": "Not in 2026 cycle",
        "polling_date": "Oct 2024 (done)", "counting_date": "Oct 8, 2024",
        "total_seats": 90, "ruling_party": "BJP", "ruling_color": "#FF6B1A",
        "opposition": "INC", "key_contest": "BJP vs INC", "last_election_year": 2024,
        "last_winner_seats": "BJP 48 / INC 37", "last_turnout": "67.9%",
        "next_election_due": "2029", "status": "not_due",
        "cm": "Nayab Singh Saini (BJP)", "capital": "Chandigarh",
    },
    "Andhra Pradesh": {
        "type": "State", "region": "South India", "phase": "Not in 2026 cycle",
        "polling_date": "May 2024 (done)", "counting_date": "Jun 4, 2024",
        "total_seats": 175, "ruling_party": "TDP + JSP + BJP", "ruling_color": "#F7C94F",
        "opposition": "YSRCP", "key_contest": "NDA vs YSRCP", "last_election_year": 2024,
        "last_winner_seats": "TDP 135 / YSRCP 11 / JSP 21", "last_turnout": "81.6%",
        "next_election_due": "2029", "status": "not_due",
        "cm": "N. Chandrababu Naidu (TDP)", "capital": "Amaravati",
    },
    "Odisha": {
        "type": "State", "region": "East India", "phase": "Not in 2026 cycle",
        "polling_date": "May 2024 (done)", "counting_date": "Jun 4, 2024",
        "total_seats": 147, "ruling_party": "BJP", "ruling_color": "#FF6B1A",
        "opposition": "BJD + INC", "key_contest": "BJP vs BJD", "last_election_year": 2024,
        "last_winner_seats": "BJP 78 / BJD 51 / INC 14", "last_turnout": "74.3%",
        "next_election_due": "2029", "status": "not_due",
        "cm": "Mohan Majhi (BJP)", "capital": "Bhubaneswar",
    },
    "Arunachal Pradesh": {
        "type": "State", "region": "Northeast India", "phase": "Not in 2026 cycle",
        "polling_date": "Apr 2024 (done)", "counting_date": "Jun 4, 2024",
        "total_seats": 60, "ruling_party": "BJP", "ruling_color": "#FF6B1A",
        "opposition": "INC + NPP", "key_contest": "BJP dominates", "last_election_year": 2024,
        "last_winner_seats": "BJP 46 / NPP 5 / INC 1", "last_turnout": "83.5%",
        "next_election_due": "2029", "status": "not_due",
        "cm": "Pema Khandu (BJP)", "capital": "Itanagar",
    },
    "Sikkim": {
        "type": "State", "region": "Northeast India", "phase": "Not in 2026 cycle",
        "polling_date": "Apr 2024 (done)", "counting_date": "Jun 4, 2024",
        "total_seats": 32, "ruling_party": "SKM", "ruling_color": "#C084FC",
        "opposition": "SDF", "key_contest": "SKM vs SDF", "last_election_year": 2024,
        "last_winner_seats": "SKM 31 / SDF 1", "last_turnout": "79.9%",
        "next_election_due": "2029", "status": "not_due",
        "cm": "Prem Singh Tamang (SKM)", "capital": "Gangtok",
    },
    "Bihar": {
        "type": "State", "region": "East India", "phase": "Not in 2026 cycle",
        "polling_date": "Oct–Nov 2025 (done)", "counting_date": "Nov 10, 2025",
        "total_seats": 243, "ruling_party": "JD(U) + BJP (NDA)", "ruling_color": "#FF6B1A",
        "opposition": "RJD + INC (INDIA)", "key_contest": "NDA vs INDIA Alliance", "last_election_year": 2020,
        "last_winner_seats": "NDA 125 / RJD 75 / INC 19", "last_turnout": "57.1%",
        "next_election_due": "2025", "status": "not_due",
        "cm": "Nitish Kumar (JD-U)", "capital": "Patna",
    },
    "Delhi": {
        "type": "UT with Legislature", "region": "North India", "phase": "Elected Feb 2025",
        "polling_date": "Feb 5, 2025 (done)", "counting_date": "Feb 8, 2025",
        "total_seats": 70, "ruling_party": "BJP", "ruling_color": "#FF6B1A",
        "opposition": "AAP + INC", "key_contest": "BJP vs AAP", "last_election_year": 2025,
        "last_winner_seats": "BJP 48 / AAP 22", "last_turnout": "60.5%",
        "next_election_due": "2030", "status": "not_due",
        "cm": "Rekha Gupta (BJP)", "capital": "New Delhi",
    },
    "Nagaland": {
        "type": "State", "region": "Northeast India", "phase": "Not in 2026 cycle",
        "polling_date": "Feb 2023 (done)", "counting_date": "Mar 2, 2023",
        "total_seats": 60, "ruling_party": "NDPP + BJP", "ruling_color": "#FF6B1A",
        "opposition": "NPF + INC", "key_contest": "NDPP-BJP vs NPF", "last_election_year": 2023,
        "last_winner_seats": "NDPP 25 / BJP 12 / NPF 2", "last_turnout": "83.4%",
        "next_election_due": "2028", "status": "not_due",
        "cm": "Neiphiu Rio (NDPP)", "capital": "Kohima",
    },
    "Meghalaya": {
        "type": "State", "region": "Northeast India", "phase": "Not in 2026 cycle",
        "polling_date": "Feb 2023 (done)", "counting_date": "Mar 2, 2023",
        "total_seats": 60, "ruling_party": "NPP + BJP", "ruling_color": "#C084FC",
        "opposition": "INC + TMC", "key_contest": "NPP vs INC", "last_election_year": 2023,
        "last_winner_seats": "NPP 26 / INC 5 / BJP 2", "last_turnout": "85.9%",
        "next_election_due": "2028", "status": "not_due",
        "cm": "Conrad Sangma (NPP)", "capital": "Shillong",
    },
    "Tripura": {
        "type": "State", "region": "Northeast India", "phase": "Not in 2026 cycle",
        "polling_date": "Feb 2023 (done)", "counting_date": "Mar 2, 2023",
        "total_seats": 60, "ruling_party": "BJP + TIPRA Motha", "ruling_color": "#FF6B1A",
        "opposition": "CPI(M) + INC", "key_contest": "BJP vs CPI(M)", "last_election_year": 2023,
        "last_winner_seats": "BJP 32 / TIPRA 13 / CPI(M) 11", "last_turnout": "89.9%",
        "next_election_due": "2028", "status": "not_due",
        "cm": "Manik Saha (BJP)", "capital": "Agartala",
    },
    "Jammu & Kashmir": {
        "type": "UT with Legislature", "region": "North India", "phase": "Elected Sep–Oct 2024",
        "polling_date": "Sep–Oct 2024 (done)", "counting_date": "Oct 8, 2024",
        "total_seats": 90, "ruling_party": "NC + INC", "ruling_color": "#4F8EF7",
        "opposition": "BJP + PDP", "key_contest": "NC vs BJP", "last_election_year": 2024,
        "last_winner_seats": "NC 42 / BJP 29 / INC 6", "last_turnout": "63.9%",
        "next_election_due": "2029", "status": "not_due",
        "cm": "Omar Abdullah (NC)", "capital": "Srinagar / Jammu",
    },
    "Ladakh": {
        "type": "UT without Legislature", "region": "North India", "phase": "No Assembly",
        "polling_date": "Governed by Lt. Governor", "counting_date": "N/A",
        "total_seats": 0, "ruling_party": "Central Govt.", "ruling_color": "#5C6480",
        "opposition": "N/A", "key_contest": "N/A", "last_election_year": 0,
        "last_winner_seats": "No Legislative Assembly", "last_turnout": "N/A",
        "next_election_due": "N/A", "status": "no_assembly",
        "cm": "Lt. Governor", "capital": "Leh",
    },
    "Chandigarh": {
        "type": "UT without Legislature", "region": "North India", "phase": "No Assembly",
        "polling_date": "Municipal elections only", "counting_date": "N/A",
        "total_seats": 0, "ruling_party": "Central Govt.", "ruling_color": "#5C6480",
        "opposition": "N/A", "key_contest": "N/A", "last_election_year": 0,
        "last_winner_seats": "No Legislative Assembly", "last_turnout": "N/A",
        "next_election_due": "N/A", "status": "no_assembly",
        "cm": "Administrator (UT)", "capital": "Chandigarh",
    },
    "Dadra & Nagar Haveli and Daman & Diu": {
        "type": "UT without Legislature", "region": "West India", "phase": "No Assembly",
        "polling_date": "Governed by Administrator", "counting_date": "N/A",
        "total_seats": 0, "ruling_party": "Central Govt.", "ruling_color": "#5C6480",
        "opposition": "N/A", "key_contest": "N/A", "last_election_year": 0,
        "last_winner_seats": "No Legislative Assembly", "last_turnout": "N/A",
        "next_election_due": "N/A", "status": "no_assembly",
        "cm": "Administrator (UT)", "capital": "Daman",
    },
    "Lakshadweep": {
        "type": "UT without Legislature", "region": "South India", "phase": "No Assembly",
        "polling_date": "Governed by Administrator", "counting_date": "N/A",
        "total_seats": 0, "ruling_party": "Central Govt.", "ruling_color": "#5C6480",
        "opposition": "N/A", "key_contest": "N/A", "last_election_year": 0,
        "last_winner_seats": "No Legislative Assembly", "last_turnout": "N/A",
        "next_election_due": "N/A", "status": "no_assembly",
        "cm": "Administrator (UT)", "capital": "Kavaratti",
    },
    "Andaman & Nicobar Islands": {
        "type": "UT without Legislature", "region": "East India", "phase": "No Assembly",
        "polling_date": "Governed by Lt. Governor", "counting_date": "N/A",
        "total_seats": 0, "ruling_party": "Central Govt.", "ruling_color": "#5C6480",
        "opposition": "N/A", "key_contest": "N/A", "last_election_year": 0,
        "last_winner_seats": "No Legislative Assembly", "last_turnout": "N/A",
        "next_election_due": "N/A", "status": "no_assembly",
        "cm": "Lt. Governor (UT)", "capital": "Port Blair",
    },
}

STATUS_COLORS = {
    "completed":   "#27C96E",
    "upcoming":    "#4F8EF7",
    "not_due":     "#5C6480",
    "no_assembly": "#3A3F55",
}

STATUS_LABELS = {
    "completed":   "✅ Voted 2026",
    "upcoming":    "📅 Upcoming",
    "not_due":     "🗓️ Not in 2026",
    "no_assembly": "🏛️ No Assembly",
}

REGIONS = [
    "All Regions", "North India", "South India", "East India",
    "West India", "Central India", "Northeast India",
]


def _state_info_card(state: str) -> None:
    data = ALL_INDIA_DATA.get(state)
    if not data:
        st.warning(f"No data found for **{state}**.")
        return

    status_color = STATUS_COLORS.get(data["status"], "#5C6480")
    status_text  = STATUS_LABELS.get(data["status"], "—")
    rc = data["ruling_color"]
    is_no_assembly = data["status"] == "no_assembly"

    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#1C2030,#141720);
                    border-radius:16px;padding:22px;
                    border:1px solid rgba(255,255,255,0.08);border-top:5px solid {rc};
                    box-shadow:0 4px 20px rgba(0,0,0,0.4);">

            <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:18px;">
                <div style="flex:1;">
                    <div style="font-weight:800;font-size:1.2rem;color:#E8EAF0;">
                        🗳️ {sanitize_text(state)}
                    </div>
                    <div style="color:#9BA3BC;font-size:0.82rem;margin-top:4px;">
                        {sanitize_text(data['type'])} · {sanitize_text(data['region'])} ·
                        Capital: {sanitize_text(data['capital'])}
                    </div>
                    {f'<div style="color:#9BA3BC;font-size:0.82rem;margin-top:2px;">CM: <b style="color:#E8EAF0;">{sanitize_text(data["cm"])}</b></div>' if not is_no_assembly else ''}
                </div>
                <div style="background:{status_color}22;border:1px solid {status_color}44;
                             color:{status_color};font-weight:700;font-size:0.8rem;
                             padding:6px 14px;border-radius:20px;white-space:nowrap;">
                    {status_text}
                </div>
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr{'  1fr  1fr' if not is_no_assembly else ''};gap:10px;">
                {"" if is_no_assembly else f'''
                <div style="background:#242840;border-radius:10px;padding:12px;">
                    <div style="font-size:0.7rem;color:#5C6480;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Assembly Seats</div>
                    <div style="font-weight:700;color:#E8EAF0;font-size:0.95rem;margin-top:4px;">{data["total_seats"]}</div>
                </div>
                <div style="background:#242840;border-radius:10px;padding:12px;">
                    <div style="font-size:0.7rem;color:#5C6480;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Ruling Party</div>
                    <div style="font-weight:700;font-size:0.88rem;margin-top:4px;color:{rc};">{sanitize_text(data["ruling_party"])}</div>
                </div>
                <div style="background:#242840;border-radius:10px;padding:12px;">
                    <div style="font-size:0.7rem;color:#5C6480;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Last Election</div>
                    <div style="font-weight:700;color:#E8EAF0;font-size:0.88rem;margin-top:4px;">{data["last_election_year"] if data["last_election_year"] else "N/A"}</div>
                </div>
                <div style="background:#242840;border-radius:10px;padding:12px;">
                    <div style="font-size:0.7rem;color:#5C6480;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Turnout</div>
                    <div style="font-weight:700;color:#E8EAF0;font-size:0.88rem;margin-top:4px;">{sanitize_text(data["last_turnout"])}</div>
                </div>
                '''}
                <div style="background:#242840;border-radius:10px;padding:12px;">
                    <div style="font-size:0.7rem;color:#5C6480;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Polling Date</div>
                    <div style="font-weight:700;color:#E8EAF0;font-size:0.82rem;margin-top:4px;">{sanitize_text(data["polling_date"])}</div>
                </div>
                <div style="background:#242840;border-radius:10px;padding:12px;">
                    <div style="font-size:0.7rem;color:#5C6480;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Next Due</div>
                    <div style="font-weight:700;color:#E8EAF0;font-size:0.88rem;margin-top:4px;">{sanitize_text(data["next_election_due"])}</div>
                </div>
            </div>

            {"" if is_no_assembly else f'''
            <div style="margin-top:14px;background:#242840;border-radius:10px;padding:12px;">
                <div style="font-size:0.7rem;color:#5C6480;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">
                    Last Result ({data["last_election_year"]})
                </div>
                <div style="font-size:0.85rem;color:#E8EAF0;font-weight:600;">{sanitize_text(data["last_winner_seats"])}</div>
                <div style="font-size:0.78rem;color:#9BA3BC;margin-top:4px;">Key contest: {sanitize_text(data["key_contest"])}</div>
            </div>
            '''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_india_map() -> None:
    st.markdown("### 🗺️ India Election Map — All States & Union Territories")
    st.caption(
        "Complete data for all 28 States + 8 Union Territories · "
        "Ruling party, last results, assembly seats, and 2026 election status."
    )

    total_states = len([v for v in ALL_INDIA_DATA.values() if v["type"] == "State"])
    voting_2026  = len([v for v in ALL_INDIA_DATA.values() if v["status"] == "completed"])
    bjp_states   = len([v for v in ALL_INDIA_DATA.values() if "BJP" in v["ruling_party"] and v["status"] != "no_assembly"])
    inc_states   = len([v for v in ALL_INDIA_DATA.values() if "INC" in v["ruling_party"] and v["status"] != "no_assembly"])

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Total States", total_states)
    with m2: st.metric("Voted in 2026", voting_2026, help="States/UTs with 2026 elections")
    with m3: st.metric("BJP-led Govts", bjp_states, help="States/UTs where BJP leads coalition")
    with m4: st.metric("INC-led Govts", inc_states, help="States/UTs where INC leads coalition")

    st.divider()

    col_search, col_region, col_status = st.columns([2, 1.5, 1.5])
    with col_search:
        search = st.text_input(
            "🔍 Search state, UT or capital",
            placeholder="e.g. Mumbai, Bihar, Patna...",
            key="map_search",
        )
    with col_region:
        region_filter = st.selectbox("📍 Region", REGIONS, key="map_region")
    with col_status:
        status_filter = st.selectbox(
            "🗳️ Election Status",
            ["All", "Voted in 2026", "Not in 2026", "No Assembly"],
            key="map_status",
        )

    all_names = sorted(ALL_INDIA_DATA.keys())
    selected_state = st.selectbox(
        "🏛️ Select State / UT for full details",
        ["— Select to view details —"] + all_names,
        key="india_map_state_select",
    )

    if selected_state and selected_state != "— Select to view details —":
        st.markdown("")
        _state_info_card(selected_state)
        st.divider()

    # ── Legend ─────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:16px;">
            <span style="display:flex;align-items:center;gap:6px;font-size:0.78rem;color:#9BA3BC;">
                <span style="background:#27C96E;border-radius:4px;width:14px;height:14px;display:inline-block;"></span>
                Voted in 2026
            </span>
            <span style="display:flex;align-items:center;gap:6px;font-size:0.78rem;color:#9BA3BC;">
                <span style="background:#5C6480;border-radius:4px;width:14px;height:14px;display:inline-block;"></span>
                Not in 2026 Cycle
            </span>
            <span style="display:flex;align-items:center;gap:6px;font-size:0.78rem;color:#9BA3BC;">
                <span style="background:#3A3F55;border-radius:4px;width:14px;height:14px;display:inline-block;"></span>
                No Legislative Assembly
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    status_map = {
        "Voted in 2026": "completed",
        "Not in 2026":   "not_due",
        "No Assembly":   "no_assembly",
    }

    filtered = {}
    for name, data in ALL_INDIA_DATA.items():
        if search and search.lower() not in name.lower() and search.lower() not in data.get("capital", "").lower():
            continue
        if region_filter != "All Regions" and data.get("region") != region_filter:
            continue
        if status_filter != "All" and data.get("status") != status_map.get(status_filter):
            continue
        filtered[name] = data

    # ... (code above)
    st.markdown(f"#### 📋 Showing {len(filtered)} of {len(ALL_INDIA_DATA)} states/UTs")

    cols = st.columns(3)
    # Ensure this 'for' is at the same indentation level as 'cols ='
    for i, (state, data) in enumerate(sorted(filtered.items())):
        with cols[i % 3]:
            sc = STATUS_COLORS.get(data["status"], "#5C6480")
            sl = STATUS_LABELS.get(data["status"], "—")
            rc = data["ruling_color"]
            is_no_asm = data["status"] == "no_assembly"

            # 1. Build the HTML pieces conditionally
            party_html = (
                f'''<div style="margin:8px 0 4px;">
                    <span style="background:{rc}22;color:{rc};font-size:0.7rem;font-weight:700;padding:2px 8px;border-radius:20px;border:1px solid {rc}33;">
                    {sanitize_text(data["ruling_party"])}</span></div>'''
                if not is_no_asm else ""
            )

            next_html = (
                f'<div style="font-size:0.7rem;color:#5C6480;margin-top:6px;">Next: {sanitize_text(data["next_election_due"])}</div>'
                if not is_no_asm else ""
            )

            # 2. Assemble everything into ONE single string
            card_html = f"""
            <div style="background:#1C2030;border-radius:12px;padding:14px;
                        border:1px solid rgba(255,255,255,0.07);border-left:5px solid {rc};
                        margin-bottom:10px;box-shadow:0 1px 6px rgba(0,0,0,0.3);
                        min-height: {'90px' if is_no_asm else '130px'};">
                <div style="font-weight:700;color:#E8EAF0;font-size:0.9rem;">{sanitize_text(state)}</div>
                <div style="font-size:0.72rem;color:#5C6480;margin-top:2px;">{sanitize_text(data['type'])} · {sanitize_text(data['capital'])}</div>
                {party_html}
                <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-top:4px;">
                    <span style="background:{sc}22;color:{sc};font-size:0.68rem;font-weight:700;padding:2px 8px;border-radius:20px;border:1px solid {sc}44;">
                    {sl}</span>
                    <span style="font-size:0.68rem;color:#5C6480;">{data["total_seats"]} seats</span>
                </div>
                {next_html}
            </div>
            """

            # 3. Render the entire card in one go
            st.markdown(card_html, unsafe_allow_html=True)
            
    st.divider()
    # ... (rest of code)
            
    st.link_button(
        "📅 Full Election Schedule on ECI Website →",
        "https://eci.gov.in/elections/",
        use_container_width=True,
    )
