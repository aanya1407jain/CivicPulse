"""
CivicPulse — India-Centric Voter Checklist Component
====================================================
Localized with Indian theme colors and ECI-specific priority handling.

Accessibility fixes:
- <a><button> nesting replaced with st.link_button
- ARIA labels on interactive elements
- Colour-safe text (no #aaa on white)
"""

from __future__ import annotations
import streamlit as st

from config.settings import INDIA
from regions.base import BaseRegionHandler, ElectionStep
from services.calendar_service import CalendarService
from utils.location_utils import sanitize_text


def render_checklist(handler: BaseRegionHandler, election_data: dict) -> None:
    """Render the interactive voter checklist with progress tracking."""

    # Self-healing session initialisation
    if "checklist" not in st.session_state:
        st.session_state["checklist"] = {}

    steps = handler.get_checklist_steps()
    calendar_svc = CalendarService()

    safe_election_name = sanitize_text(
        election_data.get("election_name", "Upcoming Election")
    )

    st.markdown("### 📋 Your Voting Readiness Journey")
    st.markdown(
        f"Ensure you are ready for the **{safe_election_name}**. "
        "Each step brings you closer to casting your vote!"
    )

    # Progress bar
    checked_count = sum(
        1 for s in steps if st.session_state["checklist"].get(s.id, False)
    )
    total_steps = len(steps)
    progress = checked_count / total_steps if total_steps else 0
    st.progress(progress, text=f"🇮🇳 {checked_count}/{total_steps} steps completed")
    st.divider()

    # Group by urgency
    urgent   = [s for s in steps if s.priority == "urgent"]
    normal   = [s for s in steps if s.priority == "normal"]
    optional = [s for s in steps if s.priority == "optional"]

    if urgent:
        st.markdown("#### 🚨 Immediate Actions (Critical)")
        for step in urgent:
            _render_step(step, calendar_svc)

    if normal:
        st.markdown("#### 📌 Important Preparation")
        for step in normal:
            _render_step(step, calendar_svc)

    if optional:
        st.markdown("#### 💡 Knowledge & Assistance")
        for step in optional:
            _render_step(step, calendar_svc)

    # Registration quick-link (no unsafe HTML needed)
    reg_url = election_data.get("registration_url", INDIA["VOTER_PORTAL_URL"])
    st.markdown(
        """
        <div role="region" aria-label="Voter registration"
             style="background:#FFF3E8;padding:16px 20px;border-radius:12px;
                    border-left:5px solid #FF6B00;margin-top:20px;
                    box-shadow:0 1px 4px rgba(255,107,0,0.12);">
            <strong style="color:#1A1A2E;">🗳️ Need to Register or Update?</strong><br>
            <span style="font-size:0.9rem;color:#5C5C7A;display:block;margin-top:4px;">
                Use Form 6 for new registration or Form 8 for address changes.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.link_button("Go to Official Voter Portal →", reg_url, use_container_width=True)


def _render_step(step: ElectionStep, calendar_svc: CalendarService) -> None:
    """Render a single checklist item with accessible markup."""

    # Layer 2 safety check
    if "checklist" not in st.session_state:
        st.session_state["checklist"] = {}

    is_done = st.session_state["checklist"].get(step.id, False)

    priority_color = {
        "urgent":   "#D95200",   # deep saffron — readable on light bg
        "normal":   "#2D3561",   # navy blue
        "optional": "#0E6B06",   # deep green
    }.get(step.priority, "#444444")

    col1, col2, col3 = st.columns([0.08, 0.70, 0.22])

    with col1:
        checked = st.checkbox(
            label=f"Mark '{step.title}' as done",
            value=is_done,
            key=f"chk_{step.id}",
            label_visibility="collapsed",
        )
        st.session_state["checklist"][step.id] = checked

    safe_title = sanitize_text(step.title)
    safe_desc  = sanitize_text(step.description)

    with col2:
        title_style = (
            "text-decoration:line-through;color:#666;opacity:0.7;"
            if checked
            else f"color:{priority_color};font-weight:700;"
        )
        deadline_html = (
            f'<span style="font-size:0.75rem;color:#c62828;font-weight:bold;">'
            f"⏰ {sanitize_text(step.deadline)}</span>"
            if step.deadline
            else ""
        )

        bg_colors = {
            "urgent":   "#FFF3E8",
            "normal":   "#EEF1FF",
            "optional": "#F0FAF0",
        }
        card_bg = bg_colors.get(step.priority, "#FAFAF8")
        st.markdown(
            f'<div role="listitem" aria-label="{safe_title}" '
            f'style="border-left:5px solid {priority_color};background:{card_bg};'
            f'padding:12px 16px;border-radius:0 10px 10px 0;margin-bottom:6px;'
            f'box-shadow:0 1px 4px rgba(26,26,46,0.07);">'
            f'<div style="{title_style}">{safe_title}</div>'
            f'<div style="color:#5C5C7A;font-size:0.85rem;margin-top:3px;">{safe_desc}</div>'
            f'<div style="margin-top:6px;">{deadline_html}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
        if step.url:
            st.link_button(
                "🔗 ECI Portal",
                step.url,
                help=f"Official portal for: {step.title}",
            )

    with col3:
        if step.deadline and not checked:
            gcal_link = calendar_svc.generate_gcal_link(
                title=step.title,
                date_str=step.deadline,
                description=step.description,
            )
            st.link_button(
                "📅 Remind Me",
                gcal_link,
                use_container_width=True,
                help=f"Add '{step.title}' reminder to Google Calendar",
            )
        elif checked:
            st.markdown(
                '<div role="img" aria-label="Step completed" '
                'style="text-align:center;color:#138808;font-size:1.2rem;margin-top:5px;">✅</div>',
                unsafe_allow_html=True,
            )
