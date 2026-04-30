"""
CivicPulse — Exit Poll Aggregator Component
==========================================
Collects and averages multiple exit poll predictions.
"""

from __future__ import annotations
import streamlit as st

# ── Sample exit polls ──────────────────────────────────────────────────────────
DEFAULT_EXIT_POLLS = [
    {
        "agency": "ABP News - CVoter",
        "date": "29 April 2026",
        "aitc": 160,
        "bjp": 105,
        "left_others": 29,
        "source": "https://abpnews.in",
    },
    {
        "agency": "India Today - Axis My India",
        "date": "29 April 2026",
        "aitc": 152,
        "bjp": 118,
        "left_others": 24,
        "source": "https://indiatoday.in",
    },
    {
        "agency": "Republic TV - P-MARQ",
        "date": "29 April 2026",
        "aitc": 138,
        "bjp": 129,
        "left_others": 27,
        "source": "https://republicworld.com",
    },
    {
        "agency": "Times Now - ETG",
        "date": "29 April 2026",
        "aitc": 168,
        "bjp": 98,
        "left_others": 28,
        "source": "https://timesnow.com",
    },
]

PARTY_COLORS = {
    "aitc": "#00843D",
    "bjp": "#FF6600",
    "left_others": "#999999",
}

TOTAL_SEATS = 294
MAJORITY = 148


def _avg(polls: list[dict], key: str) -> float:
    return sum(p.get(key, 0) for p in polls) / len(polls) if polls else 0


def _mini_bar(aitc: int, bjp: int, others: int, total: int = 294) -> str:
    aitc_w  = (aitc / total) * 100
    bjp_w   = (bjp / total) * 100
    oth_w   = (others / total) * 100
    maj_pct = (MAJORITY / total) * 100
    return (
        f'<div style="position:relative;background:#E8E4DC;border-radius:6px;height:18px;overflow:visible;margin:6px 0;">'
        f'<div style="width:{aitc_w:.1f}%;background:#00843D;height:100%;display:inline-block;border-radius:6px 0 0 6px;"></div>'
        f'<div style="width:{bjp_w:.1f}%;background:#FF6600;height:100%;display:inline-block;"></div>'
        f'<div style="width:{oth_w:.1f}%;background:#AAAAAA;height:100%;display:inline-block;border-radius:0 6px 6px 0;"></div>'
        f'<div style="position:absolute;top:-4px;left:{maj_pct:.1f}%;border-left:2px dashed #C62828;height:26px;"></div>'
        f'</div>'
    )


