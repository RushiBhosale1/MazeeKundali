"""
engine/ephemeris.py
Swiss Ephemeris wrapper for computing planetary positions.

Uses pyswisseph (Python binding for Swiss Ephemeris).
Computes tropical longitudes, then converts to sidereal using Lahiri ayanamsa.
House calculation uses Whole Sign system.

Ayanamsa: Lahiri (Chitrapaksha) — SE_SIDM_LAHIRI
  This is India's government-standard ayanamsa and what most Indian
  software/astrologers use. Do NOT silently use a different ayanamsa.

Rahu mode: True Node (default) — matches most Indian software today.
  Mean Node available as an alternative.
"""
from __future__ import annotations
import os
import logging
from datetime import datetime
from typing import Optional
import math

try:
    import swisseph as swe
    SWISSEPH_AVAILABLE = True
except ImportError:
    SWISSEPH_AVAILABLE = False
    swe = None  # type: ignore

from engine.models import Planet, Rashi, Nakshatra, RahuMode

logger = logging.getLogger(__name__)

# Swiss Ephemeris planet codes
_SWE_PLANET_MAP = {
    Planet.SUN: 0,       # SE_SUN
    Planet.MOON: 1,      # SE_MOON
    Planet.MARS: 4,      # SE_MARS
    Planet.MERCURY: 2,   # SE_MERCURY
    Planet.JUPITER: 5,   # SE_JUPITER
    Planet.VENUS: 3,     # SE_VENUS
    Planet.SATURN: 6,    # SE_SATURN
}

# Rahu/Ketu — True Node vs Mean Node
_SWE_TRUE_NODE = 11   # SE_TRUE_NODE
_SWE_MEAN_NODE = 10   # SE_MEAN_NODE

# Ayanamsa constants
_SWE_SIDM_LAHIRI = 1   # SE_SIDM_LAHIRI

# House systems — pyswisseph expects bytes(b'W'), not int
_HOUSE_WHOLE_SIGN = b'W'  # Whole Sign


def _setup_ephemeris(ephe_path: Optional[str] = None) -> None:
    """Set the ephemeris data file path. Call once at startup."""
    if not SWISSEPH_AVAILABLE:
        raise RuntimeError(
            "pyswisseph is not installed. Run: pip install pyswisseph"
        )
    if ephe_path is None:
        ephe_path = os.environ.get("EPHE_PATH", "./static/ephemeris")
    swe.set_ephe_path(ephe_path)
    logger.info("Swiss Ephemeris initialized with path: %s", ephe_path)


def _datetime_to_jd(utc_dt: datetime) -> float:
    """Convert a naive UTC datetime to Julian Day Number (JD UT)."""
    return swe.julday(
        utc_dt.year, utc_dt.month, utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0,
    )


