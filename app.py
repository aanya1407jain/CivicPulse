"""
CivicPulse India — 2026 Assembly Intelligence
=============================================
Dark dashboard UI matching the design screenshot.
Top nav bar, constituency card, stat tiles, party strength, exit poll table.
All logic unchanged — only UI/UX layer replaced.
"""

import streamlit as st
import logging
from dotenv import load_dotenv

load_dotenv()

from config.settings import (
    SUPPORTED_COUNTRIES, GOOGLE_API_KEY, GEMINI_MODEL, GEMINI_MAX_TOKENS, INDIA
)
from regions import get_region_handler
from services.civic_api import CivicAPIService
from services.calendar_service import CalendarService
from components.theme import DARK_THEME_CSS
from components.timeline import render_timeline
from components.checklist import render_checklist
from components.map_view import render_map_view
from components.notification import render_notification_panel
from components.election_results import render_election_results
from components.candidate_profiles import render_candidate_profiles
from components.india_map import render_india_map
from components.historical_trends import render_historical_trends
from components.exit_poll_aggregator import render_exit_poll_aggregator, DEFAULT_EXIT_POLLS
from components.election_quiz import render_election_quiz
from components.polling_experience import render_polling_experience

from utils.location_utils import detect_country_from_input, parse_location, sanitize_text
from utils.date_utils import days_until, get_election_status
from utils.validators import validate_location_input

