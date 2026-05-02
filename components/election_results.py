"""
CivicPulse — Live Election Results Dashboard
"""

from __future__ import annotations
import streamlit as st
from datetime import datetime

from services.election_scraper import fetch_results, get_state_code_from_location, PARTY_COLORS
from components.language_selector import T


def _color(name: str) -> str:
    n = name.upper().replace(" ", "")
    return next(
        (v for k, v in PARTY_COLORS.items() if k in n or n in k),
        PARTY_COLORS["OTHERS"],
    )


def _seat_bar(parties: list[dict], total: int, majority: int) -> None:
    parts = ""
    for p in parties:
        seat_total = p.get("total", p.get("won", 0) + p.get("leading", 0))
        pct = (seat_total / total) * 100
        if pct < 0.5:
            continue
        c = p.get("color") or _color(p["name"])
        parts += (
            f'<div style="width:{pct:.1f}%;background:{c};height:100%;'
            f'display:inline-block;" title="{p["name"]}: {seat_total}"></div>'
        )

    maj_pct = (majority / total) * 100
    majority_label = T("Majority")
    st.markdown(
        f"""
        <div style="position:relative;margin:1rem 0 2.2rem;">
            <div style="background:#242840;border-radius:8px;height:34px;overflow:hidden;">
                {parts}
            </div>
            <div style="position:absolute;top:-10px;left:{maj_pct:.1f}%;
                        border-left:2px dashed #F74F4F;height:54px;z-index:10;"></div>
            <div style="position:absolute;top:-22px;left:{maj_pct:.1f}%;
                        transform:translateX(-50%);background:#F74F4F;color:#fff;
                        font-size:0.62rem;padding:2px 8px;border-radius:20px;
                        font-weight:700;white-space:nowrap;letter-spacing:0.05em;">
                {majority_label} ({majority})
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_election_results(state: str = "West Bengal") -> None:
    state_code = get_state_code_from_location(state)
    results    = fetch_results(state_code)

    state_name   = results.get("state", state)
    total        = results.get("total_seats", 294)
    majority     = results.get("majority", 148)
    parties      = results.get("parties", [])
    source       = results.get("_source", "mock")
    last_updated = results.get("last_updated", datetime.now().strftime("%d %b %Y, %I:%M %p IST"))
    count_status = results.get("counting_status", "RESULTS AWAITED")

    live_label   = T("Live ECI data") if source == "eci_live" else T("ECI-sourced data")
    auto_refresh = T("Auto-refreshes every 3 min · Last updated")
    st.markdown(f"### 📊 {T('Live Results')} — {state_name}")
    st.caption(f"{'🟢 ' + live_label} · {auto_refresh}: {last_updated}")

    is_live   = "COUNTING" in count_status or "LIVE" in count_status
    s_color   = "#F74F4F" if is_live else "#27C96E"
    pulse_css = "animation:pulse-dot 1.4s infinite;" if is_live else ""
    eci_label = T("ECI Live Portal") if source == "eci_live" else T("ECI-Sourced Estimates")
    seats_label = T("seats")

    st.markdown(
        f"""
        <style>
        @keyframes pulse-dot {{
            0%,100% {{ opacity:1; }} 50% {{ opacity:0.25; }}
        }}
        </style>
        <div role="status" aria-live="polite" aria-label="{count_status}" style="background:{s_color}0F;border:1px solid {s_color}33;
                    border-left:4px solid {s_color};border-radius:10px;
                    padding:10px 18px;display:flex;align-items:center;
                    gap:12px;margin-bottom:1.2rem;">
            <span style="color:{s_color};font-size:1.1rem;{pulse_css}" aria-hidden="true">●</span>
            <div>
                <div style="color:{s_color};font-weight:800;font-size:0.9rem;">
                    {count_status}
                </div>
                <div style="color:#9BA3BC;font-size:0.75rem;">
                    {state_name} · {total} {seats_label} · {'🔴 ' + eci_label}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    seat_tally   = T("Seat Tally")
    majority_mark = T("Majority mark")
    st.markdown(f"**{seat_tally}** — {total} {T('total')} · {majority_mark}: **{majority}**")
    _seat_bar(parties, total, majority)

    majority_badge_text = T("MAJORITY")
    won_label     = T("Won")
    leading_label = T("Leading")
    cols = st.columns(min(len(parties), 5))
    for i, party in enumerate(parties[:5]):
        with cols[i]:
            tally   = party.get("total", party.get("won", 0) + party.get("leading", 0))
            won     = party.get("won", 0)
            leading = party.get("leading", 0)
            c       = party.get("color") or _color(party["name"])
            is_maj  = tally >= majority
            maj_badge = (
                f'<div style="background:rgba(39,201,110,0.15);color:#27C96E;'
                f'font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:20px;'
                f'margin-top:6px;border:1px solid rgba(39,201,110,0.3);">🏆 {majority_badge_text}</div>'
                if is_maj else ""
            )
            st.markdown(
                f"""
                <div style="background:#181B26;border-radius:12px;padding:14px 10px;
                            text-align:center;border:1px solid rgba(255,255,255,0.08);
                            border-top:3px solid {c};">
                    <div style="color:{c};font-weight:800;font-size:1rem;">{party['name']}</div>
                    <div style="font-size:2.2rem;font-weight:900;color:#E8EAF0;line-height:1.1;">{tally}</div>
                    <div style="font-size:0.68rem;color:#9BA3BC;margin:4px 0;">
                        {won_label}: <b style="color:#E8EAF0">{won}</b> ·
                        {leading_label}: <b style="color:#E8EAF0">{leading}</b>
                    </div>
                    {maj_badge}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    top_leads = results.get("top_leads", [])
    if top_leads:
        st.markdown(f"#### 🏅 {T('Top Leading Candidates')}")
        votes_label = T("votes")
        lead_label  = T("lead")
        for cand in top_leads:
            pc = _color(cand.get("party", ""))
            st.markdown(
                f"""
                <div role="listitem" aria-label="{cand['candidate']} leading in {cand['constituency']}" style="display:flex;align-items:center;gap:12px;
                            background:#181B26;border:1px solid rgba(255,255,255,0.06);
                            border-left:4px solid {pc};border-radius:0 10px 10px 0;
                            padding:10px 16px;margin-bottom:8px;">
                    <div style="flex:1;">
                        <div style="font-weight:700;color:#E8EAF0;font-size:0.9rem;">
                            {cand['candidate']}
                        </div>
                        <div style="font-size:0.75rem;color:#9BA3BC;">
                            {cand['constituency']} ·
                            <span style="color:{pc};font-weight:700;">{cand['party']}</span>
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:0.85rem;font-weight:700;color:#E8EAF0;">
                            {cand['votes']:,} {votes_label}
                        </div>
                        <div style="font-size:0.75rem;color:#27C96E;font-weight:700;">
                            +{cand['lead']:,} {lead_label}
                        </div>
                    </div>
                    <div style="background:rgba(39,201,110,0.12);color:#27C96E;
                                font-size:0.72rem;font-weight:700;padding:4px 10px;
                                border-radius:20px;border:1px solid rgba(39,201,110,0.25);">
                        {cand['status']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    col_refresh, col_link = st.columns([1, 2])
    with col_refresh:
        if st.button(f"🔄 {T('Refresh Now')}", use_container_width=True):
            fetch_results.clear()
            st.rerun()
    with col_link:
        st.link_button(
            f"📡 {T('View Full Results on ECI Portal')} →",
            "https://results.eci.gov.in/",
            use_container_width=True,
        )

    st.caption(
        f"⏱️ {T('Data auto-refreshes every 3 minutes. Click Refresh Now for the latest update from the ECI portal.')}"
    )
