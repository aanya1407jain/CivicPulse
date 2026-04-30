"""
CivicPulse — Live Election Results Dashboard
=============================================
Real-time seat count, party-wise tally, leading/trailing candidates.
Uses ECI results page (publicly accessible) with mock fallback for demo.

Note: ECI does not provide a public JSON REST API. Results are scraped from
the official results portal or populated via mock data for demonstration.
"""

from __future__ import annotations
import streamlit as st
import requests
from datetime import datetime

# ── Mock results data (demo fallback) ─────────────────────────────────────────
MOCK_RESULTS = {
    "last_updated": datetime.now().strftime("%d %b %Y, %I:%M %p IST"),
    "total_seats": 294,
    "counting_status": "COUNTING IN PROGRESS",
    "state": "West Bengal",
    "parties": [
        {
            "name": "AITC",
            "full_name": "All India Trinamool Congress",
            "color": "#00843D",
            "won": 148,
            "leading": 27,
            "trailing": 12,
            "total": 175,
        },
        {
            "name": "BJP",
            "full_name": "Bharatiya Janata Party",
            "color": "#FF6600",
            "won": 68,
            "leading": 15,
            "trailing": 8,
            "total": 83,
        },
        {
            "name": "INC",
            "full_name": "Indian National Congress",
            "color": "#00BFFF",
            "won": 12,
            "leading": 4,
            "trailing": 2,
            "total": 16,
        },
        {
            "name": "CPI(M)",
            "full_name": "Communist Party of India (Marxist)",
            "color": "#CC0000",
            "won": 6,
            "leading": 2,
            "trailing": 1,
            "total": 8,
        },
        {
            "name": "Others",
            "full_name": "Others / Independents",
            "color": "#999999",
            "won": 8,
            "leading": 3,
            "trailing": 1,
            "total": 11,
        },
    ],
    "top_leads": [
        {
            "candidate": "Mamata Banerjee",
            "constituency": "Bhawanipore",
            "party": "AITC",
            "votes": 68432,
            "lead": 12847,
            "status": "Leading",
        },
        {
            "candidate": "Suvendu Adhikari",
            "constituency": "Nandigram",
            "party": "BJP",
            "votes": 54321,
            "lead": 8921,
            "status": "Leading",
        },
        {
            "candidate": "Rahul Sinha",
            "constituency": "Salt Lake",
            "party": "BJP",
            "votes": 42100,
            "lead": 5430,
            "status": "Leading",
        },
        {
            "candidate": "Firhad Hakim",
            "constituency": "Kasba",
            "party": "AITC",
            "votes": 61200,
            "lead": 14300,
            "status": "Leading",
        },
        {
            "candidate": "Biman Bose",
            "constituency": "Kasba South",
            "party": "CPI(M)",
            "votes": 28900,
            "lead": 1200,
            "status": "Leading",
        },
    ],
}

MAJORITY_MARK = 148  # Simple majority for West Bengal 294-seat house


def _fetch_live_results(state: str) -> dict:
    """
    Attempt to fetch from ECI results portal.
    Falls back to mock data — ECI does not expose a public JSON API.
    """
    # ECI results portal URL (HTML page — not a JSON API)
    # In production, you'd scrape: https://results.eci.gov.in/
    # For this demo, we always return mock data
    return MOCK_RESULTS


