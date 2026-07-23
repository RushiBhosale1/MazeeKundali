"""
engine/chalit.py
Bhava Chalit (चलित कुंडली) calculation engine.

Standard Vedic Astrology (Equal Bhava / Sripati system):
  - Lagna (Ascendant) longitude L° is the midpoint of House 1.
  - House 1 spans (L - 15°) to (L + 15°).
  - Each planet's Bhava (house 1-12) is computed by its angular distance from Lagna.
"""
from __future__ import annotations
import logging
from typing import Optional
from engine.models import PlanetPosition

logger = logging.getLogger(__name__)


def compute_bhava_chalit_houses(
    lagna_longitude: float,
    planet_positions: list[PlanetPosition],
) -> dict[str, int]:
    """
    Compute house placement (1-12) for each planet in Bhava Chalit chart.

    Args:
        lagna_longitude: Absolute degree of Lagna (0.0 to 359.99)
        planet_positions: List of PlanetPosition objects with absolute longitude.

    Returns:
        dict mapping planet_en (e.g. "Mars") -> bhava house number (1-12).
    """
    bhava_houses: dict[str, int] = {}

    for pp in planet_positions:
        # Distance from Lagna - 15 degrees
        diff = (pp.longitude - lagna_longitude + 15.0) % 360.0
        bhava = int(diff // 30.0) + 1
        bhava_houses[pp.planet.value] = bhava

    return bhava_houses
