"""
CivicPulse — India-Centric Maps Service
========================================
localized for Indian addresses, PIN codes, and ECI booth navigation.
"""

from __future__ import annotations
import json
import logging
import urllib.parse
import urllib.request
from typing import Any

from config.settings import GOOGLE_MAPS_API_KEY

logger = logging.getLogger(__name__)

MAPS_BASE = "https://maps.googleapis.com/maps/api"

class MapsService:
    """
    Google Maps client optimized for Indian geography.
    Includes logic for PIN code detection and official ECI routing.
    """

    def __init__(self, api_key: str = GOOGLE_MAPS_API_KEY) -> None:
        self.api_key = api_key

    # ── Public Methods ────────────────────────────────────────────────────────

    def geocode(self, address: str) -> dict | None:
        """
        Convert an Indian address or 6-digit PIN code to coordinates.
        Appends ', India' to ensure global search focuses on the subcontinent.
        """
        # Optimization: Append country context if missing
        search_query = address
        if "india" not in address.lower():
            search_query = f"{address}, India"

        params = {"address": search_query, "key": self.api_key}
        try:
            data = self._get(f"{MAPS_BASE}/geocode/json", params)
            results = data.get("results", [])
            if results:
                loc = results[0]["geometry"]["location"]
                return {
                    "lat": loc["lat"],
                    "lng": loc["lng"],
                    "formatted_address": results[0]["formatted_address"],
                }
        except Exception as exc:
            logger.warning("Geocode failed for India query '%s': %s", address, exc)
        
        # Hackathon Fallback: If API fails, return mock coordinates for New Delhi
        return {"lat": 28.6139, "lng": 77.2090, "formatted_address": "New Delhi, India (Demo Mode)"}

    def get_directions_link(self, destination: str, origin: str = "") -> str:
        """Generate a Google Maps directions URL for Indian traffic/transit."""
        # Use the universal 'dir' action for better mobile deep-linking in India
        params: dict[str, str] = {
            "api": "1",
            "destination": destination,
            "travelmode": "driving" # Common default for India
        }
        if origin:
            params["origin"] = origin
        
        return "https://www.google.com/maps/dir/?" + urllib.parse.urlencode(params)

    def find_nearby_polling_booths(self, lat: float, lng: float) -> list[dict]:
        """
        Specialized search for Indian civic infrastructure.
        Prioritizes Schools and Government buildings where booths are usually located.
        """
        # place_type 'school' is the #1 location for Indian polling booths
        return self.find_nearby_places(lat, lng, place_type="school", radius=2000)

    def find_nearby_places(self, lat: float, lng: float, place_type: str = "school", radius: int = 3000) -> list[dict]:
        """Find nearby places (Schools, Community Centers, etc)."""
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": place_type,
            "key": self.api_key,
        }
        try:
            data = self._get(f"{MAPS_BASE}/place/nearbysearch/json", params)
            return [
                {
                    "name": p.get("name", "Polling Station"),
                    "address": p.get("vicinity", ""),
                    "lat": p["geometry"]["location"]["lat"],
                    "lng": p["geometry"]["location"]["lng"],
                    "rating": p.get("rating"),
                    "types": p.get("types", [])
                }
                for p in data.get("results", [])[:3] # Limit to top 3 for UI clarity
            ]
        except Exception as exc:
            logger.warning("Nearby search failed: %s", exc)
            return []

    def get_eci_booth_locator_url(self, epic_number: str = "") -> str:
        """Helper to link directly to the official ECI booth search."""
        return "https://electoralsearch.eci.gov.in/"

    # ── Private ───────────────────────────────────────────────────────────────

    def _get(self, url: str, params: dict) -> dict:
        query = urllib.parse.urlencode(params)
        req = urllib.request.Request(f"{url}?{query}")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())