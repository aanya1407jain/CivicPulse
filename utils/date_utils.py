"""CivicPulse — India-Centric Date Utilities"""
from __future__ import annotations
from datetime import datetime, date

def days_until(date_str: str | None) -> int | None:
    """
    Return number of days from today until the given date string. 
    Supports Indian formats like DD-MM-YYYY and verbose ECI styles.
    """
    if not date_str or any(word in date_str.lower() for word in ["varies", "tbd", "phase"]):
        return None
        
    # Supported formats prioritized for Indian context
    formats = (
        "%Y-%m-%d",      # ISO
        "%d-%m-%Y",      # Common Indian (23-04-2026)
        "%d/%m/%Y",      # Common Indian (23/04/2026)
        "%d %B %Y",      # ECI Style (23 April 2026)
        "%B %d, %Y",     # Verbose (April 23, 2026)
        "%m/%d/%Y"       # US Fallback
    )

    for fmt in formats:
        try:
            target = datetime.strptime(date_str.strip(), fmt).date()
            return (target - date.today()).days
        except ValueError:
            continue
    return None

def format_date_locale(date_str: str | None) -> str:
    """
    Format a date string into an Indian human-readable form.
    Example: '2026-04-23' -> 'Thursday, 23 April 2026'
    """
    if not date_str:
        return "Date to be announced (TBA)"
        
    # Handle Phase-based strings immediately
    if "Phase" in date_str:
        return date_str

    try:
        # Normalize the date first
        d_count = days_until(date_str)
        if d_count is None: return date_str
        
        # Try to parse and reformat to Indian Standard
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d %B %Y"):
            try:
                dt = datetime.strptime(date_str, fmt)
                # %-d doesn't work on all Windows systems, using %d for safety
                return dt.strftime("%A, %d %B %Y")
            except ValueError:
                continue
    except Exception:
        pass
        
    return date_str

def is_past(date_str: str | None) -> bool:
    """Return True if the election date has already passed."""
    d = days_until(date_str)
    return d is not None and d < 0

def get_election_status(date_str: str | None) -> str:
    """
    Returns a status tag for Indian Election UI.
    """
    d = days_until(date_str)
    if d is None: return "📅 Upcoming"
    if d == 0: return "🗳️ LIVE: VOTING TODAY"
    if d < 0: return "✅ Completed"
    if d <= 2: return "⚠️ Polls Opening Soon"
    return "⏳ Scheduled"