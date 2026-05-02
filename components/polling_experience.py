"""
CivicPulse — Share Your Polling Experience
==========================================
Accessibility fixes:
- Queue severity communicated via text label, not colour alone
- All status indicators have aria-label
- Report cards have role="listitem" and aria-label
- Accessible form labels
"""

from __future__ import annotations
import streamlit as st
from datetime import datetime
from utils.location_utils import sanitize_text
from utils.validators import sanitize_and_validate
from components.language_selector import T


def _init_reports() -> None:
    if "polling_reports" not in st.session_state:
        st.session_state["polling_reports"] = [
            {
                "booth":         "Govt Primary School, Bhawanipore",
                "user":          "Voter (Kolkata)",
                "queue_minutes": 15,
                "accessible":    True,
                "overall":       "😊 Smooth",
                "notes":         "Very organized. EVM working perfectly. Queue moved fast.",
                "timestamp":     "29 Apr 2026, 9:15 AM",
            },
            {
                "booth":         "Community Hall, Nandigram",
                "user":          "Voter (Midnapore)",
                "queue_minutes": 45,
                "accessible":    False,
                "overall":       "😐 Okay",
                "notes":         "Long queue but manageable. No wheelchair ramp at entrance.",
                "timestamp":     "29 Apr 2026, 10:30 AM",
            },
            {
                "booth":         "Panchayat Bhawan, Kasba",
                "user":          "Voter (Kolkata)",
                "queue_minutes": 5,
                "accessible":    True,
                "overall":       "🎉 Excellent",
                "notes":         "Fastest I've ever voted! Great management by staff.",
                "timestamp":     "29 Apr 2026, 11:00 AM",
            },
        ]


OVERALL_OPTIONS = ["🎉 Excellent", "😊 Smooth", "😐 Okay", "😤 Long Wait", "⚠️ Issues Found"]
OVERALL_COLORS  = {
    "🎉 Excellent":     "#0E6B06",
    "😊 Smooth":        "#138808",
    "😐 Okay":          "#D95200",
    "😤 Long Wait":     "#C62828",
    "⚠️ Issues Found":  "#C62828",
}

# Text labels for queue severity — no colour-only communication
def _queue_severity_label(minutes: int) -> tuple[str, str, str]:
    """Return (colour, text_label, aria_label) for a queue wait time."""
    if minutes <= 15:
        return "#0E6B06", T("Short wait"), T("Short wait: under 15 minutes")
    elif minutes <= 40:
        return "#D95200", T("Moderate wait"), T("Moderate wait: 16 to 40 minutes")
    else:
        return "#C62828", T("Long wait"), T("Long wait: over 40 minutes")


