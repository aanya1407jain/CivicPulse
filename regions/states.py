"""
India State-by-State Election Data
Data reflects the 2026 Assembly Election cycle and 2029 General Election defaults.
"""

# We use ISO codes for Indian States (e.g., TN for Tamil Nadu, WB for West Bengal)
INDIA_STATE_DATA: dict[str, dict] = {
    "TN": {
        "name": "Tamil Nadu",
        "election_type": "Legislative Assembly",
        "poll_date": "April 23, 2026",
        "counting_day": "May 4, 2026",
        "total_seats": 234,
        "voter_turnout_2021": "72.81%",
        "dry_day_start": "April 21, 2026",
        "election_authority": "Chief Electoral Officer, Tamil Nadu",
        "official_url": "https://www.elections.tn.gov.in/",
    },
    "WB": {
        "name": "West Bengal",
        "election_type": "Legislative Assembly",
        "phases": 2,
        "poll_date": "Phase 1: April 23 | Phase 2: April 29, 2026",
        "counting_day": "May 4, 2026",
        "total_seats": 294,
        "voter_turnout_2021": "81.76%",
        "election_authority": "Chief Electoral Officer, West Bengal",
        "official_url": "https://ceowestbengal.nic.in/",
    },
    "KL": {
        "name": "Kerala",
        "election_type": "Legislative Assembly",
        "poll_date": "April 9, 2026",
        "counting_day": "May 4, 2026",
        "total_seats": 140,
        "voter_turnout_2021": "74.06%",
        "election_authority": "Chief Electoral Officer, Kerala",
        "official_url": "https://www.ceo.kerala.gov.in/",
    },
    "AS": {
        "name": "Assam",
        "election_type": "Legislative Assembly",
        "poll_date": "April 9, 2026",
        "counting_day": "May 4, 2026",
        "total_seats": 126,
        "voter_turnout_2021": "82.04%",
        "election_authority": "Chief Electoral Officer, Assam",
        "official_url": "https://ceoassam.nic.in/",
    },
    "PY": {
        "name": "Puducherry",
        "election_type": "Legislative Assembly",
        "poll_date": "April 9, 2026",
        "counting_day": "May 4, 2026",
        "total_seats": 30,
        "election_authority": "Chief Electoral Officer, Puducherry",
        "official_url": "https://ceopuducherry.py.gov.in/",
    },
    "DEFAULT": {
        "name": "India (General)",
        "election_type": "Lok Sabha / General",
        "poll_date": "May 2029 (Expected)",
        "counting_day": "June 2029 (Expected)",
        "total_seats": 543,
        "reg_deadline": "Ongoing (Form 6)",
        "voter_id_required": True,
        "election_authority": "Election Commission of India (ECI)",
        "official_url": "https://eci.gov.in/",
    },
}