def compute_planetary_positions(
    utc_dt: datetime,
    latitude: float,
    longitude: float,
    rahu_mode: RahuMode = RahuMode.TRUE_NODE,
    ephe_path: Optional[str] = None,
) -> dict:
    """
    Compute sidereal planetary positions and Lagna using Swiss Ephemeris.

    Args:
        utc_dt: Naive UTC datetime of birth.
        latitude: Birth place latitude.
        longitude: Birth place longitude.
        rahu_mode: True Node or Mean Node for Rahu.
        ephe_path: Path to Swiss Ephemeris .se1 files.

    Returns:
        dict with keys:
            'planets': { Planet → {'longitude': float (sidereal 0–360),
                                   'retrograde': bool,
                                   'speed': float} }
            'lagna_longitude': float (sidereal 0–360)
            'ayanamsa': float (ayanamsa value used)
    """
    _setup_ephemeris(ephe_path)

    jd = _datetime_to_jd(utc_dt)

    # Set Lahiri ayanamsa (sidereal mode)
    swe.set_sid_mode(_SWE_SIDM_LAHIRI)

    # Get ayanamsa value for this date
    ayanamsa = swe.get_ayanamsa_ut(jd)

    results = {}

    # --- Compute each planet ---
    calc_flags = swe.FLG_SWIEPH | swe.FLG_SPEED

    for planet, swe_id in _SWE_PLANET_MAP.items():
        xx, ret = swe.calc_ut(jd, swe_id, calc_flags)
        tropical_lon = xx[0]
        speed = xx[3]  # daily speed in longitude
        retrograde = speed < 0

        sidereal_lon = (tropical_lon - ayanamsa) % 360
        results[planet] = {
            "longitude": sidereal_lon,
            "retrograde": retrograde,
            "speed": speed,
        }

    # --- Rahu (North Node) ---
    rahu_swe_id = _SWE_TRUE_NODE if rahu_mode == RahuMode.TRUE_NODE else _SWE_MEAN_NODE
    xx_rahu, _ = swe.calc_ut(jd, rahu_swe_id, calc_flags)
    rahu_tropical = xx_rahu[0]
    rahu_sidereal = (rahu_tropical - ayanamsa) % 360
    results[Planet.RAHU] = {
        "longitude": rahu_sidereal,
        "retrograde": True,  # Rahu always retrograde in Vedic system
        "speed": xx_rahu[3],
    }

    # --- Ketu (South Node) — always 180° from Rahu ---
    ketu_sidereal = (rahu_sidereal + 180) % 360
    results[Planet.KETU] = {
        "longitude": ketu_sidereal,
        "retrograde": True,
        "speed": -xx_rahu[3],
    }

    # --- Ascendant (Lagna) ---
    # Using Whole Sign house system
    houses, ascmc = swe.houses(jd, latitude, longitude, _HOUSE_WHOLE_SIGN)
    tropical_lagna = ascmc[0]  # ascmc[0] = Ascendant
    sidereal_lagna = (tropical_lagna - ayanamsa) % 360

    logger.debug(
        "Ephemeris computed: JD=%.4f, Ayanamsa=%.4f°, Lagna=%.4f° sidereal",
        jd, ayanamsa, sidereal_lagna,
    )

    return {
        "planets": results,
        "lagna_longitude": sidereal_lagna,
        "ayanamsa": ayanamsa,
    }


def compute_outer_planets(
    utc_dt,
    ayanamsa: float,
) -> dict:
    """
    Compute sidereal positions for outer (modern) planets: Pluto, Neptune, Uranus.
    These are used informally by some modern Jyotishi astrologers in Maharashtra.

    Args:
        utc_dt: Naive UTC datetime of birth.
        ayanamsa: Already-computed Lahiri ayanamsa value (avoids re-calling swe.get_ayanamsa_ut).

    Returns:
        dict with planet names ('Pluto', 'Neptune', 'Uranus') mapping to
        {'longitude': float, 'retrograde': bool, 'rashi': int, 'degree_in_rashi': float}.
    """
    if not SWISSEPH_AVAILABLE:
        return {}

    _setup_ephemeris()
    jd = _datetime_to_jd(utc_dt)
    calc_flags = swe.FLG_SWIEPH | swe.FLG_SPEED

    # Swiss Ephemeris codes for outer planets
    OUTER_MAP = {
        "Pluto":   9,   # SE_PLUTO
        "Neptune": 8,   # SE_NEPTUNE
        "Uranus":  7,   # SE_URANUS
    }

    outer_results = {}
    for name, swe_id in OUTER_MAP.items():
        try:
            xx, _ = swe.calc_ut(jd, swe_id, calc_flags)
            tropical_lon = xx[0]
            speed = xx[3]
            sidereal_lon = (tropical_lon - ayanamsa) % 360
            rashi_idx = int(sidereal_lon / 30) % 12
            outer_results[name] = {
                "longitude": sidereal_lon,
                "retrograde": speed < 0,
                "rashi": rashi_idx,       # 0-11
                "degree_in_rashi": sidereal_lon % 30,
            }
        except Exception:
            pass  # silently skip if ephemeris data not found

    return outer_results


