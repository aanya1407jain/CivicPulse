"""
CivicPulse — Region Handler Factory
"""

from __future__ import annotations
from .base import BaseRegionHandler


def get_region_handler(country_code: str) -> BaseRegionHandler:
    """
    Factory function — returns the correct region handler for a country code.
    Falls back to a generic handler if the country isn't specifically implemented.
    """
    # Import all handlers from the single workflow.py file
    from .workflow import IndiaRegionHandler, USRegionHandler
    from .generic import GenericRegionHandler

    _REGISTRY: dict[str, type[BaseRegionHandler]] = {
        "IN": IndiaRegionHandler,
        "US": USRegionHandler,
        "UK": GenericRegionHandler,  # Points to our India-friendly fallback
        "CA": GenericRegionHandler,
        "AU": GenericRegionHandler,
        "DE": GenericRegionHandler,
        "JP": GenericRegionHandler,
        "BR": GenericRegionHandler,
        "NG": GenericRegionHandler,
        "EU": GenericRegionHandler,
    }

    handler_cls = _REGISTRY.get(country_code, GenericRegionHandler)
    return handler_cls()


__all__ = ["get_region_handler", "BaseRegionHandler"]