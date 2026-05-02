"""
CivicPulse — Exit Poll Aggregator Component
"""

from __future__ import annotations
import streamlit as st
from components.language_selector import T

DEFAULT_EXIT_POLLS = [
    {"agency": "ABP News - CVoter",          "date": "29 April 2026", "aitc": 160, "bjp": 105, "left_others": 29,  "source": "https://abpnews.in"},
    {"agency": "India Today - Axis My India", "date": "29 April 2026", "aitc": 152, "bjp": 118, "left_others": 24,  "source": "https://indiatoday.in"},
    {"agency": "Republic TV - P-MARQ",        "date": "29 April 2026", "aitc": 138, "bjp": 129, "left_others": 27,  "source": "https://republicworld.com"},
    {"agency": "Times Now - ETG",             "date": "29 April 2026", "aitc": 168, "bjp": 98,  "left_others": 28,  "source": "https://timesnow.com"},
]

PARTY_COLORS = {"aitc": "#00843D", "bjp": "#FF6600", "left_others": "#999999"}
TOTAL_SEATS = 294
MAJORITY    = 148


def _avg(polls: list[dict], key: str) -> float:
    return sum(p.get(key, 0) for p in polls) / len(polls) if polls else 0


def _mini_bar(aitc: int, bjp: int, others: int, total: int = 294) -> str:
    aitc_w  = (aitc / total) * 100
    bjp_w   = (bjp / total) * 100
    oth_w   = (others / total) * 100
    maj_pct = (MAJORITY / total) * 100
    return (
        f'<div style="position:relative;background:#242840;border-radius:6px;height:18px;overflow:visible;margin:6px 0;">'
        f'<div style="width:{aitc_w:.1f}%;background:#00843D;height:100%;display:inline-block;border-radius:6px 0 0 6px;"></div>'
        f'<div style="width:{bjp_w:.1f}%;background:#FF6600;height:100%;display:inline-block;"></div>'
        f'<div style="width:{oth_w:.1f}%;background:#AAAAAA;height:100%;display:inline-block;border-radius:0 6px 6px 0;"></div>'
        f'<div style="position:absolute;top:-4px;left:{maj_pct:.1f}%;border-left:2px dashed #C62828;height:26px;"></div>'
        f'</div>'
    )


