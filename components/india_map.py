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
        "phase": "Phase I & II Complete",
        "polling_date": "April 17 & 29, 2026",
        "counting_date": "May 4, 2026",
        "total_seats": 294,
        "ruling_party": "AITC",
        "ruling_color": "#00843D",
        "key_contest": "AITC vs BJP",
        "turnout_2021": "82.2%",
        "status": "completed",
    },
    "Assam": {
        "phase": "Phase I Complete",
        "polling_date": "April 5, 2026",
        "counting_date": "May 4, 2026",
        "total_seats": 126,
        "ruling_party": "BJP",
        "ruling_color": "#FF6600",
        "key_contest": "BJP vs INC-BPF Alliance",
        "turnout_2021": "82.5%",
        "status": "completed",
    },
    "Kerala": {
        "phase": "Single Phase",
        "polling_date": "April 12, 2026",
        "counting_date": "May 4, 2026",
        "total_seats": 140,
        "ruling_party": "CPI(M) - LDF",
        "ruling_color": "#CC0000",
        "key_contest": "LDF vs UDF",
        "turnout_2021": "74.6%",
        "status": "completed",
    },
    "Tamil Nadu": {
        "phase": "Single Phase",
        "polling_date": "April 19, 2026",
        "counting_date": "May 4, 2026",
        "total_seats": 234,
        "ruling_party": "DMK",
        "ruling_color": "#CC0000",
        "key_contest": "DMK Alliance vs AIADMK",
        "turnout_2021": "74.2%",
        "status": "completed",
    },
    "Puducherry": {
        "phase": "Single Phase",
        "polling_date": "April 19, 2026",
        "counting_date": "May 4, 2026",
        "total_seats": 30,
        "ruling_party": "NR Congress-BJP",
        "ruling_color": "#FF6600",
        "key_contest": "NR Congress vs DMK-INC",
        "turnout_2021": "77.3%",
        "status": "completed",
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
