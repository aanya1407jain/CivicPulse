"""
CivicPulse India — 2026 Assembly Intelligence
==============================================
Entry point. All heavy render logic lives in views/ and components/.
"""

import streamlit as st
import logging
from dotenv import load_dotenv

load_dotenv()

from config.settings import GOOGLE_API_KEY, GEMINI_MODEL, GEMINI_MAX_TOKENS, INDIA
from regions import get_region_handler
from services.election_scraper import fetch_results, get_state_code_from_location
from components.theme import DARK_THEME_CSS
from components.timeline import render_timeline
from components.checklist import render_checklist
from components.map_view import render_map_view
from components.notification import render_notification_panel
from components.election_results import render_election_results
from components.candidate_profiles import render_candidate_profiles
from components.india_map import render_india_map
from components.historical_trends import render_historical_trends
from components.exit_poll_aggregator import render_exit_poll_aggregator
from components.election_quiz import render_election_quiz
from components.polling_experience import render_polling_experience
from components.language_selector import render_language_selector, T

from views.dashboard import render_dashboard
from utils.location_utils import detect_country_from_input, parse_location, sanitize_text
from utils.validators import validate_location_input

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="CivicPulse | India Election Intelligence",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def init_session() -> None:
    defaults = {
        "location": "", "state_code": "", "election_data": None,
        "handler": None, "country_code": "IN", "checklist": {},
        "ai_messages": [], "saved_pins": ["700001 — West Bengal", "600001 — Tamil Nadu"],
        "gemini_token_count": 0, "language": "en",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def process_location(location: str) -> bool:
    if not validate_location_input(location):
        return False
    loc_parsed    = parse_location(location)
    country_code  = detect_country_from_input(location)
    handler       = get_region_handler(country_code)
    election_data = handler.get_election_data(loc_parsed["normalized"])
    state_code    = get_state_code_from_location(loc_parsed["normalized"])
    st.session_state.update({
        "location": location, "state_code": state_code,
        "country_code": country_code, "election_data": election_data,
        "handler": handler,
    })
    return True


def _call_gemini(question: str, election_data: dict) -> str:
    BUDGET = 20
    count  = st.session_state.get("gemini_token_count", 0)
    if count >= BUDGET:
        return (
            f"⚠️ Session AI limit reached ({BUDGET} queries). "
            f"Refresh to reset, or call the ECI Helpline: **{INDIA['VOTER_HELPLINE']}**"
        )
    st.session_state["gemini_token_count"] = count + 1
    try:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        ctx   = (
            f"You are CivicPulse, an Indian election assistant. "
            f"Election: {election_data.get('election_name','Indian election')} "
            f"in {election_data.get('jurisdiction','India')}. "
            f"ECI Helpline: {INDIA['VOTER_HELPLINE']}. Under 150 words."
        )
        resp = model.generate_content(
            f"{ctx}\n\nVoter question: {question}",
            generation_config={"max_output_tokens": GEMINI_MAX_TOKENS},
        )
        return resp.text or "Could not generate a response."
    except ImportError:
        return "⚠️ `google-generativeai` not installed."
    except Exception as exc:
        return f"⚠️ Error: {exc}\n\nECI Helpline: **{INDIA['VOTER_HELPLINE']}**"


def render_ai_assistant(election_data: dict) -> None:
    remaining = 20 - st.session_state.get("gemini_token_count", 0)
    if not GOOGLE_API_KEY:
        st.info(T("💡 Add GOOGLE_API_KEY to .env to enable the AI assistant."))
        return
    st.markdown(f"#### 🤖 {T('AI Voter Assistant')} (Gemini) · *{remaining} {T('queries left')}*")
    for msg in st.session_state["ai_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if q := st.chat_input(T("Ask about voting, ID, booths…")):
        st.session_state["ai_messages"].append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(q)
        with st.chat_message("assistant"):
            with st.spinner(T("Thinking…")):
                ans = _call_gemini(q, election_data)
            st.markdown(ans)
        st.session_state["ai_messages"].append({"role": "assistant", "content": ans})


def render_topnav() -> None:
    sub = T("India Election Intelligence")
    badge = T("COUNTING LIVE")
    st.markdown(
        f"""
        <div class="cp-topnav" role="banner">
            <div class="cp-logo">
                <div class="cp-logo-icon">CP</div>
                <div class="cp-logo-text">
                    <div class="cp-logo-title">CivicPulse</div>
                    <div class="cp-logo-sub">{sub}</div>
                </div>
            </div>
            <div class="cp-live-badge">
                <div class="cp-live-dot"></div>
                {badge}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_pincode_entry() -> None:
    headline   = T("Your India Election Dashboard")
    body       = T("Enter your 6-digit PIN code or state name to load live results, your booth, voter checklist, candidate profiles and more.")
    pin_label  = T("6-digit PIN code")
    state_label = T("state name")
    quick_access = T("Quick Access")
    search_btn = T("Search")

    st.markdown(
        f"""
        <div style="max-width:540px;margin:3rem auto 0;text-align:center;padding:0 1rem;">
            <div style="font-size:3rem;margin-bottom:1rem;">🗳️</div>
            <div style="font-size:1.9rem;font-weight:800;color:#E8EAF0;
                        font-family:'DM Sans',sans-serif;margin-bottom:8px;line-height:1.2;">
                {headline}
            </div>
            <div style="color:#9BA3BC;font-size:0.95rem;margin-bottom:2rem;line-height:1.6;">
                {body}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        loc     = st.text_input("PIN / State", label_visibility="collapsed",
                                placeholder=T("e.g. 700001  or  West Bengal"), key="entry_location")
        clicked = st.button(f"🔍  {search_btn}", type="primary", use_container_width=True)
        if clicked or loc:
            if validate_location_input(loc):
                if process_location(loc):
                    st.rerun()
            elif loc:
                st.error(T("Enter a valid 6-digit PIN code or an Indian state name."))
        st.divider()
        st.markdown(
            f'<div style="text-align:center;font-size:0.75rem;color:#5C6480;'
            f'font-weight:600;letter-spacing:0.08em;text-transform:uppercase;'
            f'margin-bottom:8px;">{quick_access}</div>',
            unsafe_allow_html=True,
        )
        pin_cols = st.columns(len(st.session_state["saved_pins"]))
        for i, pin in enumerate(st.session_state["saved_pins"]):
            with pin_cols[i]:
                if st.button(pin, key=f"quick_{i}", use_container_width=True):
                    if process_location(pin.split(" — ")[0].strip()):
                        st.rerun()


def render_location_bar() -> None:
    data         = st.session_state.get("election_data", {})
    jurisdiction = data.get("jurisdiction", st.session_state.get("location", "")) if data else ""
    col_info, col_lang, col_change = st.columns([3, 1, 1])
    with col_info:
        st.markdown(
            f'<div style="background:#181B26;border:1px solid rgba(255,255,255,0.08);'
            f'border-radius:8px;padding:8px 14px;display:flex;align-items:center;gap:10px;">'
            f'<span style="font-size:0.75rem;font-weight:700;color:#FF6B1A;">📍</span>'
            f'<span style="font-size:0.88rem;font-weight:600;color:#E8EAF0;">'
            f'{sanitize_text(jurisdiction)}</span>'
            f'<span style="font-size:0.72rem;color:#5C6480;margin-left:4px;">'
            f'· {sanitize_text(st.session_state.get("location",""))}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col_lang:
        render_language_selector()
    with col_change:
        if st.button(f"📍 {T('Change')}", use_container_width=True):
            for k in ("location", "election_data", "handler", "state_code"):
                st.session_state[k] = None if k != "location" else ""
            st.rerun()


def main() -> None:
    init_session()
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)
    st.markdown("<script>document.documentElement.setAttribute('lang','en');</script>",
                unsafe_allow_html=True)
    render_topnav()

    if not st.session_state.get("election_data"):
        render_pincode_entry()
        return

    render_location_bar()
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    data    = st.session_state["election_data"]
    handler = st.session_state["handler"]
    sc      = st.session_state["state_code"]
    loc     = st.session_state["location"]

    (
        tab_dashboard, tab_results, tab_map, tab_quiz, tab_guide,
        tab_candidates, tab_india_map, tab_trends, tab_polls,
        tab_experience, tab_notifications, tab_ai,
    ) = st.tabs([
        T("Dashboard"), T("Results"), T("Map"), T("Quiz"), f"📋 {T('Voter Guide')}",
        f"👤 {T('Candidates')}", f"🗺️ {T('India Map')}", f"📈 {T('Trends')}", f"📡 {T('Exit Polls')}",
        f"🏛️ {T('Share Exp.')}", f"🔔 {T('Notifications')}", f"🤖 {T('AI')}",
    ])

    with tab_dashboard:   render_dashboard()
    with tab_results:     render_election_results(state=loc)
    with tab_map:         render_map_view(data, loc)
    with tab_quiz:        render_election_quiz()
    with tab_guide:
        c1, c2 = st.columns([1.5, 1])
        with c1: render_checklist(handler, data)
        with c2: render_timeline(handler, data)
    with tab_candidates:  render_candidate_profiles()
    with tab_india_map:   render_india_map()
    with tab_trends:      render_historical_trends()
    with tab_polls:       render_exit_poll_aggregator()
    with tab_experience:  render_polling_experience()
    with tab_notifications: render_notification_panel(data, handler)
    with tab_ai:          render_ai_assistant(data)


if __name__ == "__main__":
    main()
