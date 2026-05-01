"""
CivicPulse — India-Centric Voter Checklist Component
====================================================
Localized with Indian theme colors and ECI-specific priority handling.
Dark-theme version: all inline HTML uses dark palette.
"""

from __future__ import annotations
import streamlit as st

from config.settings import INDIA
from regions.base import BaseRegionHandler, ElectionStep
from services.calendar_service import CalendarService
from utils.location_utils import sanitize_text


def render_checklist(handler: BaseRegionHandler, election_data: dict) -> None:
    """Render the interactive voter checklist with progress tracking."""

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

    reg_url = election_data.get("registration_url", INDIA["VOTER_PORTAL_URL"])
    st.markdown(
        """
        <div role="region" aria-label="Voter registration"
             style="background:rgba(255,107,26,0.10);padding:16px 20px;border-radius:12px;
                    border-left:5px solid #FF6B1A;margin-top:20px;
                    border:1px solid rgba(255,107,26,0.2);border-left:5px solid #FF6B1A;">
            <strong style="color:#E8EAF0;">🗳️ Need to Register or Update?</strong><br>
            <span style="font-size:0.9rem;color:#9BA3BC;display:block;margin-top:4px;">
                Use Form 6 for new registration or Form 8 for address changes.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.link_button("Go to Official Voter Portal →", reg_url, use_container_width=True)


def _render_step(step: ElectionStep, calendar_svc: CalendarService) -> None:
    """Render a single checklist item with accessible dark-theme markup."""

    if "checklist" not in st.session_state:
        st.session_state["checklist"] = {}

    is_done = st.session_state["checklist"].get(step.id, False)

    # Dark-palette priority colors (accent/highlight tones)
    priority_color = {
        "urgent":   "#FF6B1A",   # orange
        "normal":   "#4F8EF7",   # blue
        "optional": "#27C96E",   # green
    }.get(step.priority, "#9BA3BC")

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
            "text-decoration:line-through;color:#5C6480;opacity:0.7;"
            if checked
            else f"color:{priority_color};font-weight:700;"
        )
        deadline_html = (
            f'<span style="font-size:0.75rem;color:#F74F4F;font-weight:bold;">'
            f"⏰ {sanitize_text(step.deadline)}</span>"
            if step.deadline
            else ""
        )

        # Dark semi-transparent backgrounds keyed to priority
        bg_colors = {
            "urgent":   "rgba(255,107,26,0.10)",
            "normal":   "rgba(79,142,247,0.10)",
            "optional": "rgba(39,201,110,0.10)",
        }
        card_bg = bg_colors.get(step.priority, "#1C2030")
        st.markdown(
            f'<div role="listitem" aria-label="{safe_title}" '
            f'style="border-left:5px solid {priority_color};background:{card_bg};'
            f'padding:12px 16px;border-radius:0 10px 10px 0;margin-bottom:6px;'
            f'box-shadow:0 1px 4px rgba(0,0,0,0.3);">'
            f'<div style="{title_style}">{safe_title}</div>'
            f'<div style="color:#9BA3BC;font-size:0.85rem;margin-top:3px;">{safe_desc}</div>'
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
                'style="text-align:center;color:#27C96E;font-size:1.2rem;margin-top:5px;">✅</div>',
                unsafe_allow_html=True,
            )
