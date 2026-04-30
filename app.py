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
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Fraunces:wght@700;900&display=swap');

        /* ─── ROOT & GLOBAL ─────────────────────────────────── */
        :root {
            --saffron:      #FF6B00;
            --saffron-lt:   #FFF3E8;
            --saffron-md:   #FFD4A8;
            --navy:         #1A1A2E;
            --navy-lt:      #2D3561;
            --green:        #138808;
            --green-lt:     #E8F5E6;
            --red:          #C62828;
            --red-lt:       #FFEBEE;
            --bg:           #FAFAF8;
            --surface:      #FFFFFF;
            --surface2:     #F5F3EF;
            --border:       #E8E4DC;
            --text-primary: #1A1A2E;
            --text-secondary: #5C5C7A;
            --text-muted:   #9090A8;
            --shadow-sm:    0 1px 4px rgba(26,26,46,0.08);
            --shadow-md:    0 4px 16px rgba(26,26,46,0.12);
            --shadow-lg:    0 8px 32px rgba(26,26,46,0.15);
            --radius-sm:    8px;
            --radius-md:    14px;
            --radius-lg:    20px;
        }

        /* ─── APP SHELL ─────────────────────────────────────── */
        .stApp {
            background-color: var(--bg) !important;
            font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
        }

        /* ─── SIDEBAR ───────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: linear-gradient(160deg, #1A1A2E 0%, #2D3561 60%, #1A3A2E 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.08) !important;
        }
        [data-testid="stSidebar"] * {
            color: #F0EDE8 !important;
        }
        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] .stMarkdown span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stCaption {
            color: #C8C4BC !important;
        }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4 {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }
        [data-testid="stSidebar"] .stTextInput input {
            background: rgba(255,255,255,0.10) !important;
            border: 1px solid rgba(255,255,255,0.20) !important;
            color: #FFFFFF !important;
            border-radius: var(--radius-sm) !important;
        }
        [data-testid="stSidebar"] .stTextInput input::placeholder {
            color: rgba(255,255,255,0.45) !important;
        }
        [data-testid="stSidebar"] .stTextInput input:focus {
            border-color: var(--saffron) !important;
            box-shadow: 0 0 0 2px rgba(255,107,0,0.35) !important;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: #C8C4BC !important;
        }
        /* Sidebar success / warning alerts */
        [data-testid="stSidebar"] .stAlert {
            background: rgba(255,255,255,0.10) !important;
            border: 1px solid rgba(255,255,255,0.18) !important;
            border-radius: var(--radius-sm) !important;
        }
        [data-testid="stSidebar"] .stAlert p,
        [data-testid="stSidebar"] .stAlert span {
            color: #F0EDE8 !important;
        }
        [data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.15) !important;
        }
        /* Sidebar link button */
        [data-testid="stSidebar"] .stLinkButton a {
            background: rgba(255,107,0,0.20) !important;
            border: 1px solid rgba(255,107,0,0.40) !important;
            color: #FFD4A8 !important;
            border-radius: var(--radius-sm) !important;
        }
        [data-testid="stSidebar"] .stLinkButton a:hover {
            background: rgba(255,107,0,0.35) !important;
        }

        /* ─── MAIN CONTENT TYPOGRAPHY ───────────────────────── */
        .main .stMarkdown h1, .main .stMarkdown h2,
        .main .stMarkdown h3, .main .stMarkdown h4 {
            color: var(--text-primary) !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        .main .stMarkdown p, .main .stMarkdown span,
        .main .stMarkdown li {
            color: var(--text-primary) !important;
        }

        /* ─── TABS ───────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            background: var(--surface2) !important;
            border-radius: var(--radius-md) !important;
            padding: 4px !important;
            gap: 4px !important;
            border: 1px solid var(--border) !important;
        }
        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            border-radius: 10px !important;
            color: var(--text-secondary) !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
            padding: 8px 18px !important;
            transition: all 0.2s ease !important;
        }
        .stTabs [aria-selected="true"] {
            background: var(--surface) !important;
            color: var(--saffron) !important;
            box-shadow: var(--shadow-sm) !important;
        }
        .stTabs [data-baseweb="tab-panel"] {
            background: transparent !important;
            padding-top: 1.5rem !important;
        }

        /* ─── METRIC CARDS ───────────────────────────────────── */
        [data-testid="stMetric"] {
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            padding: 1.2rem !important;
            box-shadow: var(--shadow-sm) !important;
        }
        [data-testid="stMetric"] label {
            color: var(--text-muted) !important;
            font-size: 0.78rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }
        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: var(--text-primary) !important;
            font-weight: 800 !important;
        }

        /* ─── ALERTS / INFO BOXES ───────────────────────────── */
        .stAlert {
            border-radius: var(--radius-md) !important;
            border: none !important;
        }
        .stAlert[data-baseweb="notification"] {
            background: var(--saffron-lt) !important;
        }
        div[data-testid="stInfo"] {
            background: #EEF2FF !important;
            border-left: 4px solid #4F6EF7 !important;
            border-radius: var(--radius-sm) !important;
            color: var(--navy) !important;
        }
        div[data-testid="stSuccess"] {
            background: var(--green-lt) !important;
            border-left: 4px solid var(--green) !important;
            border-radius: var(--radius-sm) !important;
            color: var(--navy) !important;
        }
        div[data-testid="stWarning"] {
            background: #FFF8E1 !important;
            border-left: 4px solid #F9A825 !important;
            border-radius: var(--radius-sm) !important;
            color: var(--navy) !important;
        }
        div[data-testid="stError"] {
            background: var(--red-lt) !important;
            border-left: 4px solid var(--red) !important;
            border-radius: var(--radius-sm) !important;
            color: var(--navy) !important;
        }
        /* Fix text inside alerts */
        div[data-testid="stInfo"] p,
        div[data-testid="stSuccess"] p,
        div[data-testid="stWarning"] p,
        div[data-testid="stError"] p {
            color: var(--navy) !important;
        }

        /* ─── BUTTONS ────────────────────────────────────────── */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--saffron) 0%, #FF8C00 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: var(--radius-sm) !important;
            font-weight: 700 !important;
            box-shadow: 0 2px 8px rgba(255,107,0,0.35) !important;
            transition: all 0.2s !important;
        }
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 16px rgba(255,107,0,0.45) !important;
        }
        .stLinkButton a {
            background: var(--surface2) !important;
            border: 1px solid var(--border) !important;
            color: var(--text-primary) !important;
            border-radius: var(--radius-sm) !important;
            font-weight: 600 !important;
            transition: all 0.2s !important;
        }
        .stLinkButton a:hover {
            background: var(--saffron-lt) !important;
            border-color: var(--saffron) !important;
            color: var(--saffron) !important;
        }

        /* ─── PROGRESS BAR ───────────────────────────────────── */
        .stProgress > div > div {
            background: linear-gradient(90deg, var(--saffron) 0%, #FF8C00 100%) !important;
            border-radius: 99px !important;
        }
        .stProgress > div {
            background: var(--border) !important;
            border-radius: 99px !important;
        }

        /* ─── INPUTS (main area) ─────────────────────────────── */
        .main .stTextInput input {
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-sm) !important;
            color: var(--text-primary) !important;
        }
        .main .stTextInput input:focus {
            border-color: var(--saffron) !important;
            box-shadow: 0 0 0 3px rgba(255,107,0,0.15) !important;
        }

        /* ─── DIVIDER ────────────────────────────────────────── */
        hr {
            border-color: var(--border) !important;
            margin: 1.5rem 0 !important;
        }

        /* ─── EXPANDER ───────────────────────────────────────── */
        .streamlit-expander {
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
        }

        /* ─── CHAT ───────────────────────────────────────────── */
        [data-testid="stChatMessage"] {
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
        }

        /* ─── HERO HEADER ────────────────────────────────────── */
        .main-header {
            background: linear-gradient(120deg, #FFF3E8 0%, #FFFFFF 45%, #E8F5E6 100%);
            padding: 2.5rem 3rem;
            border-radius: var(--radius-lg);
            border: 1px solid var(--border);
            border-top: 5px solid var(--saffron);
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: var(--shadow-md);
            position: relative;
            overflow: hidden;
        }
        .main-header::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 5px;
            background: linear-gradient(90deg, #FF6B00 33%, #FFFFFF 33%, #FFFFFF 66%, #138808 66%);
        }
        .main-header h1 {
            color: var(--navy) !important;
            font-family: 'Fraunces', Georgia, serif !important;
            font-size: 2.2rem !important;
            font-weight: 900 !important;
            margin-bottom: 0.5rem !important;
            letter-spacing: -0.02em !important;
        }
        .main-header p, .main-header b {
            color: var(--text-secondary) !important;
            font-size: 1rem !important;
        }
        .main-header b { color: var(--navy) !important; }

        /* ─── LIVE TAG ───────────────────────────────────────── */
        .live-tag {
            display: inline-flex !important;
            align-items: center !important;
            gap: 6px !important;
            background: var(--red-lt) !important;
            color: var(--red) !important;
            padding: 6px 14px !important;
            border-radius: 99px !important;
            font-weight: 700 !important;
            font-size: 0.8rem !important;
            border: 1px solid rgba(198,40,40,0.25) !important;
            letter-spacing: 0.04em !important;
        }

        /* ─── STEP CARD ──────────────────────────────────────── */
        .step-card {
            background: var(--surface) !important;
            border-left: 5px solid var(--saffron) !important;
            color: var(--text-primary) !important;
            padding: 16px 20px !important;
            margin-bottom: 12px !important;
            border-radius: 0 var(--radius-sm) var(--radius-sm) 0 !important;
            box-shadow: var(--shadow-sm) !important;
        }

        /* ─── CHECKBOX LABEL ─────────────────────────────────── */
        .stCheckbox label span {
            color: var(--text-primary) !important;
        }

        /* ─── CODE BLOCK ─────────────────────────────────────── */
        .stCode, code {
            background: var(--surface2) !important;
            color: var(--navy) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-sm) !important;
        }

        /* ─── SCROLLBAR ──────────────────────────────────────── */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }
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

    except ImportError:
        return (
            "⚠️ **Missing package:** `google-generativeai` is not installed. "
            "Add it to `requirements.txt` and restart."
        )
    except Exception as exc:
        err = str(exc)
        logger.error("Gemini call failed: %s", err)

        if "API_KEY_INVALID" in err or "invalid" in err.lower():
            return "⚠️ **Invalid API key.** Check that `GOOGLE_API_KEY` is set correctly in your HF Space secrets."
        if "quota" in err.lower() or "429" in err:
            return "⚠️ **Quota exceeded.** Your Gemini API free tier limit has been reached. Try again later."
        if "not found" in err.lower() or "404" in err:
            return "⚠️ **Model not found.** The Gemini model name may be incorrect or unavailable in your region."
        if "permission" in err.lower() or "403" in err:
            return "⚠️ **Permission denied.** Your API key may not have access to the Gemini API. Check Google AI Studio."

        # Show actual error for any other unknown failure
        return (
            f"⚠️ **Gemini error:** {err}\n\n"
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
            st.markdown(
                f'<h3 style="margin:0;color:#1A1A2E;font-family:\'Plus Jakarta Sans\',sans-serif;">'
                f'📍 {sanitize_text(data.get("jurisdiction", "General"))}</h3>',
                unsafe_allow_html=True
            )
        with col2:
            status_color = {"Upcoming": "#2D3561", "Live": "#C62828", "Completed": "#0E6B06"}.get(
                status.split()[0] if status else "", "#5C5C7A"
            )
            st.markdown(
                f'<div style="background:{status_color}12;border:1px solid {status_color}30;'
                f'border-radius:20px;padding:6px 14px;text-align:center;margin-top:4px;">'
                f'<span style="color:{status_color};font-weight:700;font-size:0.85rem;">{status}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
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
