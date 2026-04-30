"""
CivicPulse — India-Centric Maps Service
========================================
Localized for Indian addresses, PIN codes, and ECI booth navigation.
"""

from __future__ import annotations
import logging
import urllib.parse
from typing import Any

import requests

from config.settings import GOOGLE_MAPS_API_KEY, INDIA

logger = logging.getLogger(__name__)

MAPS_BASE = "https://maps.googleapis.com/maps/api"

# One session per process — reuses TCP connections for efficiency
_session = requests.Session()
_session.headers.update({"Accept": "application/json"})


class MapsService:
    """
    Google Maps client optimized for Indian geography.
    Includes PIN-code detection and official ECI routing.
    """

    def __init__(self, api_key: str = GOOGLE_MAPS_API_KEY) -> None:
        self.api_key = api_key

    # ── Public Methods ────────────────────────────────────────────────────────

    def geocode(self, address: str) -> dict | None:
        """
        Convert an Indian address or 6-digit PIN code to coordinates.
        Appends ', India' to bias results toward the subcontinent.
        Returns fallback New Delhi coordinates if API key absent or call fails.
        """
        safe_address = self._safe_str(address)
        if "india" not in safe_address.lower():
            safe_address = f"{safe_address}, India"

        if not self.api_key:
            return self._fallback_coords()

        params = {"address": safe_address, "key": self.api_key}
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
            logger.warning("Geocode failed for '%s': %s", address, exc)

        return self._fallback_coords()

    def get_embed_url(self, query: str) -> str:
        """
        Return a Google Maps Embed API URL for iframe use.
        Falls back to a directions link if no API key is set.
        """
        safe_query = urllib.parse.quote(self._safe_str(query))
        if self.api_key:
            return (
                f"https://www.google.com/maps/embed/v1/search"
                f"?key={self.api_key}&q={safe_query}"
            )
        # Graceful degradation — plain iframe-friendly URL (no key required)
        return f"https://maps.google.com/maps?q={safe_query}&output=embed"

    def get_directions_link(self, destination: str, origin: str = "") -> str:
        """Generate a Google Maps directions URL optimized for Indian traffic."""
        params: dict[str, str] = {
            "api": "1",
            "destination": self._safe_str(destination),
            "travelmode": "driving",
        }
        if origin:
            params["origin"] = self._safe_str(origin)
        return "https://www.google.com/maps/dir/?" + urllib.parse.urlencode(params)

    def find_nearby_polling_booths(self, lat: float, lng: float) -> list[dict]:
        """
        Search for schools and government buildings near the given coordinates —
        these are the most common Indian polling booth venues.
        """
        return self.find_nearby_places(lat, lng, place_type="school", radius=2000)

    def find_nearby_places(
        self,
        lat: float,
        lng: float,
        place_type: str = "school",
        radius: int = 3000,
    ) -> list[dict]:
        """Find nearby places and return the top 3 results."""
        if not self.api_key:
            return []
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
                    "types": p.get("types", []),
                }
                for p in data.get("results", [])[:3]
            ]
        except Exception as exc:
            logger.warning("Nearby search failed: %s", exc)
            return []

    def get_eci_booth_locator_url(self, epic_number: str = "") -> str:
        """Return the official ECI booth search URL."""
        return INDIA["EPIC_SEARCH_URL"]

    # ── Private ───────────────────────────────────────────────────────────────

    def _get(self, url: str, params: dict) -> dict[str, Any]:
        resp = _session.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _safe_str(value: str) -> str:
        """Strip control characters; do NOT HTML-escape (URLs need raw chars)."""
        return str(value).strip()

    @staticmethod
    def _fallback_coords() -> dict:
        return {
            "lat": INDIA["MOCK_FALLBACK_LAT"],
            "lng": INDIA["MOCK_FALLBACK_LNG"],
            "formatted_address": INDIA["MOCK_FALLBACK_ADDR"],
        }
