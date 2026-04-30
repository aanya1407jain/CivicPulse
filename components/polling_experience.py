"""
CivicPulse — Share Your Polling Experience
==========================================
Crowdsourced booth queue times, accessibility reports, and polling experience.
Reports are stored in session state (can be persisted with a backend).
"""

from __future__ import annotations
import streamlit as st
from datetime import datetime
from utils.location_utils import sanitize_text


def _init_reports() -> None:
    """Seed session state with sample reports on first load."""
    if "polling_reports" not in st.session_state:
        st.session_state["polling_reports"] = [
            {
                "booth": "Govt Primary School, Bhawanipore",
                "user": "Voter (Kolkata)",
                "queue_minutes": 15,
                "accessible": True,
                "overall": "😊 Smooth",
                "notes": "Very organized. EVM working perfectly. Queue moved fast.",
                "timestamp": "29 Apr 2026, 9:15 AM",
            },
            {
                "booth": "Community Hall, Nandigram",
                "user": "Voter (Midnapore)",
                "queue_minutes": 45,
                "accessible": False,
                "overall": "😐 Okay",
                "notes": "Long queue but manageable. No wheelchair ramp at entrance.",
                "timestamp": "29 Apr 2026, 10:30 AM",
            },
            {
                "booth": "Panchayat Bhawan, Kasba",
                "user": "Voter (Kolkata)",
                "queue_minutes": 5,
                "accessible": True,
                "overall": "🎉 Excellent",
                "notes": "Fastest I've ever voted! Great management by staff.",
                "timestamp": "29 Apr 2026, 11:00 AM",
            },
        ]


OVERALL_OPTIONS = ["🎉 Excellent", "😊 Smooth", "😐 Okay", "😤 Long Wait", "⚠️ Issues Found"]
OVERALL_COLORS  = {
    "🎉 Excellent":  "#0E6B06",
    "😊 Smooth":     "#138808",
    "😐 Okay":       "#D95200",
    "😤 Long Wait":  "#C62828",
    "⚠️ Issues Found": "#C62828",
}


