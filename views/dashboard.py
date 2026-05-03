"""
CivicPulse — Dashboard View
============================
Houses all dashboard-specific render functions extracted from app.py.
Keeps app.py under 100 lines by isolating:
  • render_dashboard()
  • render_stat_tiles()
  • render_constituency_card()
  • render_party_strength()
  • render_exit_poll_compact()
"""

from __future__ import annotations
import streamlit as st

from config.settings import INDIA, INDIA_CONSTANTS
from services.election_scraper import fetch_results, STATE_MOCK
from components.exit_poll_aggregator import DEFAULT_EXIT_POLLS
from components.language_selector import T
from utils.location_utils import sanitize_text


# ── STAT TILES ────────────────────────────────────────────────────────────────

def render_stat_tiles(results: dict, election_data: dict) -> None:
    """4 big-number KPI tiles built from live results data."""
    parties  = results.get("parties", [])
    total    = results.get("total_seats", 294)

    if parties:
        top_party = max(parties, key=lambda p: p.get("total", p.get("won", 0) + p.get("leading", 0)))
        top_seats = top_party.get("total", top_party.get("won", 0) + top_party.get("leading", 0))
        top_name  = top_party["name"]
    else:
        top_seats, top_name = "—", "N/A"

    from utils.date_utils import days_until
    count_day = election_data.get("counting_day", "2026-05-04")
    days_left = days_until(count_day)
    days_str  = str(abs(days_left)) if days_left is not None else "—"
    days_sub  = f"{T('days')} · {count_day[-5:]}" if days_left and days_left > 0 else T("Counting Day")

    sc      = st.session_state.get("state_code", "WB")
    turnout = STATE_MOCK.get(sc, {}).get(
        "voter_turnout_2021",
        election_data.get("key_dates", {}).get("last_turnout", "~74%"),
    )

    polls = st.session_state.get("exit_polls", DEFAULT_EXIT_POLLS)

    tiles = [
        ("cp-tile-green",  T("Seats Won"),    str(top_seats), f"{top_name} · {results.get('state', '')[:2]}"),
        ("cp-tile-blue",   T("Counting In"),  days_str,        days_sub),
        ("cp-tile-yellow", T("Turnout"),       str(turnout),    T("last election avg")),
        ("cp-tile-orange", T("Exit Polls"),    f"+{len(polls)}", T("agencies tracked")),
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
    """Compact card showing constituency, ruling chips, and quick-nav menu."""
    jurisdiction = sanitize_text(election_data.get("jurisdiction", results.get("state", "India")))
    phase_info   = sanitize_text(election_data.get("election_type", "Assembly Election"))

    parties    = results.get("parties", [])[:3]
    chip_cls   = ["cp-chip-aitc", "cp-chip-bjp", "cp-chip-oth"]
    chips_html = '<div class="cp-party-chips">'
    for i, p in enumerate(parties):
        seats = p.get("total", p.get("won", 0) + p.get("leading", 0))
        cls   = chip_cls[i] if i < len(chip_cls) else "cp-chip-oth"
        chips_html += f'<span class="cp-chip {cls}">{sanitize_text(p["name"])} <b>{seats}</b></span>'
    chips_html += "</div>"

    menu_items = [
        ("📊", T("Live Results")),
        ("☑️", T("Voter Checklist")),
        ("🎯", T("Election Quiz")),
        ("⭐", T("Share Experience")),
    ]
    menu_html = "".join(
        f'<div class="cp-menu-item">'
        f'<div class="cp-menu-icon">{icon}</div>'
        f'<span class="cp-menu-text">{label}</span>'
        f'</div>'
        for icon, label in menu_items
    )

    my_const = T("My Constituency")
    st.markdown(
        f"""
        <div class="cp-constituency-card">
            <div class="cp-const-badge">{my_const}</div>
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
    """Horizontal seat-share bars for top parties."""
    total    = results.get("total_seats", 294)
    majority = results.get("majority", 148)
    parties  = results.get("parties", [])

    seats_label    = T("seats")
    majority_label = T("Majority mark")

    rows_html = ""
    rows_html_wrapper_open = '<div role="list" aria-label="Party seat counts">'
    rows_html_wrapper_close = "</div>"
    for p in parties:
        seats = p.get("total", p.get("won", 0) + p.get("leading", 0))
        pct   = min((seats / total) * 100, 100) if total else 0
        color = p.get("color", "#9BA3BC")
        rows_html += f"""
        <div class="cp-party-row" role="listitem">
            <div class="cp-party-name">{sanitize_text(p['name'])}</div>
            <div class="cp-bar-wrap">
                <div class="cp-bar-fill" style="width:{pct:.1f}%;background:{color};"></div>
            </div>
            <div class="cp-bar-seats" style="color:{color};">{seats} {seats_label}</div>
        </div>
        """

    section_title = T("Party Strength")
    st.markdown(
        f"""
        <div class="cp-section-card" role="region" aria-label="Party seat strength">
            <div class="cp-section-title">{section_title} — {sanitize_text(results.get('state', 'State'))}</div>
            {rows_html}
            <div class="cp-majority-line">{majority_label}: {majority} {seats_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── EXIT POLL COMPACT ─────────────────────────────────────────────────────────

def render_exit_poll_compact() -> None:
    """Inline exit-poll aggregator table for the Dashboard tab."""
    polls = st.session_state.get("exit_polls", DEFAULT_EXIT_POLLS)

    avg_aitc   = round(sum(p["aitc"] for p in polls) / len(polls)) if polls else 0
    avg_bjp    = round(sum(p["bjp"]  for p in polls) / len(polls)) if polls else 0
    avg_others = 294 - avg_aitc - avg_bjp

    short_names = {
        "India Today - Axis My India": "India Today",
        "Republic TV - P-MARQ":        "Republic P-MARQ",
        "Times Now - ETG":             "Times Now ETG",
        "ABP News - CVoter":           "ABP - CVoter",
    }

    rows_html = ""
    for p in polls[:4]:
        short  = short_names.get(p["agency"], p["agency"])
        others = max(0, 294 - p["aitc"] - p["bjp"])
        rows_html += (
            f"<tr>"
            f"<td>{sanitize_text(short)}</td>"
            f'<td class="val-aitc">{p["aitc"]}</td>'
            f'<td class="val-bjp">{p["bjp"]}</td>'
            f'<td class="val-other">{others}</td>'
            f"</tr>"
        )

    section_title   = T("Exit Poll Aggregator")
    agencies_label  = T("agencies tracked")
    agency_col      = T("Agency")
    others_col      = T("Others")

    st.markdown(
        f"""
        <div class="cp-section-card">
            <div class="cp-section-title">{section_title}</div>
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
                                color:#5C6480;text-transform:uppercase;">{others_col.upper()}</div>
                </div>
            </div>
            <div style="font-size:0.65rem;color:#5C6480;font-weight:600;
                        letter-spacing:0.08em;margin-bottom:10px;">
                {len(polls)} {agencies_label}
            </div>
            <table class="cp-poll-table">
                <thead>
                    <tr><th>{agency_col}</th><th>AITC</th><th>BJP</th><th>{others_col.upper()}</th></tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── DASHBOARD TAB ─────────────────────────────────────────────────────────────

def render_dashboard() -> None:
    """Compose the full Dashboard tab layout."""
    data    = st.session_state["election_data"]
    sc      = st.session_state["state_code"]
    results = fetch_results(sc)

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
    st.divider()
    st.markdown("#### 📅 Add Election Reminders to Google Calendar")
    from services.calendar_service import CalendarService
    cal = CalendarService()
    links = cal.generate_reminder_links(data)
    cols = st.columns(len(links)) if links else []
    for col, item in zip(cols, links):
        with col:
            st.link_button(f"📅 {item['label']}", item['link'], use_container_width=True)

    # Footer
    data_label    = T("Data: ECI Official · Updated")
    helpline_label = T("Helpline")
    st.markdown(
        f"""
        <div class="cp-footer">
            <span>{data_label}: {results.get('last_updated', '—')}</span>
            <a href="https://results.eci.gov.in/" target="_blank">
                results.eci.gov.in ↗
            </a>
            <span>{helpline_label}: <b style="color:#FF6B1A;">{INDIA['VOTER_HELPLINE']}</b></span>
        </div>
        """,
        unsafe_allow_html=True,
    )
