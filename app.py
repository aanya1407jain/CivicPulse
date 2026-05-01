"""
CivicPulse India — 2026 Assembly Intelligence
=============================================
Pincode-first entry: user enters PIN / state → everything personalises.
Dark dashboard UI. Real-time ECI results via election_scraper.
"""

import streamlit as st
import logging
from dotenv import load_dotenv

load_dotenv()

from config.settings import GOOGLE_API_KEY, GEMINI_MODEL, GEMINI_MAX_TOKENS, INDIA
from regions import get_region_handler
from services.election_scraper import (
    fetch_results, get_state_code_from_location, STATE_MOCK
)
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
from utils.date_utils import get_election_status
from utils.validators import validate_location_input

logger = logging.getLogger(__name__)

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CivicPulse | India Election Intelligence",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── SESSION INIT ──────────────────────────────────────────────────────────────
def init_session() -> None:
    defaults = {
        "location":      "",
        "state_code":    "",
        "election_data": None,
        "handler":       None,
        "country_code":  "IN",
        "checklist":     {},
        "ai_messages":   [],
        "saved_pins":    ["700001 — West Bengal", "600001 — Tamil Nadu"],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── PROCESS LOCATION INPUT ────────────────────────────────────────────────────
def process_location(location: str) -> bool:
    """Parse input, resolve handler + election data. Returns True on success."""
    if not validate_location_input(location):
        return False
    loc_parsed   = parse_location(location)
    country_code = detect_country_from_input(location)
    handler      = get_region_handler(country_code)
    election_data = handler.get_election_data(loc_parsed["normalized"])
    state_code   = get_state_code_from_location(loc_parsed["normalized"])

    st.session_state["location"]      = location
    st.session_state["state_code"]    = state_code
    st.session_state["country_code"]  = country_code
    st.session_state["election_data"] = election_data
    st.session_state["handler"]       = handler
    return True


# ── GEMINI ────────────────────────────────────────────────────────────────────
def _call_gemini(question: str, election_data: dict) -> str:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        ctx = (
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
    if not GOOGLE_API_KEY:
        st.info("💡 Add `GOOGLE_API_KEY` to `.env` to enable the AI assistant.")
        return
    st.markdown("#### 🤖 AI Voter Assistant (Gemini)")
    for msg in st.session_state["ai_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if q := st.chat_input("Ask about voting, ID, booths…"):
        st.session_state["ai_messages"].append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(q)
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                ans = _call_gemini(q, election_data)
            st.markdown(ans)
        st.session_state["ai_messages"].append({"role": "assistant", "content": ans})


# ── TOP NAV ───────────────────────────────────────────────────────────────────
def render_topnav() -> None:
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


# ── PINCODE ENTRY SCREEN ──────────────────────────────────────────────────────
def render_pincode_entry() -> None:
    """Full-screen entry shown when no location is set."""
    st.markdown(
        """
        <div style="max-width:540px;margin:3rem auto 0;text-align:center;padding:0 1rem;">
            <div style="font-size:3rem;margin-bottom:1rem;">🗳️</div>
            <div style="font-size:1.9rem;font-weight:800;color:#E8EAF0;
                        font-family:'DM Sans',sans-serif;margin-bottom:8px;line-height:1.2;">
                Your India Election Dashboard
            </div>
            <div style="color:#9BA3BC;font-size:0.95rem;margin-bottom:2rem;line-height:1.6;">
                Enter your <b style="color:#FF6B1A;">6-digit PIN code</b> or
                <b style="color:#FF6B1A;">state name</b> to load live results,
                your booth, voter checklist, candidate profiles and more.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Center-aligned input
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        loc = st.text_input(
            "PIN / State",
            label_visibility="collapsed",
            placeholder="e.g. 700001  or  West Bengal",
            key="entry_location",
        )
        clicked = st.button("🔍  Search", type="primary", use_container_width=True)

        if clicked or loc:
            if validate_location_input(loc):
                if process_location(loc):
                    st.rerun()
            elif loc:
                st.error("Enter a valid 6-digit PIN code or an Indian state name.")

        st.divider()
        st.markdown(
            '<div style="text-align:center;font-size:0.75rem;color:#5C6480;'
            'font-weight:600;letter-spacing:0.08em;text-transform:uppercase;'
            'margin-bottom:8px;">Quick Access</div>',
            unsafe_allow_html=True,
        )
        # Quick-access saved pins
        pin_cols = st.columns(len(st.session_state["saved_pins"]))
        for i, pin in enumerate(st.session_state["saved_pins"]):
            with pin_cols[i]:
                if st.button(pin, key=f"quick_{i}", use_container_width=True):
                    code = pin.split(" — ")[0].strip()
                    if process_location(code):
                        st.rerun()


# ── STAT TILES ────────────────────────────────────────────────────────────────
def render_stat_tiles(results: dict, election_data: dict) -> None:
    """4 big-number tiles from live results data."""
    parties   = results.get("parties", [])
    total     = results.get("total_seats", 294)
    majority  = results.get("majority", 148)

    # Leading party seats
    if parties:
        top_party  = max(parties, key=lambda p: p.get("total", p.get("won", 0) + p.get("leading", 0)))
        top_seats  = top_party.get("total", top_party.get("won", 0) + top_party.get("leading", 0))
        top_name   = top_party["name"]
        state_abbr = results.get("state", "")[:2]
    else:
        top_seats, top_name, state_abbr = "—", "N/A", ""

    # Days to counting
    from utils.date_utils import days_until
    count_day = election_data.get("counting_day", "2026-05-04")
    days_left = days_until(count_day)
    days_str  = str(abs(days_left)) if days_left is not None else "—"
    days_sub  = f"days · {count_day[-5:]}" if days_left and days_left > 0 else "Counting Day"

    # Turnout (from state data)
    from services.election_scraper import STATE_MOCK
    sc = st.session_state.get("state_code", "WB")
    turnout = STATE_MOCK.get(sc, {}).get("voter_turnout_2021",
              election_data.get("key_dates", {}).get("last_turnout", "~74%"))

    # Exit poll agencies tracked
    polls = st.session_state.get("exit_polls", DEFAULT_EXIT_POLLS)

    tiles = [
        ("cp-tile-green",  "Seats Won",   str(top_seats), f"{top_name} · {results.get('state','')[:2]}"),
        ("cp-tile-blue",   "Counting In", days_str,        days_sub),
        ("cp-tile-yellow", "Turnout",     str(turnout),    "last election avg"),
        ("cp-tile-orange", "Exit Polls",  f"+{len(polls)}", "agencies tracked"),
    ]

    c1, c2, c3, c4 = st.columns(4)
    for col, (cls, label, value, sub) in zip([c1, c2, c3, c4], tiles):
        with col:
            st.markdown(
                f"""
                <div class="cp-stat-tile {cls}" aria-label="{label}: {value}">
                    <div class="cp-stat-label">{label}</div>
                    <div class="cp-stat-value">{value}</div>
                    <div class="cp-stat-sub">{sub}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ── CONSTITUENCY CARD ─────────────────────────────────────────────────────────
def render_constituency_card(results: dict, election_data: dict) -> None:
    jurisdiction = sanitize_text(election_data.get("jurisdiction", results.get("state", "India")))
    phase_info   = sanitize_text(election_data.get("election_type", "Assembly Election"))

    parties = results.get("parties", [])[:3]
    chips_html = '<div class="cp-party-chips">'
    chip_cls = ["cp-chip-aitc", "cp-chip-bjp", "cp-chip-oth"]
    for i, p in enumerate(parties):
        seats = p.get("total", p.get("won", 0) + p.get("leading", 0))
        cls   = chip_cls[i] if i < len(chip_cls) else "cp-chip-oth"
        chips_html += f'<span class="cp-chip {cls}">{sanitize_text(p["name"])} <b>{seats}</b></span>'
    chips_html += "</div>"

    menu_items = [
        ("📊", "Live Results"),
        ("☑️", "Voter Checklist"),
        ("🎯", "Election Quiz"),
        ("⭐", "Share Experience"),
    ]
    menu_html = "".join(
        f'<div class="cp-menu-item">'
        f'<div class="cp-menu-icon">{icon}</div>'
        f'<span class="cp-menu-text">{label}</span>'
        f'</div>'
        for icon, label in menu_items
    )

    st.markdown(
        f"""
        <div class="cp-constituency-card">
            <div class="cp-const-badge">My Constituency</div>
            <div class="cp-const-name">{jurisdiction}</div>
            <div class="cp-const-sub">{phase_info}</div>
            {chips_html}
            <div style="margin-top:6px;">{menu_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── PARTY STRENGTH BARS ───────────────────────────────────────────────────────
def render_party_strength(results: dict) -> None:
    total    = results.get("total_seats", 294)
    majority = results.get("majority", 148)
    parties  = results.get("parties", [])

    rows_html = ""
    for p in parties:
        seats = p.get("total", p.get("won", 0) + p.get("leading", 0))
        pct   = min((seats / total) * 100, 100) if total else 0
        color = p.get("color", "#9BA3BC")
        rows_html += f"""
        <div class="cp-party-row">
            <div class="cp-party-name">{sanitize_text(p['name'])}</div>
            <div class="cp-bar-wrap">
                <div class="cp-bar-fill" style="width:{pct:.1f}%;background:{color};"></div>
            </div>
            <div class="cp-bar-seats" style="color:{color};">{seats} seats</div>
        </div>
        """

    state_name = sanitize_text(results.get("state", "State"))
    st.markdown(
        f"""
        <div class="cp-section-card">
            <div class="cp-section-title">Party Strength — {state_name}</div>
            {rows_html}
            <div class="cp-majority-line">Majority mark: {majority} seats</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── EXIT POLL COMPACT ─────────────────────────────────────────────────────────
def render_exit_poll_compact() -> None:
    polls = st.session_state.get("exit_polls", DEFAULT_EXIT_POLLS)

    avg_aitc   = round(sum(p["aitc"] for p in polls) / len(polls)) if polls else 0
    avg_bjp    = round(sum(p["bjp"]  for p in polls) / len(polls)) if polls else 0
    avg_others = 294 - avg_aitc - avg_bjp

    rows_html = ""
    for p in polls[:4]:
        short = (p["agency"]
                 .replace("India Today - Axis My India", "India Today")
                 .replace("Republic TV - P-MARQ", "Republic P-MARQ")
                 .replace("Times Now - ETG", "Times Now ETG")
                 .replace("ABP News - CVoter", "ABP - CVoter"))
        others = max(0, 294 - p["aitc"] - p["bjp"])
        rows_html += (
            f'<tr>'
            f'<td>{sanitize_text(short)}</td>'
            f'<td class="val-aitc">{p["aitc"]}</td>'
            f'<td class="val-bjp">{p["bjp"]}</td>'
            f'<td class="val-other">{others}</td>'
            f'</tr>'
        )

    st.markdown(
        f"""
        <div class="cp-section-card">
            <div class="cp-section-title">Exit Poll Aggregator</div>
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
                        <th>Agency</th><th>AITC</th><th>BJP</th><th>OTHERS</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── DASHBOARD TAB ─────────────────────────────────────────────────────────────
def render_dashboard() -> None:
    data     = st.session_state["election_data"]
    handler  = st.session_state["handler"]
    sc       = st.session_state["state_code"]
    results  = fetch_results(sc)

    # Row 1 — constituency card + stat tiles
    left, right = st.columns([0.32, 0.68])
    with left:
        render_constituency_card(results, data)
    with right:
        render_stat_tiles(results, data)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # Row 2 — party bars + exit poll table
    col_a, col_b = st.columns([0.45, 0.55])
    with col_a:
        render_party_strength(results)
    with col_b:
        render_exit_poll_compact()

    # Footer
    st.markdown(
        f"""
        <div class="cp-footer">
            <span>Data: ECI Official · Updated: {results.get('last_updated','—')}</span>
            <a href="https://results.eci.gov.in/" target="_blank">
                results.eci.gov.in ↗
            </a>
            <span>Helpline: <b style="color:#FF6B1A;">{INDIA['VOTER_HELPLINE']}</b></span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── CHANGE LOCATION BAR ───────────────────────────────────────────────────────
def render_location_bar() -> None:
    """Small bar at the top of the loaded dashboard showing current location."""
    loc = st.session_state.get("location", "")
    sc  = st.session_state.get("state_code", "")
    data = st.session_state.get("election_data", {})
    jurisdiction = data.get("jurisdiction", loc) if data else loc

    col_info, col_change = st.columns([4, 1])
    with col_info:
        st.markdown(
            f'<div style="background:#181B26;border:1px solid rgba(255,255,255,0.08);'
            f'border-radius:8px;padding:8px 14px;display:flex;align-items:center;gap:10px;">'
            f'<span style="font-size:0.75rem;font-weight:700;color:#FF6B1A;">📍</span>'
            f'<span style="font-size:0.88rem;font-weight:600;color:#E8EAF0;">'
            f'{sanitize_text(jurisdiction)}'
            f'</span>'
            f'<span style="font-size:0.72rem;color:#5C6480;margin-left:4px;">'
            f'· {sanitize_text(loc)}'
            f'</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col_change:
        if st.button("📍 Change", use_container_width=True):
            # Clear location so entry screen shows
            st.session_state["location"]      = ""
            st.session_state["election_data"] = None
            st.session_state["handler"]       = None
            st.session_state["state_code"]    = ""
            st.rerun()


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main() -> None:
    init_session()
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)
    st.markdown(
        "<script>document.documentElement.setAttribute('lang','en');</script>",
        unsafe_allow_html=True,
    )

    render_topnav()

    # ── GATE: show entry screen if no location set ────────────────────────────
    if not st.session_state.get("election_data"):
        render_pincode_entry()
        return

    # ── Location set → show full dashboard ───────────────────────────────────
    render_location_bar()
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    data    = st.session_state["election_data"]
    handler = st.session_state["handler"]
    sc      = st.session_state["state_code"]
    loc     = st.session_state["location"]

    (
        tab_dashboard,
        tab_results,
        tab_map,
        tab_quiz,
        tab_guide,
        tab_candidates,
        tab_india_map,
        tab_trends,
        tab_polls,
        tab_experience,
        tab_notifications,
        tab_ai,
    ) = st.tabs([
        "Dashboard",
        "Results",
        "Map",
        "Quiz",
        "📋 Voter Guide",
        "👤 Candidates",
        "🗺️ India Map",
        "📈 Trends",
        "📡 Exit Polls",
        "🏛️ Share Exp.",
        "🔔 Notifications",
        "🤖 AI",
    ])

    with tab_dashboard:
        render_dashboard()

    with tab_results:
        render_election_results(state=loc)

    with tab_map:
        render_map_view(data, loc)

    with tab_quiz:
        render_election_quiz()

    with tab_guide:
        c1, c2 = st.columns([1.5, 1])
        with c1:
            render_checklist(handler, data)
        with c2:
            render_timeline(handler, data)

    with tab_candidates:
        render_candidate_profiles()

    with tab_india_map:
        render_india_map()

    with tab_trends:
        render_historical_trends()

    with tab_polls:
        render_exit_poll_aggregator()

    with tab_experience:
        render_polling_experience()

    with tab_notifications:
        render_notification_panel(data, handler)

    with tab_ai:
        render_ai_assistant(data)


if __name__ == "__main__":
    main()
