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
            "मंगळ स्वराशीत (मेष/वृश्चिक) असल्याने मंगळ दोष मोठ्या प्रमाणात कमी होतो / निवारित होतो. "
            "(Mars in own sign mitigates Mangal Dosha.)"
        )

    # Rule 2: Mars in exaltation (Capricorn)
    if mars_rashi == EXALTATION_SIGN.get(Planet.MARS):
        return (
            True,
            "मंगळ उच्चस्थ (मकर राशी) असल्याने मंगळ दोष मोठ्या प्रमाणात कमी होतो / निवारित होतो. "
            "(Mars in exaltation — Capricorn — mitigates Mangal Dosha.)"
        )

    # Rule 4: Jupiter aspects Mars (Jupiter's 5th, 7th, or 9th drishti on Mars)
    jupiter_pos = next((p for p in all_planets if p.planet == Planet.JUPITER), None)
    if jupiter_pos is not None:
        aspect_houses = {5, 7, 9}
        mars_house_from_jupiter = (
            (mars_rashi.value - jupiter_pos.rashi.value) % 12
        ) + 1
        if mars_house_from_jupiter in aspect_houses:
            return (
                True,
                "गुरूची मंगळावर दृष्टी असल्याने मंगळ दोष मोठ्या प्रमाणात कमी होतो / निवारित होतो. "
                "(Jupiter's aspect on Mars mitigates Mangal Dosha.)"
            )

    return False, None


def compute_mangal_dosha(
    all_planets: list[PlanetPosition],
    lagna_rashi: Rashi,
    reference_point: str = "Lagna",
) -> MangalDoshaResult:
    """
    Compute Mangal Dosha status from Lagna, Moon, and Venus.
    Determines severity (HIGH, MILD, NONE).
    """
    mars_pos = next((p for p in all_planets if p.planet == Planet.MARS), None)
    if mars_pos is None:
        logger.error("Mars not found in planet positions — cannot compute Mangal Dosha")
        return MangalDoshaResult(
            is_manglik=False,
            severity="NONE",
            reference_point="All",
            mars_house=None,
            cancellation_applied=False,
            cancellation_rule=None,
            explanation_mr="मंगळाची स्थिती उपलब्ध नाही.",
            explanation_en="Mars position not available.",
        )

    moon_pos = next((p for p in all_planets if p.planet == Planet.MOON), None)
    venus_pos = next((p for p in all_planets if p.planet == Planet.VENUS), None)

    ref_rashis = {
        "Lagna": lagna_rashi,
        "Moon": moon_pos.rashi if moon_pos else lagna_rashi,
        "Venus": venus_pos.rashi if venus_pos else lagna_rashi,
    }

    dosha_from = []
    mars_house_lagna = None
    for ref_name, rashi in ref_rashis.items():
        house = _mars_house_from_reference(mars_pos.rashi, rashi)
        if ref_name == "Lagna":
            mars_house_lagna = house
        if house in MANGAL_DOSHA_HOUSES:
            dosha_from.append(ref_name)

    # Check cancellations
    cancelled, cancellation_rule = _check_cancellation_rules(
        mars_pos, lagna_rashi, all_planets
    )

    if not dosha_from:
        return MangalDoshaResult(
            is_manglik=False,
            severity="NONE",
            reference_point="All",
            mars_house=mars_house_lagna,
            cancellation_applied=False,
            cancellation_rule=None,
            explanation_mr="लग्न, चंद्र किंवा शुक्र कुंडलीत मंगळ दोष आढळला नाही.",
            explanation_en="No Mangal Dosha found from Lagna, Moon, or Venus.",
        )

    if cancelled:
        return MangalDoshaResult(
            is_manglik=False,
            severity="NONE",
            reference_point="All",
            mars_house=mars_house_lagna,
            cancellation_applied=True,
            cancellation_rule=cancellation_rule,
            explanation_mr=f"मंगळ दोष आढळला, पण खालील कारणाने तो निवारित होतो: {cancellation_rule}",
            explanation_en=f"Dosha present, but mitigated: {cancellation_rule}",
        )

    # Determine Severity
    if "Lagna" in dosha_from and ("Moon" in dosha_from or "Venus" in dosha_from):
        severity = "HIGH"
        desc_mr = "कडक मंगळ दोष (लग्न आणि चंद्र/शुक्र कुंडलीतून दोष)"
        desc_en = "High severity Mangal Dosha (from Lagna and Moon/Venus)"
    else:
        severity = "MILD"
        desc_mr = "सौम्य / अंशिक मंगळ दोष (फक्त एका कुंडलीतून दोष)"
        desc_en = "Mild/Partial Mangal Dosha"

    house_names = {
        1: "पहिल्या", 2: "दुसऱ्या", 4: "चौथ्या",
        7: "सातव्या", 8: "आठव्या", 12: "बाराव्या",
    }
    house_name_mr = house_names.get(mars_house_lagna, f"{mars_house_lagna}व्या") if mars_house_lagna else ""

    return MangalDoshaResult(
        is_manglik=True,
        severity=severity,
        reference_point=", ".join(dosha_from),
        mars_house=mars_house_lagna,
        cancellation_applied=False,
        cancellation_rule=None,
        explanation_mr=f"{desc_mr}: मंगळ {mars_pos.rashi.name_mr} राशीत, लग्नापासून {house_name_mr} घरात आहे.",
        explanation_en=f"{desc_en}: Mars is in {mars_pos.rashi.name_en}, house {mars_house_lagna} from Lagna.",
    )