def render_polling_experience() -> None:
    _init_reports()

    st.markdown(f"### 🏛️ {T('Share Your Polling Experience')}")
    st.caption(T("Help fellow voters by reporting queue times, accessibility, and booth conditions. All reports are anonymous."))

    reports = st.session_state["polling_reports"]
    if reports:
        avg_queue        = round(sum(r["queue_minutes"] for r in reports) / len(reports))
        accessible_count = sum(1 for r in reports if r["accessible"])
        excellent        = sum(1 for r in reports if "Excellent" in r["overall"] or "Smooth" in r["overall"])

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric(T("Total Reports"),       len(reports))
        with c2: st.metric(T("Avg Queue Time"),      f"{avg_queue} {T('min')}")
        with c3: st.metric(T("Accessible Booths"),   f"{accessible_count}/{len(reports)}")
        with c4: st.metric(T("Positive Experience"), f"{excellent}/{len(reports)}")

    st.divider()

    st.markdown(f"#### ➕ {T('Submit Your Report')}")
    with st.expander(f"📝 {T('Add your polling experience')}", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            booth_name = st.text_input(
                T("Booth / Polling Station Name"),
                placeholder=T("e.g. Govt School, Block A, Kolkata"),
                key="exp_booth_name",
            )
            queue_time = st.slider(
                T("Queue Wait Time (minutes)"),
                min_value=0, max_value=120, value=20, step=5,
                key="exp_queue_time",
                help=T("0–15 min = short, 16–40 min = moderate, 41+ min = long"),
            )
            # Show text severity label immediately below slider — no colour-only feedback
            q_col, q_lbl = "#0E6B06", T("Short wait")
            if queue_time > 40:
                q_col, q_lbl = "#C62828", T("Long wait")
            elif queue_time > 15:
                q_col, q_lbl = "#D95200", T("Moderate wait")
            st.markdown(
                f'<p style="font-size:0.8rem;font-weight:600;color:{q_col};" '
                f'aria-live="polite">{q_lbl}</p>',
                unsafe_allow_html=True,
            )
        with col2:
            overall    = st.selectbox(T("Overall Experience"), OVERALL_OPTIONS, key="exp_overall")
            accessible = st.toggle(f"♿ {T('Booth was wheelchair accessible')}", key="exp_accessible")

        notes = st.text_area(
            T("Additional Notes (optional)"),
            placeholder=T("EVM working? Staff helpful? Any issues?"),
            max_chars=300,
            key="exp_notes",
        )

        if st.button(f"📤 {T('Submit Report')}", type="primary", key="submit_exp_btn"):
            if not booth_name.strip():
                st.error(T("Please enter the booth or polling station name."))
            else:
                new_report = {
                    "booth":         sanitize_and_validate(booth_name.strip()),
                    "user":          T("Anonymous Voter"),
                    "queue_minutes": queue_time,
                    "accessible":    accessible,
                    "overall":       overall,
                    "notes":         sanitize_and_validate(notes.strip()),
                    "timestamp":     datetime.now().strftime("%d %b %Y, %I:%M %p"),
                }
                st.session_state["polling_reports"].insert(0, new_report)
                st.success(f"✅ {T('Your report has been submitted! Thank you for helping fellow voters.')}")
                st.rerun()

    st.divider()

    st.markdown(f"#### 📋 {T('Recent Reports')}")

    sort_by = st.radio(
        T("Sort by"),
        [f"🕒 {T('Latest First')}", f"⏱️ {T('Longest Queue')}", f"⚡ {T('Shortest Queue')}"],
        horizontal=True,
        key="report_sort",
    )

    all_reports = list(st.session_state["polling_reports"])
    if T("Longest Queue") in sort_by:
        all_reports.sort(key=lambda r: r["queue_minutes"], reverse=True)
    elif T("Shortest Queue") in sort_by:
        all_reports.sort(key=lambda r: r["queue_minutes"])

    accessible_label    = T("Accessible")
    accessibility_issue = T("Accessibility Issue")
    min_wait_label      = T("min wait")

    for report in all_reports:
        exp_color   = OVERALL_COLORS.get(report["overall"], "#9BA3BC")
        q_color, q_label, q_aria = _queue_severity_label(report["queue_minutes"])

        acc_badge = (
            f'<span role="img" aria-label="{accessible_label}" '
            f'style="background:rgba(39,201,110,0.12);color:#0E6B06;font-size:0.68rem;font-weight:700;'
            f'padding:2px 8px;border-radius:20px;border:1px solid rgba(39,201,110,0.3);">'
            f'♿ {accessible_label}</span>'
            if report["accessible"] else
            f'<span role="img" aria-label="{accessibility_issue}" '
            f'style="background:rgba(198,40,40,0.10);color:#C62828;font-size:0.68rem;font-weight:700;'
            f'padding:2px 8px;border-radius:20px;border:1px solid rgba(198,40,40,0.3);">'
            f'⚠️ {accessibility_issue}</span>'
        )

        safe_booth = sanitize_text(report["booth"])
        safe_user  = sanitize_text(report["user"])
        safe_ts    = sanitize_text(report["timestamp"])
        safe_notes = sanitize_text(report.get("notes", ""))

        st.markdown(
            f"""
            <div role="listitem"
                 aria-label="{safe_booth}: {report['overall']}, {q_aria}"
                 style="background:#1C2030;border-radius:14px;padding:16px;
                        border:1px solid rgba(255,255,255,0.08);border-left:5px solid {exp_color};
                        margin-bottom:12px;">
                <div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:10px;">
                    <div style="flex:1;">
                        <div style="font-weight:700;color:#E8EAF0;font-size:0.95rem;">
                            🏛️ {safe_booth}
                        </div>
                        <div style="font-size:0.75rem;color:#5C6480;margin-top:2px;">
                            {safe_user} · {safe_ts}
                        </div>
                    </div>
                    <div style="color:{exp_color};font-weight:700;font-size:0.85rem;
                                background:{exp_color}12;padding:4px 12px;border-radius:20px;
                                white-space:nowrap;border:1px solid {exp_color}30;">
                        {report['overall']}
                    </div>
                </div>
                <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px;">
                    <span aria-label="{q_aria}"
                          style="background:{q_color}12;color:{q_color};font-size:0.72rem;
                                 font-weight:700;padding:3px 10px;border-radius:20px;
                                 border:1px solid {q_color}30;">
                        ⏱️ {report['queue_minutes']} {min_wait_label} — {q_label}
                    </span>
                    {acc_badge}
                </div>
                {f'<div style="font-size:0.82rem;color:#9BA3BC;font-style:italic;padding:8px 12px;background:#242840;border-radius:8px;">{safe_notes}</div>' if safe_notes else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()
    note_text = T("Reports are user-generated and not verified by ECI. For official booth information, visit the ECI portal.")
    st.info(f"📌 **{T('Note')}:** {note_text}")
