"""
CivicPulse — India-Centric Map View Component
=============================================
Localized for Indian polling infrastructure (Schools/Community Halls)
and official ECI Portal integration.

Accessibility fixes:
- No <a><button> nesting (invalid HTML / WCAG failure)
- ARIA labels on interactive elements
- Colour contrast safe inline styles
"""

from __future__ import annotations
import streamlit as st

from config.settings import GOOGLE_MAPS_API_KEY, INDIA
from services.maps_service import MapsService
from utils.location_utils import sanitize_text


def render_map_view(election_data: dict, user_location: str) -> None:
    """Render the polling station map view with Indian civic context."""
    st.markdown("### 🗺️ Polling Station Locator")

    maps_svc = MapsService()

    # 1. India-specific guidance header
    if election_data.get("country_name") == "India" or election_data.get("country_code") == "IN":
        st.info(
            "🔍 In India you must vote at the specific booth listed on your "
            "Voter ID (EPIC) record. Use the official ECI portal below to confirm your booth."
        )

        # Official ECI portal card (uses st.link_button — no unsafe HTML needed)
        st.markdown(
            """
            <div role="region" aria-label="Official ECI booth search"
                 style="background:#FFF3E8;padding:20px;border-radius:14px;
                        border:1px solid #FFD4A8;border-left:6px solid #FF6B00;
                        margin-bottom:20px;box-shadow:0 2px 8px rgba(255,107,0,0.10);">
                <h4 style="color:#D95200;margin-top:0;">📍 Official ECI Booth Search</h4>
                <p style="font-size:0.9rem;color:#5C5C7A;">
                    Find your exact Part Number and Room Number using your EPIC number or name.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.link_button(
            "Open Official Voter Search Portal →",
            INDIA["EPIC_SEARCH_URL"],
            use_container_width=True,
        )

    if not user_location:
        st.info("💡 Enter your PIN code or area in the sidebar to see local civic buildings.")
        return

    # 2. Live map embed
    st.markdown("#### 📍 Civic Buildings in Your Area")
    st.caption(
        "Most Indian polling stations are in Government Schools or Community Centres."
    )

    safe_location = sanitize_text(user_location)

    if GOOGLE_MAPS_API_KEY:
        search_query = f"Government Schools near {safe_location}"
        embed_url = maps_svc.get_embed_url(search_query)
        st.markdown(
            f'<iframe title="Map of civic buildings near {safe_location}" '
            f'width="100%" height="400" style="border:0;border-radius:12px;" '
            f'loading="lazy" allowfullscreen referrerpolicy="no-referrer-when-downgrade" '
            f'src="{embed_url}"></iframe>',
            unsafe_allow_html=True,
        )
    else:
        st.warning("🗺️ Live map requires a Google Maps API key.")
        fallback_link = maps_svc.get_directions_link(
            f"Government School near {safe_location}"
        )
        st.link_button("View local polling centres on Google Maps →", fallback_link)

    st.divider()

    # 3. Nearby polling locations (demo data)
    st.markdown("#### 🏢 Potential Polling Locations")
    mock_booths = [
        {
            "name": "Govt Primary School, Block A",
            "address": f"Near Main Market, {user_location}",
            "accessible": True,
        },
        {
            "name": "Community Centre (Panchayat Bhawan)",
            "address": f"Civil Lines, {user_location}",
            "accessible": True,
        },
    ]

    for station in mock_booths:
        safe_name    = sanitize_text(station["name"])
        safe_address = sanitize_text(station["address"])
        directions_url = maps_svc.get_directions_link(station["address"])

        col_info, col_btn = st.columns([4, 1])
        with col_info:
            st.markdown(
                f"""
                <div role="listitem"
                     style="background:#FFFFFF;
                            border:1px solid #E8E4DC;border-radius:12px;
                            padding:1rem 1.2rem;margin-bottom:0.5rem;
                            box-shadow:0 1px 4px rgba(26,26,46,0.07);">
                    <div style="font-weight:700;color:#138808;font-size:0.95rem;">🏛️ {safe_name}</div>
                    <div style="font-size:0.85rem;color:#5C5C7A;margin-top:2px;">{safe_address}</div>
                    {"<div style='margin-top:6px;'><span style='font-size:0.75rem;background:#E8F5E6;color:#0E6B06;padding:3px 10px;border-radius:20px;font-weight:600;border:1px solid #B8E0B4;'>♿ Wheelchair Accessible</span></div>" if station['accessible'] else ""}
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_btn:
            st.link_button(
                "🗺️ Navigate",
                directions_url,
                use_container_width=True,
                help=f"Get directions to {station['name']}",
            )