def render_polling_experience() -> None:
    """Render the polling experience sharing panel."""
    _init_reports()

    st.markdown("### 🏛️ Share Your Polling Experience")
    st.caption(
        "Help fellow voters by reporting queue times, accessibility, and booth conditions. "
        "All reports are anonymous."
    )

    # ── Stats overview ─────────────────────────────────────────────────────────
    reports = st.session_state["polling_reports"]
    if reports:
        avg_queue   = round(sum(r["queue_minutes"] for r in reports) / len(reports))
        accessible_count = sum(1 for r in reports if r["accessible"])
        excellent   = sum(1 for r in reports if "Excellent" in r["overall"] or "Smooth" in r["overall"])

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total Reports", len(reports), help="Number of voter reports submitted")
        with c2:
            st.metric("Avg Queue Time", f"{avg_queue} min", help="Average wait time reported")
        with c3:
            st.metric(
                "Accessible Booths",
                f"{accessible_count}/{len(reports)}",
                help="Booths reported as wheelchair accessible"
            )
        with c4:
            st.metric(
                "Positive Experience",
                f"{excellent}/{len(reports)}",
                help="Reports marked Excellent or Smooth"
            )

    st.divider()

    # ── Submit form ────────────────────────────────────────────────────────────
    st.markdown("#### ➕ Submit Your Report")
    with st.expander("📝 Add your polling experience", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            booth_name = st.text_input(
                "Booth / Polling Station Name",
                placeholder="e.g. Govt School, Block A, Kolkata",
                key="exp_booth_name",
            )
            queue_time = st.slider(
                "Queue Wait Time (minutes)",
                min_value=0, max_value=120, value=20, step=5,
                key="exp_queue_time",
            )
        with col2:
            overall = st.selectbox(
                "Overall Experience",
                OVERALL_OPTIONS,
                key="exp_overall",
            )
            accessible = st.toggle(
                "♿ Booth was wheelchair accessible",
                key="exp_accessible",
            )

        notes = st.text_area(
            "Additional Notes (optional)",
            placeholder="EVM working? Staff helpful? Any issues?",
            max_chars=300,
            key="exp_notes",
        )

        if st.button("📤 Submit Report", type="primary", key="submit_exp_btn"):
            if not booth_name.strip():
                st.error("Please enter the booth or polling station name.")
            else:
                new_report = {
                    "booth": sanitize_text(booth_name.strip()),
                    "user": "Anonymous Voter",
                    "queue_minutes": queue_time,
                    "accessible": accessible,
                    "overall": overall,
                    "notes": sanitize_text(notes.strip()),
                    "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                }
                st.session_state["polling_reports"].insert(0, new_report)
                st.success("✅ Your report has been submitted! Thank you for helping fellow voters.")
                st.rerun()

    st.divider()

    # ── Reports feed ───────────────────────────────────────────────────────────
    st.markdown("#### 📋 Recent Reports")

    sort_by = st.radio(
        "Sort by",
        ["🕒 Latest First", "⏱️ Longest Queue", "⚡ Shortest Queue"],
        horizontal=True,
        key="report_sort",
    )

    all_reports = list(st.session_state["polling_reports"])
    if sort_by == "⏱️ Longest Queue":
        all_reports.sort(key=lambda r: r["queue_minutes"], reverse=True)
    elif sort_by == "⚡ Shortest Queue":
        all_reports.sort(key=lambda r: r["queue_minutes"])

    for report in all_reports:
        exp_color = OVERALL_COLORS.get(report["overall"], "#5C5C7A")
        acc_badge = (
            '<span style="background:#E8F5E6;color:#0E6B06;font-size:0.68rem;font-weight:700;'
            'padding:2px 8px;border-radius:20px;border:1px solid #B8E0B4;">♿ Accessible</span>'
            if report["accessible"]
            else '<span style="background:#FFEBEE;color:#C62828;font-size:0.68rem;font-weight:700;'
            'padding:2px 8px;border-radius:20px;border:1px solid #FF8A80;">⚠️ Accessibility Issue</span>'
        )

        queue_color = (
            "#0E6B06" if report["queue_minutes"] <= 15
            else "#D95200" if report["queue_minutes"] <= 40
            else "#C62828"
        )

        st.markdown(
            f"""
            <div style="background:#FFFFFF;border-radius:14px;padding:16px;
                        border:1px solid #E8E4DC;border-left:5px solid {exp_color};
                        margin-bottom:12px;box-shadow:0 2px 6px rgba(0,0,0,0.05);">
                <div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:10px;">
                    <div style="flex:1;">
                        <div style="font-weight:700;color:#1A1A2E;font-size:0.95rem;">
                            🏛️ {report['booth']}
                        </div>
                        <div style="font-size:0.75rem;color:#9090A8;margin-top:2px;">
                            {report['user']} · {report['timestamp']}
                        </div>
                    </div>
                    <div style="color:{exp_color};font-weight:700;font-size:0.85rem;
                                background:{exp_color}12;padding:4px 12px;border-radius:20px;
                                white-space:nowrap;border:1px solid {exp_color}30;">
                        {report['overall']}
                    </div>
                </div>
                <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px;">
                    <span style="background:{queue_color}12;color:{queue_color};font-size:0.72rem;
                                 font-weight:700;padding:3px 10px;border-radius:20px;
                                 border:1px solid {queue_color}30;">
                        ⏱️ {report['queue_minutes']} min wait
                    </span>
                    {acc_badge}
                </div>
                {f'<div style="font-size:0.82rem;color:#5C5C7A;font-style:italic;padding:8px 12px;background:#F5F3EF;border-radius:8px;">{report["notes"]}</div>' if report.get("notes") else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()
    st.info(
        "📌 **Note:** Reports are user-generated and not verified by ECI. "
        "For official booth information, visit the [ECI portal](https://electoralsearch.eci.gov.in/)."
    )