# ---------------------------------------------------------------------------
# Derived value functions (from sidereal longitudes)
# ---------------------------------------------------------------------------

def longitude_to_rashi(sidereal_lon: float) -> Rashi:
    """Convert a sidereal longitude to Rashi (0–11)."""
    return Rashi(int(sidereal_lon / 30) % 12)


def longitude_to_navamsa_rashi(sidereal_lon: float) -> Rashi:
    """
    Convert sidereal longitude to Navamsa Rashi (D9) using the correct
    Parashari (Varga) method.

    Each Rashi = 30°, divided into 9 navamsas of 3°20' (10/3°) each.
    The starting navamsa sign depends on the sign's element:
      - Fire signs (Aries=0, Leo=4, Sagittarius=8) → start from Aries (0)
      - Earth signs (Taurus=1, Virgo=5, Capricorn=9) → start from Capricorn (9)
      - Air signs (Gemini=2, Libra=6, Aquarius=10) → start from Libra (6)
      - Water signs (Cancer=3, Scorpio=7, Pisces=11) → start from Cancer (3)

    This matches the output of AstroSage, JHora, and standard Jyotisha software.
    """
    NAVAMSA_SPAN = 10.0 / 3.0  # 3°20'

    # Which sign (rashi 0-11) does this longitude fall in?
    rashi_index = int(sidereal_lon / 30) % 12

    # How far into the sign (0 to 30°)?
    degree_in_sign = sidereal_lon % 30.0

    # Which navamsa number within this sign (0-8)?
    navamsa_num = int(degree_in_sign / NAVAMSA_SPAN)

    # Starting Navamsa sign based on element
    # Fire=0, Earth=1, Air=2, Water=3 based on rashi_index % 4 sequence:
    # 0(Aries/Fire), 1(Taurus/Earth), 2(Gemini/Air), 3(Cancer/Water),
    # 4(Leo/Fire), 5(Virgo/Earth), 6(Libra/Air), 7(Scorpio/Water), ...
    element = rashi_index % 4  # 0=Fire, 1=Earth, 2=Air, 3=Water
    navamsa_start = {0: 0, 1: 9, 2: 6, 3: 3}[element]  # Aries, Capricorn, Libra, Cancer

    navamsa_rashi = (navamsa_start + navamsa_num) % 12
    return Rashi(navamsa_rashi)


def longitude_to_nakshatra(sidereal_lon: float) -> Nakshatra:
    """Convert a sidereal longitude to Nakshatra (0–26)."""
    nakshatra_span = 360 / 27  # 13.3333...°
    return Nakshatra(int(sidereal_lon / nakshatra_span) % 27)


def longitude_to_pada(sidereal_lon: float) -> int:
    """
    Convert sidereal longitude to Pada (1–4).
    Each nakshatra = 13°20' = 4 padas of 3°20' each.
    """
    nakshatra_span = 360 / 27       # 13.3333...°
    pada_span = nakshatra_span / 4  # 3.3333...°
    position_in_nakshatra = sidereal_lon % nakshatra_span
    return int(position_in_nakshatra / pada_span) + 1


def longitude_to_degree_in_rashi(sidereal_lon: float) -> float:
    """Return degrees within the current Rashi (0–29.99°)."""
    return sidereal_lon % 30


def longitude_to_degree_in_nakshatra(sidereal_lon: float) -> float:
    """Return degrees within the current Nakshatra (0–13.33°)."""
    nakshatra_span = 360 / 27
    return sidereal_lon % nakshatra_span


def compute_whole_sign_house(planet_rashi: Rashi, lagna_rashi: Rashi) -> int:
    """
    Whole Sign house: Lagna sign = House 1, next sign = House 2, etc.
    Returns 1–12.
    """
    return ((planet_rashi.value - lagna_rashi.value) % 12) + 1
