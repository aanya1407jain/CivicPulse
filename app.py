"""
CivicPulse India — 2026 Assembly Intelligence
=============================================
Optimized for the May 4 Counting Day cycle.
"""

import streamlit as st
import logging

from dotenv import load_dotenv

load_dotenv()

# Internal imports
from config.settings import (
    SUPPORTED_COUNTRIES, GOOGLE_API_KEY, GEMINI_MODEL, GEMINI_MAX_TOKENS, INDIA
)
from regions import get_region_handler
from services.civic_api import CivicAPIService
from services.calendar_service import CalendarService
from components.timeline import render_timeline
from components.checklist import render_checklist
from components.map_view import render_map_view
from components.notification import render_notification_panel
from utils.location_utils import detect_country_from_input, parse_location, sanitize_text
from utils.date_utils import days_until, get_election_status
from utils.validators import validate_location_input

logger = logging.getLogger(__name__)

# ── 1. PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CivicPulse India | 2026 Polls",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject lang attribute for screen readers (accessibility)
st.markdown(
    '<html lang="en">', unsafe_allow_html=True  # Streamlit strips <html> tags
)
# Alternative approach that actually works in Streamlit:
st.markdown(
    """
    <script>
        document.documentElement.setAttribute('lang', 'en');
        document.documentElement.setAttribute('dir', 'ltr');
    </script>
    """,
    unsafe_allow_html=True,
)


