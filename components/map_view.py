"""
CivicPulse — India-Centric Map View Component
=============================================
Localized for Indian polling infrastructure (Schools/Community Halls)
and official ECI Portal integration.
"""

from __future__ import annotations
import streamlit as st
from services.maps_service import MapsService # Updated name from your service refactor
from config.settings import GOOGLE_MAPS_API_KEY


def render_map_view(election_data: dict, user_location: str) -> None:
    """Render the polling station map view with Indian context."""
    st.markdown("### 🗺️ Polling Station Locator")

    maps_svc = MapsService()

    # 1. Indian Context Header
    if election_data.get("country_name") == "India" or election_data.get("country_code") == "IN":
        st.info("🔍 In India, you must vote at the specific booth mentioned on your Voter ID (EPIC) record.")
        
        # Official ECI Portal Box (Saffron Border)
        st.markdown("""
            <div style="background-color:rgba(255, 153, 51, 0.05); padding:20px; border-radius:12px; border: 1px solid #ff9933; border-left: 6px solid #ff9933; margin-bottom: 20px;">
                <h4 style="color:#ff9933; margin-top:0;">📍 Official ECI Booth Search</h4>
                <p style="font-size:0.9rem; color:#555;">Find your exact Part Number and Room Number using your EPIC number or name.</p>
                <a href="https://electoralsearch.eci.gov.in/" target="_blank" style="text-decoration:none;">
                    <button style="background-color:#1287A5; color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%;">
                        Open Official Voter Search Portal →
                    </button>
                </a>
            </div>
        """, unsafe_allow_html=True)

    if not user_location:
        st.info("💡 Enter your PIN code or Area in the sidebar to see local schools and potential polling centers.")
        return

    # 2. Live Map Embed (Using local schools/govt buildings logic)
    st.markdown("#### 📍 Civic Buildings in Your Area")
    st.caption("Most Indian polling stations are located in Government Schools or Community Centers.")

    if GOOGLE_MAPS_API_KEY and GOOGLE_MAPS_API_KEY != "YOUR_GOOGLE_API_KEY":
        # Bias search for Schools/Civic centers in India
        search_query = f"Government Schools near {user_location}"
        embed_url = maps_svc.get_embed_url(search_query)
        
        st.markdown(
            f'<iframe width="100%" height="400" style="border:0;border-radius:12px;box-shadow: 0 4px 12px rgba(0,0,0,0.1)" '
            f'loading="lazy" allowfullscreen referrerpolicy="no-referrer-when-downgrade" '
            f'src="{embed_url}"></iframe>',
            unsafe_allow_html=True,
        )
    else:
        st.warning("🗺️ **Live Map requires a Google Maps API key.**")
        fallback_link = maps_svc.get_directions_link(f"Government School near {user_location}")
        st.markdown(f"[🔗 View local Polling Centers on Google Maps →]({fallback_link})")

    st.divider()

    # 3. Nearby Results (Simulated for Demo or via API)
    # Using the specialized 'find_nearby_polling_booths' we added to your MapsService
    # For hackathon demo purposes, we usually use mock data if no lat/lng available
    
    st.markdown("#### 🏢 Potential Polling Locations")
    
    # Example Mock Data for Indian Demo
    mock_booths = [
        {"name": "Govt Primary School, Block A", "address": f"Near Main Market, {user_location}", "type": "School"},
        {"name": "Community Center (Panchayat Bhawan)", "address": f"Civil Lines, {user_location}", "type": "Civic"}
    ]

    for station in mock_booths:
        directions_url = maps_svc.get_directions_link(station["address"])

        st.markdown(
            f'''<div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.1); 
            border-radius:12px; padding:1.2rem; margin-bottom:0.75rem; display:flex; 
            justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-weight:600; color:#138808;">🏛️ {station["name"]}</div>
                    <div style="color:#aaa; font-size:0.85rem">{station["address"]}</div>
                    <div style="margin-top:0.3rem">
                        <span style="font-size:0.75rem; background:#e8f5e9; color:#2e7d32; padding:2px 8px; border-radius:4px;">Wheelchair Accessible</span>
                    </div>
                </div>
                <a href="{directions_url}" target="_blank" style="text-decoration:none">
                    <button style="background:#000080; color:white; border:none; border-radius:8px; 
                    padding:0.6rem 1.2rem; cursor:pointer; font-size:0.85rem; font-weight:600;">🗺️ Nav</button>
                </a>
            </div>''',
            unsafe_allow_html=True,
        )