def render_exit_poll_aggregator() -> None:
    st.markdown(f"### 📡 {T('Exit Poll Aggregator')}")
    st.caption(T("Average of multiple agency predictions. Add your own poll data below. Exit polls are estimates only — actual results may differ significantly."))

    disclaimer = T("Exit polls are projections, not results. Indian exit polls have historically had significant margins of error. Actual counting is on May 4, 2026.")
    st.warning(f"⚠️ **{T('Disclaimer')}:** {disclaimer}")

    if "exit_polls" not in st.session_state:
        st.session_state["exit_polls"] = [p.copy() for p in DEFAULT_EXIT_POLLS]

    polls = st.session_state["exit_polls"]

    avg_aitc   = round(_avg(polls, "aitc"))
    avg_bjp    = round(_avg(polls, "bjp"))
    avg_others = TOTAL_SEATS - avg_aitc - avg_bjp

    majority_text  = T("MAJORITY")
    majority_mark  = T("Majority mark")
    aggregated_avg = T("Aggregated Average")
    others_label   = T("Others")

    st.markdown(f"#### 🧮 {aggregated_avg}")
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#1C2030,#141720);
                    border-radius:16px;padding:20px;border:1px solid rgba(255,255,255,0.08);
                    box-shadow:0 4px 12px rgba(0,0,0,0.06);margin-bottom:1rem;">
            <div style="display:flex;gap:16px;text-align:center;margin-bottom:12px;">
                <div style="flex:1;background:#00843D18;border-radius:10px;padding:12px;border:1px solid #00843D44;">
                    <div style="font-weight:800;font-size:2rem;color:#00843D;">{avg_aitc}</div>
                    <div style="font-size:0.78rem;color:#9BA3BC;font-weight:600;">AITC ({T('Avg')})</div>
                    {'<div style="font-size:0.7rem;background:rgba(39,201,110,0.12);color:#27C96E;padding:2px 8px;border-radius:20px;margin-top:4px;font-weight:700;">🏆 ' + majority_text + '</div>' if avg_aitc >= MAJORITY else ''}
                </div>
                <div style="flex:1;background:#FF660018;border-radius:10px;padding:12px;border:1px solid #FF660044;">
                    <div style="font-weight:800;font-size:2rem;color:#FF6600;">{avg_bjp}</div>
                    <div style="font-size:0.78rem;color:#9BA3BC;font-weight:600;">BJP ({T('Avg')})</div>
                </div>
                <div style="flex:1;background:#9BA3BC18;border-radius:10px;padding:12px;border:1px solid #9BA3BC44;">
                    <div style="font-weight:800;font-size:2rem;color:#9BA3BC;">{avg_others}</div>
                    <div style="font-size:0.78rem;color:#9BA3BC;font-weight:600;">{others_label} ({T('Avg')})</div>
                </div>
            </div>
            {_mini_bar(avg_aitc, avg_bjp, avg_others)}
            <div style="font-size:0.72rem;color:#5C6480;text-align:center;margin-top:4px;">
                ─── {majority_mark}: {MAJORITY} {T('seats')} ───
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    individual_polls = T("Individual Poll Predictions")
    st.markdown(f"#### 📋 {individual_polls}")

    aitc_seats_label = T("AITC Seats")
    bjp_seats_label  = T("BJP Seats")
    others_auto      = T("Others (auto)")
    source_label     = T("Source")

    for i, poll in enumerate(polls):
        with st.expander(f"📊 {poll['agency']} · {poll['date']}", expanded=i == 0):
            c1, c2, c3 = st.columns(3)
            with c1:
                polls[i]["aitc"] = st.number_input(aitc_seats_label, min_value=0, max_value=TOTAL_SEATS, value=poll["aitc"], key=f"poll_{i}_aitc")
            with c2:
                polls[i]["bjp"]  = st.number_input(bjp_seats_label,  min_value=0, max_value=TOTAL_SEATS, value=poll["bjp"],  key=f"poll_{i}_bjp")
            with c3:
                others = TOTAL_SEATS - polls[i]["aitc"] - polls[i]["bjp"]
                st.metric(others_auto, max(0, others))
            st.markdown(_mini_bar(polls[i]["aitc"], polls[i]["bjp"], max(0, others)), unsafe_allow_html=True)
            st.link_button(f"🔗 {source_label}: {poll['agency']}", poll["source"])

    st.divider()

    add_poll_title  = T("Add Your Own Poll Data")
    add_entry_label = T("Add a new exit poll entry")
    agency_label    = T("Agency Name")
    add_poll_btn    = T("Add Poll")
    added_msg       = T("Added poll from")
    enter_agency    = T("Please enter an agency name.")

    st.markdown(f"#### ➕ {add_poll_title}")
    with st.expander(add_entry_label):
        na, nb, nc = st.columns(3)
        with na:
            new_agency = st.text_input(agency_label, key="new_poll_agency")
        with nb:
            new_aitc = st.number_input(aitc_seats_label, min_value=0, max_value=294, value=150, key="new_poll_aitc")
        with nc:
            new_bjp  = st.number_input(bjp_seats_label,  min_value=0, max_value=294, value=100, key="new_poll_bjp")
        if st.button(add_poll_btn, type="primary", key="add_poll_btn"):
            if new_agency.strip():
                polls.append({
                    "agency": new_agency.strip(),
                    "date": T("User Added"),
                    "aitc": new_aitc,
                    "bjp": new_bjp,
                    "left_others": max(0, TOTAL_SEATS - new_aitc - new_bjp),
                    "source": "https://eci.gov.in",
                })
                st.session_state["exit_polls"] = polls
                st.success(f"{added_msg} '{new_agency}'!")
                st.rerun()
            else:
                st.error(enter_agency)
