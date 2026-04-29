"""
CivicPulse India — 2026 Assembly Intelligence
=============================================
Optimized for the May 4 Counting Day cycle.
"""

import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Internal Imports
from config.settings import SUPPORTED_COUNTRIES
from regions import get_region_handler
from services.civic_api import CivicAPIService
from services.calendar_service import CalendarService
from components.timeline import render_timeline
from components.checklist import render_checklist
from components.map_view import render_map_view
from components.notification import render_notification_panel
from utils.location_utils import detect_country_from_input, parse_location
from utils.date_utils import days_until, get_election_status
from utils.validators import validate_location_input

# ── 1. PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CivicPulse India | 2026 Polls",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── 2. SESSION STATE INITIALIZATION ──────────────────────────────────────────
def init_session():
    """Initialize session state keys to prevent KeyError."""
    if "checklist" not in st.session_state:
        st.session_state["checklist"] = {}
    if "location" not in st.session_state:
        st.session_state["location"] = ""
    if "country_code" not in st.session_state:
        st.session_state["country_code"] = "IN"

# ── 3. THEME & STYLING ────────────────────────────────────────────────────────
def apply_india_theme():
    st.markdown("""
        <style>
        /* Force White Background */
        .stApp { background-color: #FFFFFF !important; }

        /* Fix 'Jurisdiction' and 'Status' text */
        h2, h3, .stText, p, span {
            color: #000000 !important; /* Pure black for maximum readability */
        }
        
        /* Specific fix for 'Immediate Actions' and sub-headers */
        .stMarkdown div p strong, .stMarkdown h4 {
            color: #1a1a1a !important;
            font-weight: 800 !important;
        }

        /* Hero Header Styling */
        .main-header {
            background: linear-gradient(90deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
            padding: 2.5rem; border-radius: 15px; border: 2px solid #ddd;
            margin-bottom: 2rem; color: #000080 !important; text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .main-header h1, .main-header p, .main-header b {
            color: #000080 !important;
        }

        /* Fix the Live Updates Tag text */
        .live-tag {
            background-color: #d32f2f !important; 
            color: #ffffff !important; 
            padding: 8px 16px !important;
            border-radius: 25px; 
            font-weight: bold !important;
        }

        /* Checklist Card Contrast */
        .step-card {
            background-color: #f9f9f9 !important;
            border-left: 6px solid #ff9933 !important;
            color: #1a1a1a !important;
            padding: 15px !important;
            margin-bottom: 12px !important;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.05) !important;
        }
        </style>
    """, unsafe_allow_html=True)

# ── 4. SIDEBAR & CONTEXT ──────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.title("🗳️ CivicPulse India")
        st.caption("Assembly Elections 2026 | Counting Day: May 4")
        
        st.divider()
        
        # Location Input
        location = st.text_input(
            "📍 PIN Code or State", 
            value=st.session_state["location"],
            placeholder="e.g. 700001 or West Bengal"
        )
        
        if location and validate_location_input(location):
            st.session_state["location"] = location
            st.session_state["country_code"] = detect_country_from_input(location)
            loc_parsed = parse_location(location)
            
            # Load the handler and data
            handler = get_region_handler(st.session_state["country_code"])
            st.session_state["election_data"] = handler.get_election_data(loc_parsed["normalized"])
            st.session_state["handler"] = handler
            st.success(f"Context Set: {loc_parsed['normalized']}")
        elif location == "":
            # Clear data if input is cleared
            if "election_data" in st.session_state:
                del st.session_state["election_data"]
        
        st.divider()
        st.markdown("#### 🇮🇳 Voter Assistance")
        st.link_button("ECI: Search Name in Roll", "https://electoralsearch.eci.gov.in/", use_container_width=True)

# ── 5. MAIN DASHBOARD ─────────────────────────────────────────────────────────
def main():
    # Crucial: Initialize session before doing anything else
    init_session()
    apply_india_theme()
    render_sidebar()

    # Dashboard Hero
    st.markdown("""
        <div class="main-header">
            <h1>🇮🇳 CivicPulse: 2026 Assembly Hub</h1>
            <p>Phase II Complete (April 29) | <b>Counting Day: May 4, 2026</b></p>
        </div>
    """, unsafe_allow_html=True)

    if "election_data" in st.session_state:
        data = st.session_state["election_data"]
        handler = st.session_state["handler"]
        
        # Real-time Status Logic
        status = get_election_status(data.get("next_election_date"))
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.subheader(f"Jurisdiction: {data.get('jurisdiction', 'General')}")
        with col2:
            st.markdown(f"Status: **{status}**")
        with col3:
            st.markdown('<div style="text-align:right"><span class="live-tag">● LIVE UPDATES</span></div>', unsafe_allow_html=True)

        st.divider()

        # Layout Tabs
        tab_guide, tab_map, tab_reminders = st.tabs(["📋 Voter Guide", "🗺️ Booth Search", "🔔 Notifications"])

        with tab_guide:
            c1, c2 = st.columns([1.5, 1])
            with c1:
                # This component now receives initialized session state
                render_checklist(handler, data)
            with c2:
                render_timeline(handler, data)

        with tab_map:
            render_map_view(data, st.session_state["location"])

        with tab_reminders:
            render_notification_panel(data, handler)
            
    else:
        # Initial Welcome
        st.info("👋 Welcome! Please enter your location in the sidebar to load the 2026 Election Dashboard.")
        st.image("https://www.eci.gov.in/img/eci-logo.png", width=200)

if __name__ == "__main__":
    main()