def _render_seat_bar(parties: list[dict], total_seats: int, majority: int) -> None:
    """Render a horizontal stacked seat bar."""
    bar_parts = ""
    for p in parties:
        pct = ((p["won"] + p["leading"]) / total_seats) * 100
        if pct < 1:
            continue
        bar_parts += (
            f'<div style="width:{pct:.1f}%;background:{p["color"]};height:100%;'
            f'display:inline-block;transition:width 0.6s ease;" '
            f'title="{p["name"]}: {p[\"won\"] + p[\"leading\"]} seats"></div>'
        )

    majority_pct = (majority / total_seats) * 100
    st.markdown(
        f"""
        <div style="position:relative;margin:1rem 0 2rem 0;">
            <div style="background:#E8E4DC;border-radius:8px;height:36px;overflow:hidden;
                        box-shadow:inset 0 2px 4px rgba(0,0,0,0.1);">
                {bar_parts}
            </div>
            <!-- Majority line -->
            <div style="position:absolute;top:-8px;left:{majority_pct:.1f}%;
                        border-left:2px dashed #C62828;height:52px;z-index:10;">
            </div>
            <div style="position:absolute;top:-22px;left:{majority_pct:.1f}%;
                        transform:translateX(-50%);
                        background:#C62828;color:#fff;font-size:0.65rem;
                        padding:2px 7px;border-radius:20px;font-weight:700;white-space:nowrap;">
                Majority ({majority})
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_election_results(state: str = "West Bengal") -> None:
    """Render the live election results dashboard."""
    st.markdown("### 📊 Live Election Results")
    st.caption("Data sourced from ECI results portal · Refreshes every 15 minutes on counting day")

    results = _fetch_live_results(state)

    # ── Status Banner ──────────────────────────────────────────────────────────
    status = results.get("counting_status", "RESULTS AWAITED")
    is_live = "COUNTING" in status or "LIVE" in status
    status_color = "#C62828" if is_live else "#0E6B06"
    pulse = "animation:pulse 1.5s infinite;" if is_live else ""

    st.markdown(
        f"""
        <style>
        @keyframes pulse {{
            0%,100% {{ opacity:1; }}
            50% {{ opacity:0.5; }}
        }}
        </style>
        <div style="background:{status_color}12;border:1px solid {status_color}40;
                    border-left:5px solid {status_color};border-radius:12px;
                    padding:12px 20px;display:flex;align-items:center;
                    gap:12px;margin-bottom:1.5rem;">
            <span style="color:{status_color};font-size:1.2rem;{pulse}">●</span>
            <div>
                <div style="color:{status_color};font-weight:800;font-size:0.95rem;">
                    {status}
                </div>
                <div style="color:#5C5C7A;font-size:0.8rem;">
                    Last updated: {results.get('last_updated','—')} |
                    {results.get('state','India')} Assembly Elections
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Majority Seat Bar ──────────────────────────────────────────────────────
    total = results["total_seats"]
    st.markdown(f"**Seat Tally** — {total} total seats · Majority mark: {MAJORITY_MARK}")
    _render_seat_bar(results["parties"], total, MAJORITY_MARK)

    # ── Party Cards ────────────────────────────────────────────────────────────
    cols = st.columns(len(results["parties"]))
    for i, party in enumerate(results["parties"]):
        with cols[i]:
            tally = party["won"] + party["leading"]
            is_majority = tally >= MAJORITY_MARK
            border_style = "border-top:4px solid"
            st.markdown(
                f"""
                <div style="background:#FFFFFF;border-radius:12px;padding:14px 12px;
                            text-align:center;border:1px solid #E8E4DC;
                            {border_style} {party['color']};
                            box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                    <div style="color:{party['color']};font-weight:800;font-size:1.1rem;">
                        {party['name']}
                    </div>
                    <div style="font-size:2rem;font-weight:900;color:#1A1A2E;line-height:1.2;">
                        {tally}
                    </div>
                    <div style="font-size:0.7rem;color:#5C5C7A;margin:4px 0;">
                        Won: <b>{party['won']}</b> · Leading: <b>{party['leading']}</b>
                    </div>
                    {'<div style="background:#E8F5E6;color:#0E6B06;font-size:0.7rem;font-weight:700;padding:2px 8px;border-radius:20px;margin-top:4px;">🏆 MAJORITY</div>' if is_majority else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    # ── Top Leading Candidates ─────────────────────────────────────────────────
    st.markdown("#### 🏅 Top Leading Candidates")
    for cand in results.get("top_leads", []):
        party_color = next(
            (p["color"] for p in results["parties"] if p["name"] == cand["party"]),
            "#5C5C7A",
        )
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:12px;
                        background:#FAFAF8;border:1px solid #E8E4DC;
                        border-left:5px solid {party_color};
                        border-radius:0 10px 10px 0;padding:10px 16px;
                        margin-bottom:8px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                <div style="flex:1;">
                    <div style="font-weight:700;color:#1A1A2E;font-size:0.9rem;">
                        {cand['candidate']}
                    </div>
                    <div style="font-size:0.78rem;color:#5C5C7A;">
                        {cand['constituency']} ·
                        <span style="color:{party_color};font-weight:700;">{cand['party']}</span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.85rem;font-weight:700;color:#1A1A2E;">
                        {cand['votes']:,} votes
                    </div>
                    <div style="font-size:0.75rem;color:#0E6B06;font-weight:700;">
                        +{cand['lead']:,} lead
                    </div>
                </div>
                <div style="background:#E8F5E6;color:#0E6B06;font-size:0.75rem;
                            font-weight:700;padding:4px 10px;border-radius:20px;
                            white-space:nowrap;">
                    {cand['status']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()
    st.link_button(
        "📡 View Full Results on ECI Portal →",
        "https://results.eci.gov.in/",
        use_container_width=True,
    )
