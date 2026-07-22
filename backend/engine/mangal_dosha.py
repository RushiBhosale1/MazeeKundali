"""
engine/mangal_dosha.py
Mangal Dosha (Manglik) calculation.

Algorithm matches AstroSage and all major Indian astrology tools:
  Check Mars from Lagna (if birth time known), Moon, and Venus.
  If Mars occupies a dosha house from ANY of these references → is_manglik=True.
  Severity: LOW (MILD) = 1 reference, HIGH = 2+ references.

Global cancellation rules (own sign, exaltation, Jupiter aspect) are applied first.
If any cancellation applies, no reference will show active dosha.
"""
from __future__ import annotations
import logging
from typing import Optional

from engine.models import (
    Planet, Rashi, MangalDoshaResult, PlanetPosition
)
from engine.tables import EXALTATION_SIGN, OWN_SIGNS

logger = logging.getLogger(__name__)

# Houses from any reference that trigger Mangal Dosha
# Standard Parashar/BPHS tradition (matches AstroSage, JHora):
#   1st (self/health), 4th (home), 7th (spouse), 8th (longevity), 12th (bed pleasures)
# Note: 2nd house is NOT included — it appears in some later texts but is NOT standard.
MANGAL_DOSHA_HOUSES = {1, 4, 7, 8, 12}


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

    Algorithm (matches AstroSage, JHora, and all standard Indian tools):
      1. Apply global cancellation rules — if Mars is in own sign, exaltation,
         or aspected by Jupiter, dosha is cancelled regardless.
      2. Check Mars from up to 3 references:
           - Lagna (if birth time known)
           - Moon
           - Venus
      3. Count how many references show Mars in a dosha house {1,2,4,7,8,12}.
      4. Severity:
           0 references = No Mangal Dosha
           1 reference  = Low Mangal Dosha   (is_manglik=True, severity="MILD")
           2+ references = High Mangal Dosha  (is_manglik=True, severity="HIGH")

    This is why AstroSage says "Low Mangal Dosha" when only Moon or Venus triggers,
    even if Lagna does not.
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

    # ── Global cancellation check ─────────────────────────────────────────────
    # Use any available reference for the function signature (it only uses Mars's rashi)
    _ref_for_cancel = (
        lagna_rashi if lagna_rashi is not None
        else (moon_pos.rashi if moon_pos else Rashi.ARIES)
    )
    cancelled, cancellation_rule = _check_cancellation_rules(
        mars_pos, _ref_for_cancel, all_planets
    )

    # ── Build reference list ──────────────────────────────────────────────────
    # (label_en, rashi, label_mr)
    refs: list[tuple[str, Rashi, str]] = []
    if lagna_rashi is not None:
        refs.append(("Lagna", lagna_rashi, "लग्न"))
    if moon_pos is not None:
        refs.append(("Moon",  moon_pos.rashi,  "चंद्र"))
    if venus_pos is not None:
        refs.append(("Venus", venus_pos.rashi, "शुक्र"))

    if not refs:
        return MangalDoshaResult(
            is_manglik=False, severity="NONE", reference_point="None",
            mars_house=None, cancellation_applied=False, cancellation_rule=None,
            explanation_mr="संदर्भ स्थिती उपलब्ध नाही.",
            explanation_en="No reference positions available.",
        )

    # ── Compute house of Mars from each reference ─────────────────────────────
    house_from: dict[str, int] = {}
    dosha_from: dict[str, bool] = {}
    for label, rashi, _ in refs:
        h = _mars_house_from_reference(mars_pos.rashi, rashi)
        house_from[label] = h
        dosha_from[label] = (h in MANGAL_DOSHA_HOUSES)

    triggered_refs = [label for label, _, _ in refs if dosha_from[label]]
    dosha_count = len(triggered_refs)

    # Primary reference for mars_house field in result
    primary_label    = refs[0][0]
    primary_label_mr = refs[0][2]
    primary_house    = house_from[primary_label]

    # ── Per-reference context string (for transparency) ───────────────────────
    ref_parts_mr = []
    for label, rashi, label_mr in refs:
        h = house_from[label]
        flag = "दोष" if dosha_from[label] else "दोष नाही"
        ref_parts_mr.append(f"{label_mr}: {h}वे घर ({flag})")
    context_mr = " | ".join(ref_parts_mr)

    ref_parts_en = []
    for label, _, _ in refs:
        h = house_from[label]
        flag = "dosha" if dosha_from[label] else "no dosha"
        ref_parts_en.append(f"{label}: house {h} ({flag})")
    context_en = " | ".join(ref_parts_en)

    lagna_note_mr = "" if lagna_rashi is not None else " (जन्मवेळ अज्ञात — लग्न तपासले नाही)"
    lagna_note_en = "" if lagna_rashi is not None else " (birth time unknown — Lagna not checked)"

    # ── Cancellation applied → Mangal Dosha Cancelled (Parihara) ─────────────
    if cancelled:
        severity_val = "CANCELLED" if dosha_count > 0 else "NONE"
        return MangalDoshaResult(
            is_manglik=False,
            severity=severity_val,
            reference_point=primary_label,
            mars_house=primary_house,
            cancellation_applied=True,
            cancellation_rule=cancellation_rule,
            explanation_mr=(
                f"मंगळ {mars_pos.rashi.name_mr} राशीत ({primary_house}वे घर). "
                f"{context_mr}.{lagna_note_mr} "
                f"मंगळ दोष रद्द (परिहार लागू): {cancellation_rule}"
            ),
            explanation_en=(
                f"Mars in {mars_pos.rashi.name_en} (House {primary_house}). "
                f"{context_en}.{lagna_note_en} "
                f"Dosha cancelled (Parihara): {cancellation_rule}"
            ),
        )

    # ── No dosha from any reference ───────────────────────────────────────────
    if dosha_count == 0:
        return MangalDoshaResult(
            is_manglik=False,
            severity="NONE",
            reference_point=primary_label,
            mars_house=primary_house,
            cancellation_applied=False,
            cancellation_rule=None,
            explanation_mr=(
                f"मंगळ {mars_pos.rashi.name_mr} राशीत. "
                f"{context_mr}.{lagna_note_mr} "
                f"कोणत्याही संदर्भातून मंगळ दोष नाही."
            ),
            explanation_en=(
                f"Mars in {mars_pos.rashi.name_en}. "
                f"{context_en}.{lagna_note_en} "
                f"No Mangal Dosha from any reference."
            ),
        )

    # ── Dosha present — grade severity ────────────────────────────────────────
    # Matches AstroSage: 1 reference = "Low", 2+ = "High"
    if dosha_count >= 2:
        severity = "HIGH"
        sev_mr = "कडक मंगळ दोष"
        sev_en = "High Mangal Dosha"
    else:
        severity = "MILD"
        sev_mr = "सौम्य मंगळ दोष"
        sev_en = "Low Mangal Dosha"

    triggered_labels_mr = ", ".join(
        label_mr for label, _, label_mr in refs if dosha_from[label]
    )
    triggered_labels_en = ", ".join(triggered_refs)

    return MangalDoshaResult(
        is_manglik=True,
        severity=severity,
        reference_point=" + ".join(triggered_refs),
        mars_house=primary_house,
        cancellation_applied=False,
        cancellation_rule=None,
        explanation_mr=(
            f"{sev_mr}: मंगळ {mars_pos.rashi.name_mr} राशीत. "
            f"दोष आढळला: {triggered_labels_mr}. "
            f"{context_mr}.{lagna_note_mr}"
        ),
        explanation_en=(
            f"{sev_en}: Mars in {mars_pos.rashi.name_en}. "
            f"Dosha from: {triggered_labels_en}. "
            f"{context_en}.{lagna_note_en}"
        ),
    )
