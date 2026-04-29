"""
CivicPulse — India-Centric Election Timeline Component
======================================================
Localized for the 2026/2029 Indian election cycles with Phase support.
"""

from __future__ import annotations
import streamlit as st
from regions.base import BaseRegionHandler
from utils.date_utils import days_until, format_date_locale


def render_timeline(handler: BaseRegionHandler, election_data: dict) -> None:
    """Render a visual countdown localized for Indian Election phases."""
    st.markdown("### 📅 Election Timeline")

    election_name = election_data.get("election_name", "Upcoming Election")
    next_election = election_data.get("next_election_date")
    
    # Handle the fact that some Indian elections have multiple phase dates
    if isinstance(next_election, str) and "Phase" in next_election:
        # If it's a phase-based string, we display it as a focus area
        st.warning(f"🗳️ **{next_election}** — Check your constituency for exact poll date.")
        days = None
    else:
        days = days_until(next_election) if next_election else None

    # 1. Hero Countdown Section (Indian Gradient)
    if days is not None:
        # Saffron for urgent, Blue for upcoming, Green for live
        if days < 0:
            color, urgency_text = "#138808", "✅ COMPLETED" # Indian Green
        elif days == 0:
            color, urgency_text = "#ef4444", "🚨 LIVE: POLLS OPEN"
        elif days <= 7:
            color, urgency_text = "#ff9933", "🚨 URGENT" # Indian Saffron
        else:
            color, urgency_text = "#000080", "📅 UPCOMING" # Navy Blue

        st.markdown(
            f'<div style="background:linear-gradient(135deg,{color}22,{color}11);border:1px solid {color}44;'
            f'border-radius:16px;padding:2rem;text-align:center;margin-bottom:1.5rem">'
            f'<div style="font-size:0.9rem;color:{color};font-weight:600">{urgency_text}</div>'
            f'<div style="font-size:3.5rem;font-weight:800;color:{color}">{abs(days)}</div>'
            f'<div style="font-size:1rem;color:#ccc">days {"since" if days < 0 else "until"} {election_name}</div>'
            f'<div style="font-size:0.85rem;color:#888;margin-top:0.5rem">'
            f'Target Date: {format_date_locale(next_election)}</div>'
            "</div>",
            unsafe_allow_html=True,
        )

    # 2. Key Indian Milestones (Nomination, Poll, Counting)
    key_dates = election_data.get("key_dates", {})
    if key_dates:
        st.markdown("#### 🗓️ Key Milestones")
        for label, date_str in key_dates.items():
            d = days_until(date_str) if date_str and "Phase" not in str(date_str) else None
            
            if d is not None and d < 0:
                status_icon, status_color, status_text = "✅", "#138808", "Completed"
            elif d == 0:
                status_icon, status_color, status_text = "🔴", "#ef4444", "TODAY"
            elif "Phase" in str(date_str):
                status_icon, status_color, status_text = "📍", "#000080", "Zonal"
            else:
                status_icon, status_color, status_text = "⏳", "#ff9933", f"{d} days" if d else "Planned"

            st.markdown(
                f'<div style="display:flex;align-items:center;gap:1rem;padding:0.8rem 1rem;'
                f'background:rgba(255,255,255,0.03);border-radius:10px;margin-bottom:0.5rem;'
                f'border-left:4px solid {status_color}">'
                f'<span style="font-size:1.1rem">{status_icon}</span>'
                f'<div style="flex:1">'
                f'<div style="font-weight:600;font-size:0.9rem">{label}</div>'
                f'<div style="color:#888;font-size:0.8rem">{date_str}</div>'
                "</div>"
                f'<div style="color:{status_color};font-weight:700;font-size:0.9rem">{status_text}</div>'
                "</div>",
                unsafe_allow_html=True,
            )

    # 3. Voting Methods (EVM & VVPAT Focus)
    voting_methods = election_data.get("voting_methods", [])
    if voting_methods:
        st.divider()
        st.markdown("#### 📟 Voting System")
        cols = st.columns(len(voting_methods))
        for i, method in enumerate(voting_methods):
            with cols[i]:
                st.markdown(
                    f'<div style="background:rgba(19,136,8,0.05);border:1px solid rgba(19,136,8,0.2);'
                    f'border-radius:12px;padding:1rem;text-align:center;min-height:140px">'
                    f'<div style="font-size:2rem">{method["icon"]}</div>'
                    f'<div style="font-weight:600;font-size:0.85rem;margin:0.3rem 0;color:#138808">{method["name"]}</div>'
                    f'<div style="color:#aaa;font-size:0.75rem">{method["description"]}</div>'
                    "</div>",
                    unsafe_allow_html=True,
                )