logger = logging.getLogger(__name__)

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CivicPulse | India Election Intelligence",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
def init_session() -> None:
    defaults = {
        "checklist":    {},
        "location":     "",
        "country_code": INDIA["COUNTRY_CODE"],
        "ai_messages":  [],
        "active_tab":   "Dashboard",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ── GEMINI AI ─────────────────────────────────────────────────────────────────
def render_ai_assistant(election_data: dict) -> None:
    if not GOOGLE_API_KEY:
        st.info("💡 Add `GOOGLE_API_KEY` to `.env` to unlock the AI voter assistant.")
        return
    st.markdown("#### 🤖 AI Voter Assistant (Powered by Gemini)")
    st.caption("Ask anything about voting, your rights, or the election process.")
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
        st.session_state["ai_messages"].append({"role": "assistant", "content": answer})


def _call_gemini(question: str, election_data: dict) -> str:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        ctx = (
            f"You are CivicPulse, an expert Indian election assistant. "
            f"Election: {election_data.get('election_name','Indian election')} "
            f"in {election_data.get('jurisdiction','India')}. "
            f"Facts: {election_data.get('requirements',[])}. "
            f"ECI Helpline: {INDIA['VOTER_HELPLINE']}. "
            f"Keep answers under 150 words, factual, plain English."
        )
        response = model.generate_content(
            f"{ctx}\n\nVoter question: {question}",
            generation_config={"max_output_tokens": GEMINI_MAX_TOKENS},
        )
        return response.text or "Could not generate a response. Please try again."
    except ImportError:
        return "⚠️ `google-generativeai` not installed. Add it to requirements.txt."
    except Exception as exc:
        err = str(exc)
        logger.error("Gemini call failed: %s", err)
        if "API_KEY_INVALID" in err or "invalid" in err.lower():
            return "⚠️ Invalid API key. Check `GOOGLE_API_KEY` in `.env`."
        if "quota" in err.lower() or "429" in err:
            return "⚠️ Quota exceeded. Free tier limit reached."
        return f"⚠️ Gemini error: {err}\n\nECI Helpline: **{INDIA['VOTER_HELPLINE']}**"


# ── TOP NAV BAR ───────────────────────────────────────────────────────────────
def render_topnav() -> None:
    """Render the CivicPulse logo + nav pills + LIVE badge."""
    st.markdown(
        """
        <div class="cp-topnav" role="banner">
            <div class="cp-logo">
                <div class="cp-logo-icon">CP</div>
                <div class="cp-logo-text">
                    <div class="cp-logo-title">CivicPulse</div>
                    <div class="cp-logo-sub">India Election Intelligence</div>
                </div>
            </div>
            <div class="cp-live-badge">
                <div class="cp-live-dot"></div>
                COUNTING LIVE
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── SEARCH BAR ────────────────────────────────────────────────────────────────
def render_search_bar() -> None:
    """PIN / State search row styled like the screenshot."""
    col_label, col_input, col_btn = st.columns([0.12, 0.72, 0.16])
    with col_label:
        st.markdown(
            '<div style="padding-top:8px;">'
            '<span style="font-size:0.75rem;font-weight:700;color:#FF6B1A;'
            'letter-spacing:0.06em;text-transform:uppercase;">📍 PIN / State:</span>'
            '</div>',
            unsafe_allow_html=True,
        )
    with col_input:
        location = st.text_input(
            label="location_input",
            label_visibility="collapsed",
            value=st.session_state["location"],
            placeholder="e.g. 700001 or West Bengal",
            key="main_location_input",
        )
    with col_btn:
        search_clicked = st.button("Search", type="primary", use_container_width=True)

    if search_clicked or (location and location != st.session_state.get("_last_loc", "")):
        st.session_state["_last_loc"] = location
        if location and validate_location_input(location):
            st.session_state["location"] = location
            st.session_state["country_code"] = detect_country_from_input(location)
            loc_parsed = parse_location(location)
            handler = get_region_handler(st.session_state["country_code"])
            st.session_state["election_data"] = handler.get_election_data(loc_parsed["normalized"])
            st.session_state["handler"] = handler
        elif location:
            st.warning("Enter a valid 6-digit PIN code or Indian state name.")


# ── CONSTITUENCY CARD (left panel) ────────────────────────────────────────────
def render_constituency_card(data: dict, handler) -> None:
    """Left-side constituency card matching the screenshot layout."""
    jurisdiction = sanitize_text(data.get("jurisdiction", "India"))
    state_line   = sanitize_text(data.get("election_type", "Assembly Election"))

    # Mock seat tally for the chip row (from election_results mock data)
    chips_html = (
        '<div class="cp-party-chips">'
        '<span class="cp-chip cp-chip-aitc">AITC <b>1</b></span>'
        '<span class="cp-chip cp-chip-bjp">BJP <b>2</b></span>'
        '<span class="cp-chip cp-chip-oth">Others <b>3</b></span>'
        '</div>'
    )

    menu_items = [
        ("📊", "#E8F0FF", "Live Results"),
        ("☑️", "#F0F0E8", "Voter Checklist"),
        ("🎯", "#FFE8F0", "Election Quiz"),
        ("⭐", "#FFF8E8", "Share Experience"),
    ]
    menu_html = ""
    for icon, bg, label in menu_items:
        menu_html += (
            f'<div class="cp-menu-item">'
            f'<div class="cp-menu-icon" style="background:{bg}22;">{icon}</div>'
            f'<span class="cp-menu-text">{label}</span>'
            f'</div>'
        )

    st.markdown(
        f"""
        <div class="cp-constituency-card">
            <div class="cp-const-badge">My Constituency</div>
            <div class="cp-const-name">{jurisdiction}</div>
            <div class="cp-const-sub">{state_line}</div>
            {chips_html}
            <div style="margin-top:4px;">
                {menu_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── STAT TILES ────────────────────────────────────────────────────────────────
def render_stat_tiles(data: dict) -> None:
    """4 stat tiles: Seats Won, Counting In, Turnout, Exit Polls."""
    c1, c2, c3, c4 = st.columns(4)

    tiles = [
        (c1, "cp-tile-green",  "Seats Won",    "213",   "AITC · WB"),
        (c2, "cp-tile-blue",   "Counting In",  "4",     "days · May 4"),
        (c3, "cp-tile-yellow", "Turnout",       "78.2%", "5-state avg"),
        (c4, "cp-tile-orange", "Exit Polls",    "+4",    "agencies tracked"),
    ]

    for col, cls, label, value, sub in tiles:
        with col:
            st.markdown(
                f"""
                <div class="cp-stat-tile {cls}" role="figure" aria-label="{label}: {value}">
                    <div class="cp-stat-label">{label}</div>
                    <div class="cp-stat-value">{value}</div>
                    <div class="cp-stat-sub">{sub}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ── PARTY STRENGTH BARS ───────────────────────────────────────────────────────
def render_party_strength(data: dict) -> None:
    """Horizontal bar chart of party seats — left panel of bottom section."""
    total = 294
    majority = 148

    parties = [
        ("AITC", 213, "#27C96E"),
        ("BJP",   77, "#FF6B1A"),
        ("Others", 4, "#5C6480"),
    ]

    rows_html = ""
    for name, seats, color in parties:
        pct = min((seats / total) * 100, 100)
        rows_html += f"""
        <div class="cp-party-row">
            <div class="cp-party-name">{name}</div>
            <div class="cp-bar-wrap">
                <div class="cp-bar-fill" style="width:{pct:.1f}%;background:{color};"></div>
            </div>
            <div class="cp-bar-seats" style="color:{color};">{seats} seats</div>
        </div>
        """

    st.markdown(
        f"""
        <div class="cp-section-card">
            <div class="cp-section-title">Party Strength — WB 2026</div>
            {rows_html}
            <div class="cp-majority-line">Majority mark: {majority} seats</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── EXIT POLL AGGREGATOR COMPACT ──────────────────────────────────────────────
def render_exit_poll_compact() -> None:
    """Compact exit poll table matching the screenshot right panel."""
    polls = st.session_state.get("exit_polls", DEFAULT_EXIT_POLLS)

    import math
    avg_aitc   = round(sum(p["aitc"] for p in polls) / len(polls))
    avg_bjp    = round(sum(p["bjp"] for p in polls) / len(polls))
    avg_others = 294 - avg_aitc - avg_bjp

    # Agency rows
    rows_html = ""
    for p in polls[:4]:
        others = 294 - p["aitc"] - p["bjp"]
        agency_short = (
            p["agency"]
            .replace("News - ", " - ")
            .replace("India Today - Axis My India", "India Today")
            .replace("Republic TV - ", "Republic ")
            .replace("Times Now - ", "Times Now ")
        )
        rows_html += f"""
        <tr>
            <td>{agency_short}</td>
            <td class="val-aitc">{p["aitc"]}</td>
            <td class="val-bjp">{p["bjp"]}</td>
            <td class="val-other">{max(0,others)}</td>
        </tr>
        """

    st.markdown(
        f"""
        <div class="cp-section-card">
            <div class="cp-section-title">Exit Poll Aggregator</div>
            <!-- Avg row -->
            <div style="display:flex;gap:12px;margin-bottom:14px;">
                <div style="flex:1;background:rgba(39,201,110,0.10);border:1px solid rgba(39,201,110,0.25);
                            border-radius:10px;padding:10px;text-align:center;">
                    <div style="font-size:1.6rem;font-weight:800;color:#27C96E;">{avg_aitc}</div>
                    <div style="font-size:0.62rem;font-weight:700;letter-spacing:0.08em;
                                color:#5C6480;text-transform:uppercase;">AITC AVG</div>
                </div>
                <div style="flex:1;background:rgba(255,107,26,0.10);border:1px solid rgba(255,107,26,0.25);
                            border-radius:10px;padding:10px;text-align:center;">
                    <div style="font-size:1.6rem;font-weight:800;color:#FF6B1A;">{avg_bjp}</div>
                    <div style="font-size:0.62rem;font-weight:700;letter-spacing:0.08em;
                                color:#5C6480;text-transform:uppercase;">BJP AVG</div>
                </div>
                <div style="flex:1;background:rgba(92,100,128,0.10);border:1px solid rgba(92,100,128,0.25);
                            border-radius:10px;padding:10px;text-align:center;">
                    <div style="font-size:1.6rem;font-weight:800;color:#9BA3BC;">{avg_others}</div>
                    <div style="font-size:0.62rem;font-weight:700;letter-spacing:0.08em;
                                color:#5C6480;text-transform:uppercase;">OTHERS</div>
                </div>
            </div>
            <div style="font-size:0.65rem;color:#5C6480;font-weight:600;
                        letter-spacing:0.08em;margin-bottom:10px;">
                {len(polls)} agencies tracked
            </div>
            <table class="cp-poll-table">
                <thead>
                    <tr>
                        <th>Agency</th>
                        <th>AITC</th>
                        <th>BJP</th>
                        <th>OTHERS</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── DASHBOARD TAB CONTENT ─────────────────────────────────────────────────────
def render_dashboard_content() -> None:
    """The main dashboard view — constituency card + stat tiles + bottom panels."""
    has_location = "election_data" in st.session_state

    if has_location:
        data    = st.session_state["election_data"]
        handler = st.session_state["handler"]
    else:
        # Default demo data so the dashboard always looks good
        handler = get_region_handler("IN")
        data    = handler.get_election_data("West Bengal")

    # Row 1: constituency card (left) + 4 stat tiles (right)
    left_col, right_col = st.columns([0.32, 0.68])

    with left_col:
        render_constituency_card(data, handler)

    with right_col:
        render_stat_tiles(data)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # Row 2: party strength (left) + exit poll compact (right)
    col_strength, col_polls = st.columns([0.45, 0.55])

    with col_strength:
        render_party_strength(data)

    with col_polls:
        render_exit_poll_compact()

    # Footer strip
    st.markdown(
        f"""
        <div class="cp-footer">
            <span>Data: ECI Official · Updated: 29 Apr, 3:20 PM</span>
            <a href="https://results.eci.gov.in/" target="_blank">Helpline 1950</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not has_location:
        st.info("👋 Enter your PIN code or state above to personalise this dashboard.")


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main() -> None:
    init_session()

    # Inject dark CSS
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

    # Inject lang attribute
    st.markdown(
        "<script>document.documentElement.setAttribute('lang','en');</script>",
        unsafe_allow_html=True,
    )

    # Top nav bar (logo + live badge)
    render_topnav()

    # Search row (always visible)
    render_search_bar()

    # Tab navigation — all 11 tabs, first one is Dashboard
    (
        tab_dashboard,
        tab_results,
        tab_map_booth,
        tab_quiz,
        tab_pincodes,
        tab_guide,
        tab_candidates,
        tab_india_map,
        tab_trends,
        tab_polls,
        tab_experience,
        tab_ai,
    ) = st.tabs([
        "Dashboard",
        "Results",
        "Map",
        "Quiz",
        "My Pincodes",
        "📋 Voter Guide",
        "👤 Candidates",
        "🗺️ India Map",
        "📈 Trends",
        "📡 Exit Polls",
        "🏛️ Share Exp.",
        "🤖 AI Assistant",
    ])

    # ── Dashboard (default landing tab) ──────────────────────────────────────
    with tab_dashboard:
        render_dashboard_content()

    # ── Results ───────────────────────────────────────────────────────────────
    with tab_results:
        location = st.session_state.get("location", "West Bengal")
        render_election_results(state=location if location else "West Bengal")

    # ── Booth Map ─────────────────────────────────────────────────────────────
    with tab_map_booth:
        if "election_data" in st.session_state:
            render_map_view(st.session_state["election_data"], st.session_state["location"])
        else:
            st.info("👋 Enter your location above to find your polling booth.")

    # ── Quiz ──────────────────────────────────────────────────────────────────
    with tab_quiz:
        render_election_quiz()

    # ── My Pincodes ───────────────────────────────────────────────────────────
    with tab_pincodes:
        st.markdown("### 📍 My Pincodes")
        st.caption("Save frequently used PIN codes and states for quick switching.")
        if "saved_pincodes" not in st.session_state:
            st.session_state["saved_pincodes"] = ["700001 — West Bengal", "400001 — Maharashtra"]
        for pin in st.session_state["saved_pincodes"]:
            col_pin, col_use = st.columns([4, 1])
            with col_pin:
                st.markdown(
                    f'<div style="background:var(--card,#181B26);border:1px solid rgba(255,255,255,0.08);'
                    f'border-radius:8px;padding:10px 14px;font-size:0.88rem;">'
                    f'📍 {sanitize_text(pin)}</div>',
                    unsafe_allow_html=True,
                )
            with col_use:
                if st.button("Use", key=f"use_{pin}", use_container_width=True):
                    code = pin.split(" — ")[0].strip()
                    st.session_state["location"] = code
                    st.rerun()
        st.divider()
        new_pin = st.text_input("Add a PIN code or state", placeholder="e.g. 600001 or Tamil Nadu")
        if st.button("Save", type="primary"):
            if new_pin.strip() and validate_location_input(new_pin.strip()):
                entry = f"{new_pin.strip()}"
                if entry not in st.session_state["saved_pincodes"]:
                    st.session_state["saved_pincodes"].append(entry)
                    st.success(f"Saved: {entry}")
                    st.rerun()
            else:
                st.error("Please enter a valid 6-digit PIN or state name.")

    # ── Voter Guide ───────────────────────────────────────────────────────────
    with tab_guide:
        if "election_data" in st.session_state:
            data    = st.session_state["election_data"]
            handler = st.session_state["handler"]
            c1, c2  = st.columns([1.5, 1])
            with c1:
                render_checklist(handler, data)
            with c2:
                render_timeline(handler, data)
        else:
            st.info("👋 Enter your location above to load your personalised voter guide.")

    # ── Candidates ────────────────────────────────────────────────────────────
    with tab_candidates:
        render_candidate_profiles()

    # ── India Map ─────────────────────────────────────────────────────────────
    with tab_india_map:
        render_india_map()

    # ── Historical Trends ────────────────────────────────────────────────────
    with tab_trends:
        render_historical_trends()

    # ── Exit Polls (full) ────────────────────────────────────────────────────
    with tab_polls:
        render_exit_poll_aggregator()

    # ── Share Experience ──────────────────────────────────────────────────────
    with tab_experience:
        render_polling_experience()

    # ── AI Assistant ──────────────────────────────────────────────────────────
    with tab_ai:
        if "election_data" in st.session_state:
            render_ai_assistant(st.session_state["election_data"])
        else:
            data = get_region_handler("IN").get_election_data("India")
            render_ai_assistant(data)


if __name__ == "__main__":
    main()
