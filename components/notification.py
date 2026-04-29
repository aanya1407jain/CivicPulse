"""
CivicPulse — India-Centric Notifications & Reminders Component
==============================================================
Localized for ECI (Election Commission of India) helplines,
SMS status checks, and localized Google Calendar reminders.
"""

from __future__ import annotations
import streamlit as st
from services.calendar_service import CalendarService
from regions.base import BaseRegionHandler

def render_notification_panel(election_data: dict, handler: BaseRegionHandler | None) -> None:
    """Render the localized reminder and helpline panel for Indian voters."""
    st.markdown("### 🔔 Election Alerts & Support")
    st.markdown(
        "Never miss a polling date. Set high-priority reminders and access "
        "official ECI support channels below."
    )

    # 1. Official ECI Helpline (Crucial for India)
    st.markdown("#### 📞 Official ECI Support")
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("☎️ **Toll-Free: 1950**\n\nCall for registration status, booth location, or to report issues.")
    with col_b:
        st.success("📱 **Voter Helpline App**\n\nDownload the official ECI app for e-EPIC and real-time results.")
        st.link_button("Get App on Play Store", "https://play.google.com/store/apps/details?id=com.eci.citizen")

    st.divider()

    # 2. Calendar Reminders (Using IST Localized Service)
    st.markdown("#### 📅 Sync Key Dates to Calendar")
    st.caption("Syncing works instantly with Google Calendar — no sign-in required.")
    
    calendar_svc = CalendarService()
    # Uses the build_india_reminder_events logic we added to the service
    reminder_links = calendar_svc.generate_reminder_links(election_data)

    if not reminder_links:
        st.info("Polling dates for this specific constituency are being finalized. Check back soon!")
    else:
        for reminder in reminder_links:
            col1, col2 = st.columns([3, 1])
            with col1:
                # Saffron-tinted background for Indian context
                st.markdown(
                    f'<div style="background:rgba(255, 153, 51, 0.08); border-left: 4px solid #ff9933; '
                    f'border-radius:8px; padding:0.75rem 1rem;">'
                    f'<div style="font-weight:600; font-size:0.9rem; color:#333;">{reminder["title"]}</div>'
                    f'<div style="color:#666; font-size:0.8rem">📅 {reminder["date"]}</div>'
                    "</div>",
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f'<a href="{reminder["link"]}" target="_blank" style="text-decoration:none">'
                    f'<button style="width:100%; padding:0.8rem; background:#000080; color:white; '
                    f'border:none; border-radius:8px; cursor:pointer; font-size:0.8rem; font-weight:bold;">'
                    f'➕ Sync</button></a>',
                    unsafe_allow_html=True,
                )
            st.markdown("")

    st.divider()

    # 3. India-Specific SMS/Status Check
    st.markdown("#### 💬 SMS Voter Search")
    st.markdown(
        "You can check your name in the electoral roll by sending an SMS to **1950**."
    )
    
    with st.expander("Show SMS Formats"):
        st.code("ECI <EPIC_NUMBER> to 1950", language="text")
        st.caption("Example: ECI ABC1234567")

    # Demo Subscription (Hackathon Mock)
    st.markdown("#### 📱 Get Mobile Notifications")
    phone = st.text_input("Enter 10-digit mobile number", placeholder="9876543210")
    if st.button("🔔 Subscribe to Poll Alerts"):
        if phone and len(phone) >= 10:
            st.success(f"✅ Registered! You will receive alerts on {phone} for {election_data.get('jurisdiction')} polls.")
        else:
            st.error("Please enter a valid 10-digit Indian mobile number.")

    st.divider()
    st.markdown(
        '<p style="font-size:0.8rem; color:#888; text-align:center;">'
        'Data powered by ECI Samadhan & CivicPulse Intelligence'
        '</p>',
        unsafe_allow_html=True
    )