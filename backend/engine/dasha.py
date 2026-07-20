"""
engine/dasha.py
Vimshottari Dasha calculation.

Standard 120-year cycle.
Sequence: Ketu(7) → Venus(20) → Sun(6) → Moon(10) → Mars(7)
          → Rahu(18) → Jupiter(16) → Saturn(19) → Mercury(17)

Starting dasha lord derived from Moon's nakshatra.
Elapsed portion of first dasha = proportion of nakshatra completed at birth.

Returns: current Mahadasha and Antardasha as of today.
"""
from __future__ import annotations
import logging
from datetime import date, timedelta
from typing import Optional

from engine.models import Planet, Nakshatra, DashaResult
from engine.tables import (
    VIMSHOTTARI_SEQUENCE,
    VIMSHOTTARI_TOTAL_YEARS,
    NAKSHATRA_DASHA_LORD,
)

logger = logging.getLogger(__name__)

# Days in a year (using Julian year = 365.25 days for dasha calculations)
DAYS_PER_YEAR = 365.25

# Pre-compute dasha durations in days
DASHA_DURATION_DAYS: dict[Planet, float] = {
    lord: years * DAYS_PER_YEAR
    for lord, years in VIMSHOTTARI_SEQUENCE
}

SEQUENCE_ORDER: list[Planet] = [lord for lord, _ in VIMSHOTTARI_SEQUENCE]


def _get_sequence_index(planet: Planet) -> int:
    return SEQUENCE_ORDER.index(planet)


def compute_dasha_balance(
    moon_nakshatra: Nakshatra,
    moon_longitude_sidereal: float,
) -> tuple[Planet, float]:
    """
    Compute the starting dasha lord and the remaining balance (in days)
    of the first dasha at birth.

    The balance = (1 - fraction_of_nakshatra_elapsed) × total_dasha_duration.
    fraction_elapsed = position within nakshatra / total nakshatra span.

    Returns (dasha_lord, balance_days).
    """
    nakshatra_span = 360.0 / 27  # 13.3333°

    # Position within the nakshatra (0 to nakshatra_span)
    nakshatra_start = moon_nakshatra.value * nakshatra_span
    position_in_nakshatra = moon_longitude_sidereal - nakshatra_start

    # Clamp to [0, nakshatra_span) for floating-point safety
    position_in_nakshatra = max(0.0, min(position_in_nakshatra, nakshatra_span - 1e-10))

    fraction_elapsed = position_in_nakshatra / nakshatra_span
    fraction_remaining = 1.0 - fraction_elapsed

    starting_lord = NAKSHATRA_DASHA_LORD[moon_nakshatra]
    total_duration = DASHA_DURATION_DAYS[starting_lord]
    balance_days = fraction_remaining * total_duration

    logger.debug(
        "Dasha balance: nakshatra=%s, lord=%s, fraction_remaining=%.4f, balance=%.1f days",
        moon_nakshatra.name_en, starting_lord.value, fraction_remaining, balance_days,
    )

    return starting_lord, balance_days


def _get_antardasha_sequence(mahadasha_lord: Planet) -> list[tuple[Planet, float]]:
    """
    Return the antardasha (sub-dasha) sequence within a given Mahadasha.
    Order starts from the Mahadasha lord itself.
    Duration of each antardasha = (mahadasha_years × antardasha_years / 120) years.
    """
    maha_years = dict(VIMSHOTTARI_SEQUENCE)[mahadasha_lord]
    start_idx = _get_sequence_index(mahadasha_lord)
    antara_sequence = []

    for i in range(9):
        idx = (start_idx + i) % 9
        lord, years = VIMSHOTTARI_SEQUENCE[idx]
        antara_days = (maha_years * years / VIMSHOTTARI_TOTAL_YEARS) * DAYS_PER_YEAR
        antara_sequence.append((lord, antara_days))

    return antara_sequence


def compute_current_dasha(
    moon_nakshatra: Nakshatra,
    moon_longitude_sidereal: float,
    birth_date: date,
    as_of: Optional[date] = None,
) -> DashaResult:
    """
    Compute the current Mahadasha and Antardasha for a given birth data,
    as of `as_of` date (defaults to today).

    Args:
        moon_nakshatra: Moon's nakshatra at birth.
        moon_longitude_sidereal: Moon's sidereal longitude (for balance calc).
        birth_date: Date of birth.
        as_of: Reference date for "current" dasha (default: today).

    Returns:
        DashaResult with mahadasha and antardasha details.
    """
    if as_of is None:
        as_of = date.today()

    # Days elapsed since birth
    days_elapsed = (as_of - birth_date).days

    # Starting dasha and balance
    starting_lord, balance_days = compute_dasha_balance(
        moon_nakshatra, moon_longitude_sidereal
    )

    # Walk through the dasha sequence to find the current Mahadasha
    start_idx = _get_sequence_index(starting_lord)
    cursor_days = 0.0
    maha_lord = starting_lord
    maha_start_days = 0.0
    maha_end_days = balance_days  # First dasha ends at balance

    if days_elapsed <= balance_days:
        # Still in the first (partial) dasha
        maha_lord = starting_lord
        maha_start_days = 0.0
        maha_end_days = balance_days
    else:
        # Move past the first partial dasha
        cursor_days = balance_days
        for i in range(1, 100):  # 100 iterations covers 9 dashas × many cycles
            idx = (start_idx + i) % 9
            lord, _ = VIMSHOTTARI_SEQUENCE[idx]
            duration = DASHA_DURATION_DAYS[lord]
            if cursor_days + duration > days_elapsed:
                maha_lord = lord
                maha_start_days = cursor_days
                maha_end_days = cursor_days + duration
                break
            cursor_days += duration

    # Convert day offsets to actual dates
    maha_start_date = birth_date + timedelta(days=maha_start_days)
    maha_end_date = birth_date + timedelta(days=maha_end_days)

    # --- Find current Antardasha within this Mahadasha ---
    antara_sequence = _get_antardasha_sequence(maha_lord)
    antara_cursor = maha_start_days
    antara_lord = maha_lord
    antara_start_date = maha_start_date
    antara_end_date = maha_end_date

    for lord, antara_days in antara_sequence:
        antara_end = antara_cursor + antara_days
        if antara_cursor <= days_elapsed < antara_end:
            antara_lord = lord
            antara_start_date = birth_date + timedelta(days=antara_cursor)
            antara_end_date = birth_date + timedelta(days=antara_end)
            break
        antara_cursor += antara_days
    else:
        # Fallback: last antardasha in the mahadasha
        antara_lord = antara_sequence[-1][0]

    logger.debug(
        "Current Dasha: Maha=%s (%s to %s), Antara=%s (%s to %s)",
        maha_lord.value, maha_start_date, maha_end_date,
        antara_lord.value, antara_start_date, antara_end_date,
    )

    return DashaResult(
        mahadasha_lord=maha_lord,
        mahadasha_start=maha_start_date,
        mahadasha_end=maha_end_date,
        antardasha_lord=antara_lord,
        antardasha_start=antara_start_date,
        antardasha_end=antara_end_date,
    )
