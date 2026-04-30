"""
CivicPulse — India-Centric Election Timeline Component
======================================================
Localized for 2026/2029 Indian election cycles with phase support.

Accessibility fixes:
- All custom HTML has role attributes
- Colour values meet WCAG AA contrast on white backgrounds
- User-supplied strings sanitized before injection
"""

from __future__ import annotations
import streamlit as st

from regions.base import BaseRegionHandler
from utils.date_utils import days_until, format_date_locale
from utils.location_utils import sanitize_text


def render_timeline(handler: BaseRegionHandler, election_data: dict) -> None:
    """Render a visual countdown localized for Indian Election phases."""
    st.markdown("### 📅 Election Timeline")

    election_name = sanitize_text(
        election_data.get("election_name", "Upcoming Election")
    )
    next_election = election_data.get("next_election_date")

    # Multi-phase elections display as a note
    if isinstance(next_election, str) and "Phase" in next_election:
        st.warning(
            f"🗳️ **{sanitize_text(next_election)}** — "
            "Check your constituency for the exact poll date."
        )
        days = None
    else:
        days = days_until(next_election) if next_election else None

    # 1. Hero Countdown
    if days is not None:
        # Contrast-safe: text at 4.5:1+ on white
        if days < 0:
            color, text_color, urgency_text = "#1a6b0a", "#1a6b0a", "✅ COMPLETED"
        elif days == 0:
            color, text_color, urgency_text = "#c62828", "#c62828", "🚨 LIVE: POLLS OPEN"
        elif days <= 7:
            color, text_color, urgency_text = "#b35900", "#b35900", "🚨 URGENT"
        else:
            color, text_color, urgency_text = "#000080", "#000080", "📅 UPCOMING"

        st.markdown(
            f'<div role="status" aria-live="polite" aria-label="Election countdown: {abs(days)} days"'
            f' style="background:{color}11;border:1px solid {color}44;'
            f'border-radius:16px;padding:2rem;text-align:center;margin-bottom:1.5rem;">'
            f'<div style="font-size:0.9rem;color:{text_color};font-weight:600;">'
            f"{urgency_text}</div>"
            f'<div style="font-size:3.5rem;font-weight:800;color:{text_color};">'
            f"{abs(days)}</div>"
            f'<div style="font-size:1rem;color:#333;">'
            f'days {"since" if days < 0 else "until"} {election_name}</div>'
            f'<div style="font-size:0.85rem;color:#555;margin-top:0.5rem;">'
            f"Target Date: {sanitize_text(format_date_locale(next_election))}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # 2. Key Milestones
    key_dates = election_data.get("key_dates", {})
    if key_dates:
        st.markdown("#### 🗓️ Key Milestones")
        for label, date_str in key_dates.items():
            d = (
                days_until(date_str)
                if date_str and "Phase" not in str(date_str)
                else None
            )

            if d is not None and d < 0:
                status_icon, s_color, status_text = "✅", "#1a6b0a", "Completed"
            elif d == 0:
                status_icon, s_color, status_text = "🔴", "#c62828", "TODAY"
            elif "Phase" in str(date_str):
                status_icon, s_color, status_text = "📍", "#000080", "Zonal"
            else:
                status_icon, s_color, status_text = (
                    "⏳",
                    "#b35900",
                    f"{d} days" if d is not None else "Planned",
                )

            safe_label    = sanitize_text(label)
            safe_date_str = sanitize_text(str(date_str))

            st.markdown(
                f'<div role="listitem" aria-label="{safe_label}: {status_text}"'
                f' style="display:flex;align-items:center;gap:1rem;padding:0.8rem 1rem;'
                f"background:#fafafa;border-radius:10px;margin-bottom:0.5rem;"
                f'border-left:4px solid {s_color};">'
                f'<span aria-hidden="true" style="font-size:1.1rem;">{status_icon}</span>'
                f"<div style=\"flex:1;\">"
                f'<div style="font-weight:600;font-size:0.9rem;color:#1a1a1a;">{safe_label}</div>'
                f'<div style="color:#444;font-size:0.8rem;">{safe_date_str}</div>'
                f"</div>"
                f'<div style="color:{s_color};font-weight:700;font-size:0.9rem;">'
                f"{sanitize_text(status_text)}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # 3. Voting Methods
    voting_methods = election_data.get("voting_methods", [])
    if voting_methods:
        st.divider()
        st.markdown("#### 📟 Voting System")
        cols = st.columns(len(voting_methods))
        for i, method in enumerate(voting_methods):
            with cols[i]:
                safe_method_name = sanitize_text(method.get("name", ""))
                safe_method_desc = sanitize_text(method.get("description", ""))
                st.markdown(
                    f'<div role="listitem" aria-label="{safe_method_name}"'
                    f' style="background:rgba(19,136,8,0.05);border:1px solid rgba(19,136,8,0.2);'
                    f'border-radius:12px;padding:1rem;text-align:center;min-height:140px;">'
                    f'<div aria-hidden="true" style="font-size:2rem;">{method.get("icon","")}</div>'
                    f'<div style="font-weight:600;font-size:0.85rem;margin:0.3rem 0;color:#1a6b0a;">'
                    f"{safe_method_name}</div>"
                    f'<div style="color:#333;font-size:0.75rem;">{safe_method_desc}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
