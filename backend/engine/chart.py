"""
engine/chart.py
Main Kundali computation pipeline orchestrator.

This is the entry point for computing a full kundali.
It wires together: geocoding → ephemeris → derived values → dasha → mangal dosha.

POST /engine/kundali internally calls compute_kundali().
All functions are pure — no DB access, no side effects.
"""
from __future__ import annotations
import logging
import os
from datetime import date, time
from typing import Optional

from engine.models import (
    KundaliResult, PlanetPosition, Planet, Rashi, Nakshatra,
    TimeAccuracy, RahuMode,
)
from engine.geocoding import resolve_utc_birth_moment
from engine.ephemeris import (
    compute_planetary_positions,
    longitude_to_rashi,
    longitude_to_nakshatra,
    longitude_to_pada,
    longitude_to_degree_in_rashi,
    longitude_to_degree_in_nakshatra,
    compute_whole_sign_house,
)
from engine.tables import (
    NAKSHATRA_TO_GANA,
    NAKSHATRA_TO_NADI,
    RASHI_TO_VARNA,
    EXALTATION_SIGN,
    DEBILITATION_SIGN,
)
from engine.dasha import compute_current_dasha
from engine.mangal_dosha import compute_mangal_dosha

logger = logging.getLogger(__name__)

EPHE_PATH = os.environ.get("EPHE_PATH", "./static/ephemeris")


def compute_kundali(
    name: str,
    gender: str,
    birth_date: date,
    birth_time: Optional[time],
    time_accuracy: TimeAccuracy,
    place_text: str,
    latitude: float,
    longitude: float,
    tz_iana: str,
    ayanamsa: str = "lahiri",
    house_system: str = "whole_sign",
    rahu_mode: RahuMode = RahuMode.TRUE_NODE,
    compute_paid_fields: bool = False,
) -> KundaliResult:
    """
    Full kundali computation pipeline.

    Args:
        name, gender: Person's basic info.
        birth_date, birth_time: Birth date and local time (time may be None).
        time_accuracy: exact/approximate/unknown.
        place_text: As entered by user.
        latitude, longitude: Resolved lat/long.
        tz_iana: IANA timezone string (e.g. "Asia/Kolkata").
        ayanamsa: Ayanamsa system (only "lahiri" for MVP).
        house_system: House system (only "whole_sign" for MVP).
        rahu_mode: True Node or Mean Node.
        compute_paid_fields: If True, compute full planet table, dasha, mangal dosha.

    Returns:
        KundaliResult — free-tier always populated; paid fields only if requested.
    """
    logger.info(
        "Computing kundali for %s, DOB=%s, Time=%s, Place=%s (%s)",
        name, birth_date, birth_time, place_text, tz_iana,
    )

    # Step 1: Resolve UTC birth moment
    utc_datetime = resolve_utc_birth_moment(birth_date, birth_time, tz_iana)

    result = KundaliResult(
        name=name,
        gender=gender,
        dob=birth_date,
        time_of_birth=birth_time.strftime("%H:%M") if birth_time else None,
        time_accuracy=time_accuracy,
        place_text=place_text,
        latitude=latitude,
        longitude=longitude,
        tz_iana=tz_iana,
        utc_datetime=utc_datetime,
        ayanamsa=ayanamsa,
        house_system=house_system,
        rahu_mode=rahu_mode,
        lagna_reliable=(time_accuracy == TimeAccuracy.EXACT),
    )

    # If birth time is completely unknown, we can only compute Moon sign
    # (from date alone — using noon as proxy for approximate cases)
    if utc_datetime is None and time_accuracy == TimeAccuracy.UNKNOWN:
        # Use noon of birth date as a rough approximation for Moon sign only.
        # Flag lagna as unreliable.
        from datetime import datetime
        proxy_utc = datetime(birth_date.year, birth_date.month, birth_date.day, 6, 30)
        # 6:30 UTC ≈ noon IST — rough proxy
        logger.warning(
            "Birth time unknown for %s — using noon proxy. "
            "Lagna and time-sensitive fields will be unreliable.",
            name,
        )
        _fill_free_fields_from_ephemeris(result, proxy_utc, latitude, longitude, rahu_mode)
        result.lagna = None  # Explicitly null lagna if time unknown
        result.lagna_reliable = False
    elif utc_datetime is not None:
        _fill_free_fields_from_ephemeris(result, utc_datetime, latitude, longitude, rahu_mode)

    # Paid fields (only computed when unlocked)
    if compute_paid_fields and utc_datetime is not None:
        _fill_paid_fields(result, utc_datetime, latitude, longitude, rahu_mode)

    return result


