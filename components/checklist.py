"""
CivicPulse — India-Centric Voter Checklist Component
====================================================
Localized with Indian theme colors and ECI-specific priority handling.
Includes self-healing session state initialization.
"""

from __future__ import annotations
import streamlit as st
from regions.base import BaseRegionHandler, ElectionStep
from services.calendar_service import CalendarService


def render_checklist(handler: BaseRegionHandler, election_data: dict) -> None:
    """Render the interactive voter checklist with progress tracking for Indian voters."""
    
    # --- SELF-HEALING INITIALIZATION ---
    # Fixes KeyError: 'checklist' by ensuring it exists before access
    if "checklist" not in st.session_state:
        st.session_state["checklist"] = {}
        
    steps = handler.get_checklist_steps()
    calendar_svc = CalendarService()

    st.markdown("### 📋 Your Voting Readiness Journey")
    st.markdown(
        f"Ensure you are ready for the **{election_data.get('election_name', 'Upcoming Election')}**. "
        "Each step brings you closer to casting your vote!"
    )

    # Progress bar with Indian Green color
    # We use .get() as a second layer of defense
    checked_count = sum(1 for s in steps if st.session_state["checklist"].get(s.id, False))
    total_steps = len(steps)
    progress = checked_count / total_steps if total_steps else 0
    
    st.progress(progress, text=f"🇮🇳 {checked_count}/{total_steps} steps completed")

    st.divider()

    # Urgency grouping
    urgent = [s for s in steps if s.priority == "urgent"]
    normal = [s for s in steps if s.priority == "normal"]
    optional = [s for s in steps if s.priority == "optional"]

    # Render Groups
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

    # Registration quick link (Points to ECI portal)
    reg_url = election_data.get("registration_url", "https://voters.eci.gov.in/")
    st.markdown(
        f"""
        <div style="background-color:rgba(255, 153, 51, 0.1); padding:15px; border-radius:10px; border-left: 5px solid #ff9933; margin-top:20px;">
            <strong>🗳️ Need to Register or Update?</strong><br>
            <span style="font-size:0.9rem">Use Form 6 for new registration or Form 8 for address shifts on the ECI portal.</span><br>
            <a href="{reg_url}" target="_blank" style="color:#ff9933; font-weight:bold; text-decoration:none;">Go to Official Voter Portal →</a>
        </div>
        """, 
        unsafe_allow_html=True
    )


def _render_step(step: ElectionStep, calendar_svc: CalendarService) -> None:
    """Renders an individual checklist item with Indian styling."""
    col1, col2, col3 = st.columns([0.08, 0.70, 0.22])
    
    # Layer 3 safety check
    if "checklist" not in st.session_state:
        st.session_state["checklist"] = {}
        
    is_done = st.session_state["checklist"].get(step.id, False)

    with col1:
        # Styled checkbox - key is unique per step ID
        checked = st.checkbox("", value=is_done, key=f"chk_{step.id}", label_visibility="collapsed")
        st.session_state["checklist"][step.id] = checked

    # Indian-themed status colors: Saffron, Navy Blue, Indian Green
    priority_color = {
        "urgent": "#ff9933", 
        "normal": "#000080", 
        "optional": "#138808"
    }.get(step.priority, "#888")
    
    with col2:
        # Style logic: Strike-through if checked, colored if pending
        title_style = "text-decoration:line-through;color:#888;opacity:0.6;" if checked else f"color:{priority_color};font-weight:700;"
        url_html = f'<a href="{step.url}" target="_blank" style="font-size:0.75rem;color:#000080;font-weight:600;text-decoration:none;">🔗 ECI Portal</a>' if step.url else ""
        deadline_html = f'<span style="font-size:0.75rem;color:#d32f2f;font-weight:bold;">⏰ {step.deadline}</span>' if step.deadline else ""

        # Step Card Container
        st.markdown(
            f'<div class="step-card" style="border-left: 5px solid {priority_color}; background:white; padding:10px; border-radius:4px; margin-bottom:5px;">'
            f'<div style="{title_style}">{step.title}</div>'
            f'<div style="color:#222; font-size:0.85rem; margin-top:2px; font-weight:400;">{step.description}</div>'
            f'<div style="margin-top:5px;">{deadline_html} &nbsp; {url_html}</div>'
            "</div>",
            unsafe_allow_html=True,
        )

    with col3:
        # Only show calendar button if a deadline exists and it's not already checked
        if step.deadline and not checked:
            gcal_link = calendar_svc.generate_gcal_link(
                title=step.title,
                date_str=step.deadline,
                description=step.description,
            )
            st.markdown(
                f'<a href="{gcal_link}" target="_blank">'
                f'<button style="width:100%;padding:8px;background:{priority_color};color:white;border:none;border-radius:8px;cursor:pointer;font-size:0.7rem;font-weight:bold;">📅 Remind Me</button>'
                f'</a>', 
                unsafe_allow_html=True
            )
        elif checked:
            st.markdown('<div style="text-align:center;color:#138808;font-size:1.2rem;margin-top:5px;">✅</div>', unsafe_allow_html=True)