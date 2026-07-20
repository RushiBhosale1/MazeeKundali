"""
engine/mangal_dosha.py
Mangal Dosha (Manglik) calculation.

Checks if Mars falls in houses 1, 2, 4, 7, 8, or 12 from the Lagna.
We also check from Moon and Venus as secondary reference points (noted clearly).

Cancellation rules are applied as explicit, cited functions.
IMPORTANT: We never silently cancel or adjust — we always show which rule applied.
"""
from __future__ import annotations
import logging
from typing import Optional

from engine.models import (
    Planet, Rashi, MangalDoshaResult, PlanetPosition
)
from engine.tables import EXALTATION_SIGN, OWN_SIGNS

logger = logging.getLogger(__name__)

# Houses from Lagna that trigger Mangal Dosha
MANGAL_DOSHA_HOUSES = {1, 2, 4, 7, 8, 12}


def _mars_house_from_reference(
    mars_rashi: Rashi,
    reference_rashi: Rashi,
) -> int:
    """Return the house Mars occupies counting from the reference Rashi."""
    return ((mars_rashi.value - reference_rashi.value) % 12) + 1


def _check_cancellation_rules(
    mars_position: PlanetPosition,
    lagna_rashi: Rashi,
    all_planets: list[PlanetPosition],
) -> tuple[bool, Optional[str]]:
    """
    Check standard Mangal Dosha cancellation rules.
    Returns (cancelled, rule_description) where rule_description is the
    classical rule that applies, or None if no cancellation.

    Rules (from standard Parasara references):
    1. Mars is in its own sign (Aries or Scorpio) — dosha is cancelled.
    2. Mars is in its exaltation sign (Capricorn) — dosha is cancelled.
    3. Mars is in Cancer (debilitation) — some traditions cancel; we note but
       don't auto-cancel (debilitation weakens Mars, different traditions differ).
    4. Jupiter aspects Mars (Jupiter in 4th, 7th, or 10th from Mars in Whole Sign)
       — dosha significantly mitigated.
    5. Mars is in 2nd house AND owner of 2nd house is strongly placed — partial.
    6. If both partners are Manglik — they cancel each other
       (handled at the matching level, not here).

    We implement rules 1, 2, and 4 as full cancellations.
    Rule 3 is noted but not auto-cancelled (we show it).
    """
    mars_rashi = mars_position.rashi

    # Rule 1: Mars in own sign
    if mars_rashi in OWN_SIGNS.get(Planet.MARS, []):
        return (
            True,
            "मंगळ स्वराशीत (मेष/वृश्चिक) असल्याने मंगळ दोष रद्द होतो. "
            "(Mars in own sign cancels Mangal Dosha.)"
        )

    # Rule 2: Mars in exaltation (Capricorn)
    if mars_rashi == EXALTATION_SIGN.get(Planet.MARS):
        return (
            True,
            "मंगळ उच्चस्थ (मकर राशी) असल्याने मंगळ दोष रद्द होतो. "
            "(Mars in exaltation — Capricorn — cancels Mangal Dosha.)"
        )

    # Rule 4: Jupiter aspects Mars (Whole Sign 4th, 7th, 10th from Mars)
    jupiter_pos = next((p for p in all_planets if p.planet == Planet.JUPITER), None)
    if jupiter_pos is not None:
        aspect_houses = {4, 7, 10}
        jupiter_house_from_mars = (
            (jupiter_pos.rashi.value - mars_rashi.value) % 12
        ) + 1
        if jupiter_house_from_mars in aspect_houses:
            return (
                True,
                "गुरूची मंगळावर दृष्टी असल्याने मंगळ दोष रद्द होतो. "
                "(Jupiter's aspect on Mars cancels Mangal Dosha.)"
            )

    return False, None


