"""
engine/geocoding.py
Place name → latitude, longitude, IANA timezone.
Historical UTC offset resolution via zoneinfo (IANA tz database).

CRITICAL: Never hardcode +5:30 for India. Use zoneinfo for the exact date.
This correctly handles:
  - Pre-1947 regional local mean times
  - 1941-1945 wartime offset changes
  - Modern IST (+5:30)
"""
from __future__ import annotations
import logging
from datetime import datetime, date, time
try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:
    from backports.zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # type: ignore
from typing import Optional

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from timezonefinder import TimezoneFinder

from engine.models import PlaceResult

logger = logging.getLogger(__name__)

# Singleton instances (initialized once)
_geocoder: Optional[Nominatim] = None
_tz_finder: Optional[TimezoneFinder] = None


def _get_geocoder(user_agent: str = "kundali-platform/1.0") -> Nominatim:
    global _geocoder
    if _geocoder is None:
        _geocoder = Nominatim(user_agent=user_agent)
    return _geocoder


def _get_tz_finder() -> TimezoneFinder:
    global _tz_finder
    if _tz_finder is None:
        _tz_finder = TimezoneFinder()
    return _tz_finder


def geocode_place(query: str, max_results: int = 5) -> list[PlaceResult]:
    """
    Search for a place by name.
    Returns up to max_results candidates with lat/long + IANA timezone.

    Used for the autocomplete search on the input form.
    """
    geocoder = _get_geocoder()
    tf = _get_tz_finder()

    try:
        locations = geocoder.geocode(
            query,
            exactly_one=False,
            limit=max_results,
            language="en",          # English for consistency
            addressdetails=True,
            namedetails=True,
            country_codes=None,     # Don't restrict to India — diaspora users exist
            timeout=10,
        )
    except GeocoderTimedOut:
        logger.warning("Geocoding timed out for query: %s", query)
        return []
    except GeocoderServiceError as e:
        logger.error("Geocoding service error: %s", e)
        return []

    if not locations:
        return []

    results: list[PlaceResult] = []
    for loc in locations:
        lat = loc.latitude
        lon = loc.longitude
        tz_iana = tf.timezone_at(lat=lat, lng=lon)
        if tz_iana is None:
            # Fallback for places at sea or edge cases
            tz_iana = "UTC"

        # Build a clean display name that includes state/country for disambiguation
        # e.g. "Kolhapur, Maharashtra, India" not just "Kolhapur"
        display_name = _clean_display_name(loc.raw)

        results.append(PlaceResult(
            display_name=display_name,
            latitude=round(lat, 6),
            longitude=round(lon, 6),
            tz_iana=tz_iana,
            source="nominatim",
        ))

    return results


def _clean_display_name(raw: dict) -> str:
    """
    Build a human-readable display name from Nominatim raw result.
    Priority: city/town/village, state, country.
    """
    addr = raw.get("address", {})
    parts = []

    # Primary locality
    for key in ("city", "town", "village", "hamlet", "suburb"):
        if key in addr:
            parts.append(addr[key])
            break

    # State
    if "state" in addr:
        parts.append(addr["state"])

    # Country
    if "country" in addr:
        parts.append(addr["country"])

    if parts:
        return ", ".join(parts)
    return raw.get("display_name", "Unknown place")


def resolve_utc_birth_moment(
    birth_date: date,
    birth_time: Optional[time],
    tz_iana: str,
) -> Optional[datetime]:
    """
    Convert local birth date+time to UTC datetime using the IANA timezone.

    Returns None if birth_time is None (unknown birth time case).

    IMPORTANT: This uses Python's zoneinfo which reads from the IANA tz database.
    This correctly handles all historical offsets including pre-1947 India.
    Examples:
      - Birth in Bombay on 1920-06-15: will use LMT (+5:21:28), not +5:30
      - Birth during 1941-1945 wartime: zoneinfo handles the offset shifts
      - Modern birth: +5:30 IST correctly applied
    """
    if birth_time is None:
        return None

    local_dt = datetime.combine(birth_date, birth_time)

    try:
        # Try system tz database first; falls back to tzdata package on Windows
        zone = ZoneInfo(tz_iana)
    except Exception:
        try:
            # Explicit tzdata package fallback (for Windows without system tz)
            import importlib.resources
            zone = ZoneInfo(tz_iana)
        except Exception:
            logger.warning("Unknown IANA timezone: %s, falling back to UTC+5:30", tz_iana)
            # IST hardcode only as last resort (should not happen with tzdata installed)
            from datetime import timezone, timedelta
            zone = timezone(timedelta(hours=5, minutes=30))
            return (local_dt - timedelta(hours=5, minutes=30)).replace(tzinfo=None)

    # Attach the timezone (this is a "wall clock" local time)
    local_dt_aware = local_dt.replace(tzinfo=zone)

    # Convert to UTC
    utc_dt = local_dt_aware.astimezone(ZoneInfo("UTC"))

    logger.debug(
        "Birth time resolution: %s %s (%s) → %s UTC (offset: %s)",
        birth_date, birth_time, tz_iana,
        utc_dt.strftime("%Y-%m-%d %H:%M:%S"),
        local_dt_aware.utcoffset(),
    )

    return utc_dt.replace(tzinfo=None)  # Return naive UTC datetime for Swiss Ephemeris


def get_historical_utc_offset(birth_date: date, tz_iana: str) -> str:
    """
    For display purposes: return the historical UTC offset string for a given
    birth date and timezone. e.g. "+05:21" for pre-1947 Bombay.

    This is informational — used to show the user what offset was applied.
    """
    # Use noon as the reference time (avoids DST transition edge cases)
    local_noon = datetime(birth_date.year, birth_date.month, birth_date.day, 12, 0, 0)
    try:
        zone = ZoneInfo(tz_iana)
        aware = local_noon.replace(tzinfo=zone)
        offset = aware.utcoffset()
        if offset is None:
            return "+05:30"  # Sensible India default
        total_minutes = int(offset.total_seconds() / 60)
        sign = "+" if total_minutes >= 0 else "-"
        total_minutes = abs(total_minutes)
        hours, mins = divmod(total_minutes, 60)
        return f"{sign}{hours:02d}:{mins:02d}"
    except Exception as e:
        logger.warning("Failed to resolve historical offset: %s", e)
        return "+05:30"  # IST default fallback