def _fill_free_fields_from_ephemeris(
    result: KundaliResult,
    utc_datetime,
    latitude: float,
    longitude: float,
    rahu_mode: RahuMode,
) -> None:
    """Compute and fill the free-tier fields (Rashi, Nakshatra, Lagna, etc.)"""
    try:
        raw = compute_planetary_positions(
            utc_datetime, latitude, longitude, rahu_mode, EPHE_PATH
        )
    except Exception as e:
        logger.error("Ephemeris computation failed: %s", e)
        raise

    planets_raw = raw["planets"]
    lagna_lon = raw["lagna_longitude"]

    # Moon-based fields (free tier)
    moon_lon = planets_raw[Planet.MOON]["longitude"]
    result.rashi = longitude_to_rashi(moon_lon)
    result.nakshatra = longitude_to_nakshatra(moon_lon)
    result.pada = longitude_to_pada(moon_lon)

    # Lagna
    result.lagna = longitude_to_rashi(lagna_lon)

    # Derived from nakshatra
    result.gana = NAKSHATRA_TO_GANA[result.nakshatra]
    result.nadi = NAKSHATRA_TO_NADI[result.nakshatra]
    result.varna = RASHI_TO_VARNA[result.rashi]

    # Store raw ephemeris data for paid field computation (avoid re-calling)
    result._raw_ephemeris = raw  # type: ignore[attr-defined]


def _fill_paid_fields(
    result: KundaliResult,
    utc_datetime,
    latitude: float,
    longitude: float,
    rahu_mode: RahuMode,
) -> None:
    """Compute and fill the paid-tier fields (full planet table, dasha, mangal dosha)."""
    raw = getattr(result, "_raw_ephemeris", None)
    if raw is None:
        raw = compute_planetary_positions(
            utc_datetime, latitude, longitude, rahu_mode, EPHE_PATH
        )

    planets_raw = raw["planets"]
    lagna_rashi = result.lagna
    lagna_lon = raw["lagna_longitude"]

    if lagna_rashi is None:
        logger.warning("Lagna is None — skipping paid fields that depend on Lagna")
        return

    # Build full planet positions list
    planet_positions: list[PlanetPosition] = []
    for planet in Planet:
        if planet not in planets_raw:
            continue
        pdata = planets_raw[planet]
        lon = pdata["longitude"]
        rashi = longitude_to_rashi(lon)
        nakshatra = longitude_to_nakshatra(lon)
        house = compute_whole_sign_house(rashi, lagna_rashi)

        planet_positions.append(PlanetPosition(
            planet=planet,
            longitude=lon,
            rashi=rashi,
            degree_in_rashi=longitude_to_degree_in_rashi(lon),
            house=house,
            nakshatra=nakshatra,
            pada=longitude_to_pada(lon),
            degree_in_nakshatra=longitude_to_degree_in_nakshatra(lon),
            retrograde=pdata["retrograde"],
            is_exalted=(rashi == EXALTATION_SIGN.get(planet)),
            is_debilitated=(rashi == DEBILITATION_SIGN.get(planet)),
        ))

    result.planet_positions = planet_positions

    # Outer planets (Pluto, Neptune, Uranus) — used by some Maharashtrian astrologers
    try:
        from engine.ephemeris import compute_outer_planets
        outer = compute_outer_planets(utc_datetime, raw["ayanamsa"])
        # Store in raw ephemeris so SVG renderer and API layer can access
        raw["outer_planets"] = outer  # type: ignore[index]
    except Exception as op_err:
        logger.warning("Outer planet computation failed: %s", op_err)
        raw["outer_planets"] = {}  # type: ignore[index]

    # Dasha
    if result.nakshatra is not None:
        moon_lon = planets_raw[Planet.MOON]["longitude"]
        result.dasha = compute_current_dasha(
            moon_nakshatra=result.nakshatra,
            moon_longitude_sidereal=moon_lon,
            birth_date=result.dob,
        )

    # Mangal Dosha
    result.mangal_dosha = compute_mangal_dosha(
        all_planets=planet_positions,
        lagna_rashi=lagna_rashi,
        reference_point="Lagna",
    )