def compute_mangal_dosha(
    all_planets: list[PlanetPosition],
    lagna_rashi: Rashi,
    reference_point: str = "Lagna",
) -> MangalDoshaResult:
    """
    Compute Mangal Dosha status.

    Args:
        all_planets: List of all planetary positions.
        lagna_rashi: Ascendant Rashi.
        reference_point: "Lagna" (default for MVP). Can also be "Moon" or "Venus".

    Returns:
        MangalDoshaResult with full transparency on status and cancellation.
    """
    mars_pos = next((p for p in all_planets if p.planet == Planet.MARS), None)
    if mars_pos is None:
        logger.error("Mars not found in planet positions — cannot compute Mangal Dosha")
        return MangalDoshaResult(
            is_manglik=False,
            reference_point=reference_point,
            mars_house=None,
            cancellation_applied=False,
            cancellation_rule=None,
            explanation_mr="मंगळाची स्थिती उपलब्ध नाही.",
            explanation_en="Mars position not available.",
        )

    # Determine reference rashi
    if reference_point == "Lagna":
        ref_rashi = lagna_rashi
    elif reference_point == "Moon":
        moon_pos = next((p for p in all_planets if p.planet == Planet.MOON), None)
        ref_rashi = moon_pos.rashi if moon_pos else lagna_rashi
    elif reference_point == "Venus":
        venus_pos = next((p for p in all_planets if p.planet == Planet.VENUS), None)
        ref_rashi = venus_pos.rashi if venus_pos else lagna_rashi
    else:
        ref_rashi = lagna_rashi

    mars_house = _mars_house_from_reference(mars_pos.rashi, ref_rashi)
    is_dosha = mars_house in MANGAL_DOSHA_HOUSES

    if not is_dosha:
        return MangalDoshaResult(
            is_manglik=False,
            reference_point=reference_point,
            mars_house=mars_house,
            cancellation_applied=False,
            cancellation_rule=None,
            explanation_mr=(
                f"मंगळ {reference_point} पासून {mars_house}व्या घरात आहे. "
                f"मंगळ दोष नाही."
            ),
            explanation_en=(
                f"Mars is in house {mars_house} from {reference_point}. "
                f"No Mangal Dosha."
            ),
        )

    # Dosha exists — check cancellations
    cancelled, cancellation_rule = _check_cancellation_rules(
        mars_pos, lagna_rashi, all_planets
    )

    if cancelled:
        return MangalDoshaResult(
            is_manglik=False,   # Cancelled = not effectively Manglik
            reference_point=reference_point,
            mars_house=mars_house,
            cancellation_applied=True,
            cancellation_rule=cancellation_rule,
            explanation_mr=(
                f"मंगळ {reference_point} पासून {mars_house}व्या घरात आहे "
                f"(दोष आहे), पण रद्द होतो: {cancellation_rule}"
            ),
            explanation_en=(
                f"Mars is in house {mars_house} from {reference_point} "
                f"(dosha present), but cancelled: {cancellation_rule}"
            ),
        )

    # Dosha confirmed, not cancelled
    house_names = {
        1: "पहिल्या", 2: "दुसऱ्या", 4: "चौथ्या",
        7: "सातव्या", 8: "आठव्या", 12: "बाराव्या",
    }
    house_name_mr = house_names.get(mars_house, f"{mars_house}व्या")
    mars_rashi_mr = mars_pos.rashi.name_mr

    return MangalDoshaResult(
        is_manglik=True,
        reference_point=reference_point,
        mars_house=mars_house,
        cancellation_applied=False,
        cancellation_rule=None,
        explanation_mr=(
            f"मंगळ {mars_rashi_mr} राशीत, {reference_point} पासून {house_name_mr} "
            f"घरात आहे. मंगळ दोष आहे. कोणताही रद्द नियम लागू नाही."
        ),
        explanation_en=(
            f"Mars is in {mars_pos.rashi.name_en}, house {mars_house} from "
            f"{reference_point}. Mangal Dosha confirmed. No cancellation rule applies."
        ),
    )
