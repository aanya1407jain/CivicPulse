"""
CivicPulse — Candidate Profiles Component
==========================================
Criminal records, assets, education pulled from ECI affidavits.
Source: https://affidavit.eci.gov.in/ (publicly accessible data)
"""

from __future__ import annotations
import streamlit as st
from utils.location_utils import sanitize_text

ECI_AFFIDAVIT_URL = "https://affidavit.eci.gov.in/"

# ── Mock candidate data (replace with real affidavit scraper) ──────────────────
MOCK_CANDIDATES = [
    {
        "name": "Mamata Banerjee",
        "party": "AITC",
        "party_color": "#00843D",
        "constituency": "Bhawanipore",
        "age": 69,
        "education": "B.A., LL.B. (University of Calcutta)",
        "assets_total": "₹1.02 Crore",
        "assets_movable": "₹68,45,000",
        "assets_immovable": "₹34,00,000",
        "liabilities": "₹0",
        "criminal_cases": 0,
        "criminal_details": [],
        "image_placeholder": "👩‍💼",
        "affidavit_url": "https://affidavit.eci.gov.in/",
        "pan": "DISCLOSED",
        "bio": "Chief Minister of West Bengal and founder of All India Trinamool Congress.",
    },
    {
        "name": "Suvendu Adhikari",
        "party": "BJP",
        "party_color": "#FF6600",
        "constituency": "Nandigram",
        "age": 53,
        "education": "B.A. (Tamluk Hamilton College)",
        "assets_total": "₹4.37 Crore",
        "assets_movable": "₹2.10 Crore",
        "assets_immovable": "₹2.27 Crore",
        "liabilities": "₹0",
        "criminal_cases": 2,
        "criminal_details": [
            {"ipc": "Section 147 IPC", "description": "Rioting", "status": "Pending"},
            {"ipc": "Section 341 IPC", "description": "Wrongful restraint", "status": "Pending"},
        ],
        "image_placeholder": "👨‍💼",
        "affidavit_url": "https://affidavit.eci.gov.in/",
        "pan": "DISCLOSED",
        "bio": "Leader of Opposition in West Bengal Legislative Assembly.",
    },
    {
        "name": "Firhad Hakim",
        "party": "AITC",
        "party_color": "#00843D",
        "constituency": "Kasba",
        "age": 62,
        "education": "B.Com (University of Calcutta)",
        "assets_total": "₹3.21 Crore",
        "assets_movable": "₹1.80 Crore",
        "assets_immovable": "₹1.41 Crore",
        "liabilities": "₹12,00,000",
        "criminal_cases": 1,
        "criminal_details": [
            {"ipc": "Section 120B IPC", "description": "Criminal conspiracy", "status": "Under Trial"},
        ],
        "image_placeholder": "👨‍💼",
        "affidavit_url": "https://affidavit.eci.gov.in/",
        "pan": "DISCLOSED",
        "bio": "Mayor of Kolkata and senior AITC leader.",
    },
]


def _criminal_badge(count: int) -> str:
    if count == 0:
        return '<span style="background:#E8F5E6;color:#0E6B06;font-size:0.72rem;font-weight:700;padding:3px 10px;border-radius:20px;border:1px solid #B8E0B4;">✅ No Cases</span>'
    color = "#C62828" if count >= 3 else "#D95200"
    bg = "#FFEBEE" if count >= 3 else "#FFF3E8"
    border = "#FF8A80" if count >= 3 else "#FFD4A8"
    return f'<span style="background:{bg};color:{color};font-size:0.72rem;font-weight:700;padding:3px 10px;border-radius:20px;border:1px solid {border};">⚠️ {count} Case{"s" if count > 1 else ""}</span>'