def render_exit_poll_aggregator() -> None:
    """Render exit poll aggregator with editable poll table."""
    st.markdown("### 📡 Exit Poll Aggregator")
    st.caption(
        "Average of multiple agency predictions. Add your own poll data below. "
        "Exit polls are estimates only — actual results may differ significantly."
    )

    # ── Warning banner ─────────────────────────────────────────────────────────
    st.warning(
        "⚠️ **Disclaimer:** Exit polls are projections, not results. Indian exit polls "
        "have historically had significant margins of error. Actual counting is on **May 4, 2026**."
    )

    # ── Session state for editable polls ──────────────────────────────────────
    if "exit_polls" not in st.session_state:
        st.session_state["exit_polls"] = [p.copy() for p in DEFAULT_EXIT_POLLS]

    polls = st.session_state["exit_polls"]

    # ── Aggregated average ─────────────────────────────────────────────────────
    avg_aitc   = round(_avg(polls, "aitc"))
    avg_bjp    = round(_avg(polls, "bjp"))
    avg_others = TOTAL_SEATS - avg_aitc - avg_bjp

    st.markdown("#### 🧮 Aggregated Average")
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#F0FAF0,#FFFFFF);
                    border-radius:16px;padding:20px;border:1px solid #E8E4DC;
                    box-shadow:0 4px 12px rgba(0,0,0,0.06);margin-bottom:1rem;">
            <div style="display:flex;gap:16px;text-align:center;margin-bottom:12px;">
                <div style="flex:1;background:#00843D18;border-radius:10px;padding:12px;border:1px solid #00843D44;">
                    <div style="font-weight:800;font-size:2rem;color:#00843D;">{avg_aitc}</div>
                    <div style="font-size:0.78rem;color:#5C5C7A;font-weight:600;">AITC (Avg)</div>
                    {'<div style="font-size:0.7rem;background:#E8F5E6;color:#0E6B06;padding:2px 8px;border-radius:20px;margin-top:4px;font-weight:700;">🏆 MAJORITY</div>' if avg_aitc >= MAJORITY else ''}
                </div>
                <div style="flex:1;background:#FF660018;border-radius:10px;padding:12px;border:1px solid #FF660044;">
                    <div style="font-weight:800;font-size:2rem;color:#FF6600;">{avg_bjp}</div>
                    <div style="font-size:0.78rem;color:#5C5C7A;font-weight:600;">BJP (Avg)</div>
                </div>
                <div style="flex:1;background:#99999918;border-radius:10px;padding:12px;border:1px solid #99999944;">
                    <div style="font-weight:800;font-size:2rem;color:#666;">{avg_others}</div>
                    <div style="font-size:0.78rem;color:#5C5C7A;font-weight:600;">Others (Avg)</div>
                </div>
            </div>
            {_mini_bar(avg_aitc, avg_bjp, avg_others)}
            <div style="font-size:0.72rem;color:#9090A8;text-align:center;margin-top:4px;">
                ─── Majority mark: {MAJORITY} seats ───
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Individual polls table ─────────────────────────────────────────────────
    st.markdown("#### 📋 Individual Poll Predictions")

    for i, poll in enumerate(polls):
        with st.expander(f"📊 {poll['agency']} · {poll['date']}", expanded=i == 0):
            c1, c2, c3 = st.columns(3)
            with c1:
                polls[i]["aitc"] = st.number_input(
                    "AITC Seats",
                    min_value=0, max_value=TOTAL_SEATS,
                    value=poll["aitc"],
                    key=f"poll_{i}_aitc",
                )
            with c2:
                polls[i]["bjp"] = st.number_input(
                    "BJP Seats",
                    min_value=0, max_value=TOTAL_SEATS,
                    value=poll["bjp"],
                    key=f"poll_{i}_bjp",
                )
            with c3:
                others = TOTAL_SEATS - polls[i]["aitc"] - polls[i]["bjp"]
                st.metric("Others (auto)", max(0, others))

            st.markdown(
                _mini_bar(polls[i]["aitc"], polls[i]["bjp"], max(0, others)),
                unsafe_allow_html=True,
            )
            st.link_button(f"🔗 Source: {poll['agency']}", poll["source"])

    st.divider()

    # ── Add new poll ───────────────────────────────────────────────────────────
    st.markdown("#### ➕ Add Your Own Poll Data")
    with st.expander("Add a new exit poll entry"):
        na, nb, nc = st.columns(3)
        with na:
            new_agency = st.text_input("Agency Name", key="new_poll_agency")
        with nb:
            new_aitc = st.number_input("AITC Seats", min_value=0, max_value=294, value=150, key="new_poll_aitc")
        with nc:
            new_bjp  = st.number_input("BJP Seats", min_value=0, max_value=294, value=100, key="new_poll_bjp")
        if st.button("Add Poll", type="primary", key="add_poll_btn"):
            if new_agency.strip():
                polls.append({
                    "agency": new_agency.strip(),
                    "date": "User Added",
                    "aitc": new_aitc,
                    "bjp": new_bjp,
                    "left_others": max(0, TOTAL_SEATS - new_aitc - new_bjp),
                    "source": "https://eci.gov.in",
                })
                st.session_state["exit_polls"] = polls
                st.success(f"Added poll from '{new_agency}'!")
                st.rerun()
            else:
                st.error("Please enter an agency name.")
