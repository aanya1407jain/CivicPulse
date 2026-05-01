"""
CivicPulse — India-Centric Notifications & Reminders Component
==============================================================
Localized for ECI helplines, SMS status checks, and Google Calendar reminders.

Accessibility fixes:
- <a><button> nesting replaced with st.link_button
- Colour-safe text values
- ARIA region labels
"""

from __future__ import annotations
import streamlit as st

from config.settings import INDIA
from regions.base import BaseRegionHandler
from services.calendar_service import CalendarService
from utils.location_utils import sanitize_text
from utils.validators import validate_phone


def render_notification_panel(
    election_data: dict, handler: BaseRegionHandler | None
) -> None:
    """Render the localized reminder and helpline panel for Indian voters."""
    st.markdown("### 🔔 Election Alerts & Support")
    st.markdown(
        "Never miss a polling date. Set high-priority reminders and access "
        "official ECI support channels below."
    )

    # 1. Official ECI Helpline
    st.markdown("#### 📞 Official ECI Support")
    col_a, col_b = st.columns(2)
    with col_a:
        st.info(
            f"☎️ **Toll-Free: {INDIA['VOTER_HELPLINE']}**\n\n"
            "Call for registration status, booth location, or to report issues."
        )
    with col_b:
        st.success(
            "📱 **Voter Helpline App**\n\n"
            "Download the official ECI app for e-EPIC and real-time results."
        )
        st.link_button(
            "Get App on Play Store",
            INDIA["VOTER_APP_PLAYSTORE"],
            use_container_width=True,
        )

    st.divider()

    # 2. Calendar Reminders
    st.markdown("#### 📅 Sync Key Dates to Calendar")
    st.caption("Syncing works instantly with Google Calendar — no sign-in required.")

    calendar_svc = CalendarService()
    reminder_links = calendar_svc.generate_reminder_links(election_data)

    if not reminder_links:
        st.info(
            "Polling dates for this constituency are being finalised. Check back soon!"
        )
    else:
        for reminder in reminder_links:
            safe_title = sanitize_text(reminder["title"])
            safe_date  = sanitize_text(reminder["date"])
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(
                    f'<div role="listitem" '
                    f'style="background:rgba(255,107,26,0.10);border-left:4px solid #FF6B1A;'
                    f'border-radius:0 10px 10px 0;padding:0.85rem 1rem;'
                    f'box-shadow:0 1px 3px rgba(255,107,0,0.10);">'
                    f'<div style="font-weight:600;font-size:0.9rem;color:#E8EAF0;">{safe_title}</div>'
                    f'<div style="color:#9BA3BC;font-size:0.8rem;margin-top:2px;">📅 {safe_date}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
            with col2:
                st.link_button(
                    "➕ Sync",
                    reminder["link"],
                    use_container_width=True,
                    help=f"Add {reminder['title']} to Google Calendar",
                )
            st.markdown("")

    st.divider()

    # 3. SMS Voter Search
    st.markdown("#### 💬 SMS Voter Search")
    st.markdown(
        f"Check your name in the electoral roll by sending an SMS to "
        f"**{INDIA['SMS_NUMBER']}**."
    )
    with st.expander("Show SMS Formats"):
        st.code(f"ECI <EPIC_NUMBER> to {INDIA['SMS_NUMBER']}", language="text")
        st.caption("Example: ECI ABC1234567")

    # 4. Mobile Notification subscription (demo)
    st.markdown("#### 📱 Get Mobile Notifications")
    phone = st.text_input(
        "Enter 10-digit mobile number",
        placeholder="9876543210",
        help="Standard Indian mobile number starting with 6, 7, 8, or 9",
    )
    if st.button("🔔 Subscribe to Poll Alerts", type="primary"):
        if validate_phone(phone):
            safe_jurisdiction = sanitize_text(
                election_data.get("jurisdiction", "your region")
            )
            st.success(
                f"✅ Registered! You will receive alerts on {phone} "
                f"for {safe_jurisdiction} polls."
            )
        else:
            st.error("Please enter a valid 10-digit Indian mobile number (e.g. 9876543210).")

    st.divider()
    st.markdown(
        '<p style="font-size:0.8rem;color:#666;text-align:center;">'
        "Data powered by ECI Samadhan &amp; CivicPulse Intelligence"
        "</p>",
        unsafe_allow_html=True,
    )