# ── 2. SESSION STATE ──────────────────────────────────────────────────────────
def init_session() -> None:
    """Initialize session state keys to prevent KeyError."""
    defaults = {
        "checklist":    {},
        "location":     "",
        "country_code": INDIA["COUNTRY_CODE"],
        "ai_messages":  [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ── 3. THEME ──────────────────────────────────────────────────────────────────
def apply_india_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp { background-color: #FFFFFF !important; }

        h2, h3, p, span { color: #000000 !important; }

        .stMarkdown div p strong, .stMarkdown h4 {
            color: #1a1a1a !important;
            font-weight: 700 !important;
        }

        .main-header {
            background: linear-gradient(90deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
            padding: 2.5rem; border-radius: 15px; border: 2px solid #ddd;
            margin-bottom: 2rem; text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .main-header h1, .main-header p, .main-header b { color: #000080 !important; }

        .live-tag {
            background-color: #d32f2f !important;
            color: #ffffff !important;
            padding: 8px 16px !important;
            border-radius: 25px;
            font-weight: bold !important;
        }

        .step-card {
            background-color: #f9f9f9 !important;
            border-left: 6px solid #ff9933 !important;
            color: #1a1a1a !important;
            padding: 15px !important;
            margin-bottom: 12px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── 4. GEMINI AI ASSISTANT ────────────────────────────────────────────────────
def render_ai_assistant(election_data: dict) -> None:
    """Inline AI assistant powered by Gemini — answers voter questions."""
    if not GOOGLE_API_KEY:
        st.info(
            "💡 Add `GOOGLE_API_KEY` to your `.env` to unlock the AI voter assistant."
        )
        return

    st.markdown("#### 🤖 AI Voter Assistant (Powered by Gemini)")
    st.caption("Ask anything about voting, your rights, or the election process.")

    # Show conversation history
    for msg in st.session_state["ai_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_q := st.chat_input("e.g. What ID do I need to vote?"):
        st.session_state["ai_messages"].append({"role": "user", "content": user_q})

        with st.chat_message("user"):
            st.markdown(user_q)

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                answer = _call_gemini(user_q, election_data)
            st.markdown(answer)

        st.session_state["ai_messages"].append(
            {"role": "assistant", "content": answer}
        )


def _call_gemini(question: str, election_data: dict) -> str:
    """Call the Gemini API with context about the current election."""
    try:
        import google.generativeai as genai  # type: ignore

        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)

        system_ctx = (
            f"You are CivicPulse, an expert Indian election assistant. "
            f"The user is asking about the {election_data.get('election_name', 'Indian election')} "
            f"in {election_data.get('jurisdiction', 'India')}. "
            f"Key facts: {election_data.get('requirements', [])}. "
            f"Voter helpline: {INDIA['VOTER_HELPLINE']}. "
            f"Keep answers concise (under 150 words), factual, and in plain English."
        )

        response = model.generate_content(
            f"{system_ctx}\n\nVoter question: {question}",
            generation_config={"max_output_tokens": GEMINI_MAX_TOKENS},
        )
        return response.text or "I could not generate a response. Please try again."

    except Exception as exc:
        logger.warning("Gemini call failed: %s", exc)
        return (
            "Sorry, the AI assistant is temporarily unavailable. "
            f"For election queries, call the ECI helpline at **{INDIA['VOTER_HELPLINE']}**."
        )


# ── 5. SIDEBAR ────────────────────────────────────────────────────────────────
def render_sidebar() -> None:
    with st.sidebar:
        st.title("🗳️ CivicPulse India")
        st.caption("Assembly Elections 2026 | Counting Day: May 4")
        st.divider()

        location = st.text_input(
            "📍 PIN Code or State",
            value=st.session_state["location"],
            placeholder="e.g. 700001 or West Bengal",
            help="Enter a 6-digit PIN code or the name of an Indian state",
        )

        if location and validate_location_input(location):
            st.session_state["location"] = location
            st.session_state["country_code"] = detect_country_from_input(location)
            loc_parsed = parse_location(location)

            handler = get_region_handler(st.session_state["country_code"])
            st.session_state["election_data"] = handler.get_election_data(
                loc_parsed["normalized"]
            )
            st.session_state["handler"] = handler
            st.success(f"Context set: {sanitize_text(loc_parsed['normalized'])}")

        elif location and not validate_location_input(location):
            st.warning("Please enter a valid 6-digit PIN code or state name.")

        elif location == "":
            st.session_state.pop("election_data", None)

        st.divider()
        st.markdown("#### 🇮🇳 Voter Assistance")
        st.link_button(
            "ECI: Search Name in Roll",
            INDIA["EPIC_SEARCH_URL"],
            use_container_width=True,
        )


# ── 6. MAIN DASHBOARD ─────────────────────────────────────────────────────────
def main() -> None:
    init_session()
    apply_india_theme()
    render_sidebar()

    # Hero header
    st.markdown(
        """
        <div class="main-header" role="banner">
            <h1>🇮🇳 CivicPulse: 2026 Assembly Hub</h1>
            <p>Phase II Complete (April 29) | <b>Counting Day: May 4, 2026</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "election_data" in st.session_state:
        data    = st.session_state["election_data"]
        handler = st.session_state["handler"]

        status = get_election_status(data.get("next_election_date"))

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.subheader(f"Jurisdiction: {sanitize_text(data.get('jurisdiction', 'General'))}")
        with col2:
            st.markdown(f"Status: **{status}**")
        with col3:
            st.markdown(
                '<div style="text-align:right">'
                '<span class="live-tag" role="status" aria-live="polite">● LIVE UPDATES</span>'
                "</div>",
                unsafe_allow_html=True,
            )

        st.divider()

        tab_guide, tab_map, tab_reminders, tab_ai = st.tabs(
            ["📋 Voter Guide", "🗺️ Booth Search", "🔔 Notifications", "🤖 AI Assistant"]
        )

        with tab_guide:
            c1, c2 = st.columns([1.5, 1])
            with c1:
                render_checklist(handler, data)
            with c2:
                render_timeline(handler, data)

        with tab_map:
            render_map_view(data, st.session_state["location"])

        with tab_reminders:
            render_notification_panel(data, handler)

        with tab_ai:
            render_ai_assistant(data)

    else:
        st.info(
            "👋 Welcome! Enter your location in the sidebar to load the 2026 Election Dashboard."
        )
        st.image("https://www.eci.gov.in/img/eci-logo.png", width=200)


if __name__ == "__main__":
    main()