def render_candidate_profiles(constituency: str = "") -> None:
    """Render the candidate profile explorer."""
    st.markdown("### 👤 Candidate Profiles & Affidavit Data")
    st.info(
        "🔍 All data is sourced from **ECI sworn affidavits** — public information "
        "that every candidate must legally disclose. Data shown below is illustrative "
        "for demonstration purposes."
    )

    # ── Search ─────────────────────────────────────────────────────────────────
    col_search, col_filter = st.columns([2, 1])
    with col_search:
        search = st.text_input(
            "Search candidate or constituency",
            placeholder="e.g. Bhawanipore or Mamata...",
            key="candidate_search",
        )
    with col_filter:
        filter_party = st.selectbox(
            "Filter by Party",
            ["All", "AITC", "BJP", "INC", "CPI(M)"],
            key="candidate_party_filter",
        )

    # ── Filter candidates ──────────────────────────────────────────────────────
    candidates = MOCK_CANDIDATES
    if search:
        s = search.lower()
        candidates = [
            c for c in candidates
            if s in c["name"].lower() or s in c["constituency"].lower()
        ]
    if filter_party != "All":
        candidates = [c for c in candidates if c["party"] == filter_party]

    if not candidates:
        st.warning("No candidates found. Try a different search term.")
        return

    # ── Render each candidate ──────────────────────────────────────────────────
    for cand in candidates:
        with st.expander(
            f"{cand['image_placeholder']}  **{cand['name']}** · {cand['constituency']} · {cand['party']}",
            expanded=False,
        ):
            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown(
                    f"""
                    <div style="background:#F5F3EF;border-radius:12px;padding:16px;
                                border-left:5px solid {cand['party_color']};">
                        <div style="font-size:3rem;text-align:center;">{cand['image_placeholder']}</div>
                        <div style="font-weight:800;font-size:1rem;color:#1A1A2E;text-align:center;margin-top:8px;">
                            {sanitize_text(cand['name'])}
                        </div>
                        <div style="text-align:center;margin-top:4px;">
                            <span style="background:{cand['party_color']}22;color:{cand['party_color']};
                                         font-size:0.78rem;font-weight:700;padding:3px 10px;border-radius:20px;">
                                {cand['party']}
                            </span>
                        </div>
                        <div style="color:#5C5C7A;font-size:0.8rem;text-align:center;margin-top:8px;">
                            Age: {cand['age']} · {sanitize_text(cand['constituency'])}
                        </div>
                        <div style="color:#5C5C7A;font-size:0.78rem;margin-top:8px;line-height:1.4;">
                            {sanitize_text(cand['bio'])}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with c2:
                st.markdown("**📚 Education & Background**")
                st.markdown(
                    f"""
                    <div style="background:#EEF2FF;border-radius:10px;padding:12px 16px;
                                margin-bottom:12px;border-left:4px solid #4F6EF7;">
                        <div style="font-size:0.85rem;color:#1A1A2E;font-weight:600;">
                            🎓 {sanitize_text(cand['education'])}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown("**💰 Assets & Liabilities**")
                st.markdown(
                    f"""
                    <div style="background:#F0FAF0;border-radius:10px;padding:12px 16px;border-left:4px solid #0E6B06;">
                        <div style="font-size:0.82rem;color:#1A1A2E;margin-bottom:4px;">
                            Total: <b>{cand['assets_total']}</b>
                        </div>
                        <div style="font-size:0.78rem;color:#5C5C7A;">Movable: {cand['assets_movable']}</div>
                        <div style="font-size:0.78rem;color:#5C5C7A;">Immovable: {cand['assets_immovable']}</div>
                        <div style="font-size:0.78rem;color:#C62828;margin-top:4px;">Liabilities: {cand['liabilities']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with c3:
                st.markdown("**⚖️ Criminal Record**")
                st.markdown(
                    f"""
                    <div style="background:#FAFAF8;border-radius:10px;padding:12px 16px;
                                border:1px solid #E8E4DC;margin-bottom:12px;">
                        <div style="margin-bottom:8px;">{_criminal_badge(cand['criminal_cases'])}</div>
                        {''.join([
                            f'<div style="font-size:0.78rem;margin-top:6px;padding:6px 10px;background:#FFF3E8;border-radius:8px;border-left:3px solid #D95200;">'
                            f'<b>{sanitize_text(d["ipc"])}</b><br>'
                            f'<span style="color:#5C5C7A;">{sanitize_text(d["description"])} · {sanitize_text(d["status"])}</span>'
                            f'</div>'
                            for d in cand.get('criminal_details', [])
                        ])}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.link_button(
                "📄 View Official Affidavit on ECI →",
                cand["affidavit_url"],
                use_container_width=True,
            )

    st.divider()
    st.link_button(
        "🔍 Search All Candidates on ECI Affidavit Portal →",
        ECI_AFFIDAVIT_URL,
        use_container_width=True,
    )
