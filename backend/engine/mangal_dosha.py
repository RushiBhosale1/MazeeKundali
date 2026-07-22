"""
engine/mangal_dosha.py
Mangal Dosha (Manglik) calculation.

PRIMARY check: Lagna (standard Maharashtra/Parashar tradition).
SECONDARY checks: Moon and Venus — shown transparently in the output for
  full information, but is_manglik is only set True when Lagna triggers.

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
    4. Jupiter aspects Mars (Jupiter's 5th, 7th, or 9th drishti on Mars)
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
    lagna_rashi: Optional[Rashi],
    reference_point: str = "Lagna",
) -> MangalDoshaResult:
    """
    Compute Mangal Dosha status.

    PRIMARY check:
      - If birth time is known → use Lagna (standard Maharashtra/Parashar tradition)
      - If birth time is unknown (lagna_rashi=None) → fall back to Moon rashi as primary
        (AstroSage and all major tools use Moon as fallback when Lagna is unavailable)

    SECONDARY checks: Moon and Venus for severity escalation only.

    is_manglik=True when Mars is in a dosha house from the primary reference.
    Severity:
      HIGH  — dosha from primary AND secondary (Moon or Venus)
      MILD  — dosha from primary reference ONLY
      NONE  — no dosha from primary reference
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

    moon_pos  = next((p for p in all_planets if p.planet == Planet.MOON),  None)
    venus_pos = next((p for p in all_planets if p.planet == Planet.VENUS), None)

    # ── Determine PRIMARY reference ──────────────────────────────────────────
    # If lagna is available (birth time known) → use Lagna
    # If lagna is None (birth time unknown) → fall back to Moon rashi
    lagna_is_available = lagna_rashi is not None
    if lagna_is_available:
        primary_rashi  = lagna_rashi
        primary_label  = "Lagna"
        primary_label_mr = "लग्न"
    else:
        if moon_pos is None:
            return MangalDoshaResult(
                is_manglik=False, severity="NONE", reference_point="Unknown",
                mars_house=None, cancellation_applied=False, cancellation_rule=None,
                explanation_mr="जन्मवेळ अज्ञात व चंद्र स्थिती उपलब्ध नाही — मंगळ दोष तपासणे शक्य नाही.",
                explanation_en="Birth time unknown and Moon position unavailable — cannot compute Mangal Dosha.",
            )
        primary_rashi  = moon_pos.rashi
        primary_label  = "Moon"
        primary_label_mr = "चंद्र (लग्न अज्ञात)"

    # House of Mars from each reference
    mars_house_primary = _mars_house_from_reference(mars_pos.rashi, primary_rashi)
    mars_house_lagna   = _mars_house_from_reference(mars_pos.rashi, lagna_rashi)  if lagna_rashi  else mars_house_primary
    mars_house_moon    = _mars_house_from_reference(mars_pos.rashi, moon_pos.rashi)  if moon_pos  else None
    mars_house_venus   = _mars_house_from_reference(mars_pos.rashi, venus_pos.rashi) if venus_pos else None

    # PRIMARY dosha check
    primary_dosha = mars_house_primary in MANGAL_DOSHA_HOUSES

    # SECONDARY: Moon + Venus checks (for severity escalation only)
    moon_dosha  = (mars_house_moon  in MANGAL_DOSHA_HOUSES) if (mars_house_moon  is not None and primary_label != "Moon") else False
    venus_dosha = (mars_house_venus in MANGAL_DOSHA_HOUSES) if  mars_house_venus is not None else False

    # Check cancellations using primary reference rashi
    cancelled, cancellation_rule = _check_cancellation_rules(
        mars_pos, primary_rashi, all_planets
    )

    house_names = {
        1: "पहिल्या", 2: "दुसऱ्या", 4: "चौथ्या",
        7: "सातव्या", 8: "आठव्या", 12: "बाराव्या",
    }
    house_name_primary = house_names.get(mars_house_primary, f"{mars_house_primary}व्या")

    # Build secondary context string for transparency
    secondary_parts = []
    if mars_house_moon is not None and primary_label != "Moon":
        moon_flag = "✓ दोष" if moon_dosha else "✗ दोष नाही"
        secondary_parts.append(f"चंद्रापासून {mars_house_moon}वे घर ({moon_flag})")
    if mars_house_venus is not None:
        venus_flag = "✓ दोष" if venus_dosha else "✗ दोष नाही"
        secondary_parts.append(f"शुक्रापासून {mars_house_venus}वे घर ({venus_flag})")
    secondary_str_mr = " | ".join(secondary_parts)

    # Label for fallback note
    fallback_note_mr = "" if lagna_is_available else " (जन्मवेळ अज्ञात — चंद्र संदर्भ वापरला)"
    fallback_note_en = "" if lagna_is_available else " (birth time unknown — Moon used as reference)"

    # ── No dosha from primary ────────────────────────────────────────────────
    if not primary_dosha:
        extra_mr = f" | द्वितीयक: {secondary_str_mr}" if secondary_str_mr else ""
        return MangalDoshaResult(
            is_manglik=False,
            severity="NONE",
            reference_point=primary_label,
            mars_house=mars_house_primary,
            cancellation_applied=False,
            cancellation_rule=None,
            explanation_mr=(
                f"मंगळ {mars_pos.rashi.name_mr} राशीत, {primary_label_mr}पासून {mars_house_primary}व्या घरात — "
                f"मंगळ दोषाचे घर नाही. मंगळ दोष नाही.{fallback_note_mr}{extra_mr}"
            ),
            explanation_en=(
                f"Mars in {mars_pos.rashi.name_en}, house {mars_house_primary} from {primary_label} — "
                f"not a Mangal Dosha house. No Mangal Dosha.{fallback_note_en}"
            ),
        )

    # ── Dosha from primary — check cancellation ──────────────────────────────
    if cancelled:
        extra_mr = f" | द्वितीयक: {secondary_str_mr}" if secondary_str_mr else ""
        return MangalDoshaResult(
            is_manglik=False,
            severity="NONE",
            reference_point=primary_label,
            mars_house=mars_house_primary,
            cancellation_applied=True,
            cancellation_rule=cancellation_rule,
            explanation_mr=(
                f"मंगळ {mars_pos.rashi.name_mr} राशीत, {primary_label_mr}पासून {house_name_primary} घरात. "
                f"मंगळ दोष होता, परंतु रद्द झाला: {cancellation_rule}{fallback_note_mr}{extra_mr}"
            ),
            explanation_en=(
                f"Mars in {mars_pos.rashi.name_en}, house {mars_house_primary} from {primary_label}. "
                f"Mangal Dosha present but mitigated: {cancellation_rule}{fallback_note_en}"
            ),
        )

    # ── Active Mangal Dosha — determine severity ──────────────────────────────
    if moon_dosha or venus_dosha:
        severity = "HIGH"
        sev_mr = "कडक मंगळ दोष"
        sev_en = "High severity Mangal Dosha"
    else:
        severity = "MILD"
        sev_mr = "सौम्य मंगळ दोष"
        sev_en = "Mild Mangal Dosha"

    secondary_note = f" | द्वितीयक संदर्भ: {secondary_str_mr}" if secondary_str_mr else ""

    return MangalDoshaResult(
        is_manglik=True,
        severity=severity,
        reference_point=primary_label,
        mars_house=mars_house_primary,
        cancellation_applied=False,
        cancellation_rule=None,
        explanation_mr=(
            f"{sev_mr}: मंगळ {mars_pos.rashi.name_mr} राशीत, "
            f"{primary_label_mr}पासून {house_name_primary} घरात आहे.{fallback_note_mr}{secondary_note}"
        ),
        explanation_en=(
            f"{sev_en}: Mars is in {mars_pos.rashi.name_en}, "
            f"house {mars_house_primary} from {primary_label}.{fallback_note_en}"
        ),
    )
