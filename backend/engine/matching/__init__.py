"""
engine/matching/__init__.py
Ashtakoot Guna Milan matching engine.

Entry point: compute_match(kundali_a, kundali_b) → MatchResult
All functions are pure — no DB access, no ephemeris calls.
Takes already-computed Rashi + Nakshatra + planet data from KundaliResult.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Optional

from engine.models import (
    KundaliResult, Nakshatra, Rashi, Gana, Nadi, Planet,
)
from engine.tables import (
    NAKSHATRA_TO_GANA,
    NAKSHATRA_TO_NADI,
    RASHI_TO_VARNA,
    NAKSHATRA_DASHA_LORD,
    get_yoni_score,
    get_vashya_score,
    get_graha_maitri_score,
    OWN_SIGNS,
    RASHI_LORD,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class KootaResult:
    name_en: str
    name_mr: str
    points_earned: float
    points_max: int
    notes_mr: str
    notes_en: str


@dataclass
class DoshaCancellation:
    dosha_name: str
    is_present: bool
    is_cancelled: bool
    cancellation_rule_mr: Optional[str]
    cancellation_rule_en: Optional[str]
    explanation_mr: str
    explanation_en: str


@dataclass
class MatchResult:
    # 8 koota breakdown
    varna: KootaResult
    vashya: KootaResult
    tara: KootaResult
    yoni: KootaResult
    graha_maitri: KootaResult
    gana: KootaResult
    bhakoot: KootaResult
    nadi: KootaResult

    # Total
    total_score: float
    total_max: int = 36

    # Doshas (with cancellation transparency)
    nadi_dosha: DoshaCancellation = field(default=None)  # type: ignore
    bhakoot_dosha: DoshaCancellation = field(default=None)  # type: ignore
    mangal_compatibility: Optional[str] = None  # plain text summary

    # Verdict
    verdict_mr: str = ""
    verdict_en: str = ""

    @property
    def kootas(self) -> list[KootaResult]:
        return [
            self.varna, self.vashya, self.tara, self.yoni,
            self.graha_maitri, self.gana, self.bhakoot, self.nadi,
        ]


# ---------------------------------------------------------------------------
# Individual Koota calculators
# ---------------------------------------------------------------------------

def _compute_varna(bride_rashi: Rashi, groom_rashi: Rashi) -> KootaResult:
    """
    Varna (1 point): Spiritual/mental compatibility.
    Score: 1 if groom's Varna ≥ bride's Varna, else 0.
    """
    bride_varna = RASHI_TO_VARNA[bride_rashi]
    groom_varna = RASHI_TO_VARNA[groom_rashi]
    score = 1 if groom_varna.rank >= bride_varna.rank else 0

    if score == 1:
        notes_mr = f"मुलाचा वर्ण ({groom_varna.name_mr}) ≥ मुलीचा वर्ण ({bride_varna.name_mr}). अनुकूल."
        notes_en = f"Groom's Varna ({groom_varna.value}) ≥ Bride's Varna ({bride_varna.value}). Compatible."
    else:
        notes_mr = f"मुलाचा वर्ण ({groom_varna.name_mr}) < मुलीचा वर्ण ({bride_varna.name_mr}). प्रतिकूल."
        notes_en = f"Groom's Varna ({groom_varna.value}) < Bride's Varna ({bride_varna.value}). Incompatible."

    return KootaResult("Varna", "वर्ण", score, 1, notes_mr, notes_en)


def _compute_vashya(bride_rashi: Rashi, groom_rashi: Rashi) -> KootaResult:
    """Vashya (2 points): Mutual attraction/dominance."""
    score = get_vashya_score(bride_rashi, groom_rashi)
    if score == 2:
        notes_mr = "दोन्ही एकाच वश्य गटात. पूर्ण अनुकूल."
        notes_en = "Both in the same Vashya group. Fully compatible."
    elif score == 1:
        notes_mr = "एकतर्फी वश्य. अंशतः अनुकूल."
        notes_en = "One-way Vashya affinity. Partially compatible."
    else:
        notes_mr = "वश्य नाही. प्रतिकूल."
        notes_en = "No Vashya affinity. Incompatible."

    return KootaResult("Vashya", "वश्य", score, 2, notes_mr, notes_en)


def _compute_tara(bride_nakshatra: Nakshatra, groom_nakshatra: Nakshatra) -> KootaResult:
    """
    Tara (3 points): Health/wellbeing based on nakshatra counting.
    Count from bride→groom and groom→bride. mod 9, then classify:
    1,3,5,7 = inauspicious; 2,4,6,8,9(=0) = auspicious.
    3 if both auspicious, 1.5 if one auspicious, 0 if neither.
    """
    def tara_value(from_nak: Nakshatra, to_nak: Nakshatra) -> bool:
        """Returns True if the direction is auspicious."""
        count = ((to_nak.value - from_nak.value) % 27) + 1
        tara = count % 9
        # tara=0 maps to 9 (Aadhar/Jeevan)
        if tara == 0:
            tara = 9
        return tara in {2, 4, 6, 8, 9}

    bride_to_groom_ok = tara_value(bride_nakshatra, groom_nakshatra)
    groom_to_bride_ok = tara_value(groom_nakshatra, bride_nakshatra)

    if bride_to_groom_ok and groom_to_bride_ok:
        score = 3.0
        notes_mr = "दोन्ही दिशांनी तारा शुभ. उत्तम."
        notes_en = "Tara auspicious in both directions. Excellent."
    elif bride_to_groom_ok or groom_to_bride_ok:
        score = 1.5
        notes_mr = "एका दिशेने तारा शुभ. ठीक."
        notes_en = "Tara auspicious in one direction. Average."
    else:
        score = 0.0
        notes_mr = "दोन्ही दिशांनी तारा अशुभ. प्रतिकूल."
        notes_en = "Tara inauspicious in both directions. Incompatible."

    return KootaResult("Tara", "तारा", score, 3, notes_mr, notes_en)


def _compute_yoni(bride_nakshatra: Nakshatra, groom_nakshatra: Nakshatra) -> KootaResult:
    """Yoni (4 points): Physical/sexual compatibility via animal symbols."""
    score = get_yoni_score(bride_nakshatra, groom_nakshatra)

    from engine.tables import NAKSHATRA_YONI
    bride_animal, _ = NAKSHATRA_YONI[bride_nakshatra]
    groom_animal, _ = NAKSHATRA_YONI[groom_nakshatra]

    score_labels = {4: "उत्तम", 3: "अनुकूल", 2: "मध्यम", 1: "प्रतिकूल", 0: "शत्रू"}
    score_labels_en = {4: "Excellent", 3: "Friendly", 2: "Neutral", 1: "Unfriendly", 0: "Enemy"}

    notes_mr = (
        f"मुलगी ({bride_nakshatra.name_mr}): {bride_animal} | "
        f"मुलगा ({groom_nakshatra.name_mr}): {groom_animal}. "
        f"योनी जुळणी: {score_labels.get(score, str(score))}."
    )
    notes_en = (
        f"Bride ({bride_nakshatra.name_en}): {bride_animal} | "
        f"Groom ({groom_nakshatra.name_en}): {groom_animal}. "
        f"Yoni compatibility: {score_labels_en.get(score, str(score))}."
    )

    return KootaResult("Yoni", "योनी", float(score), 4, notes_mr, notes_en)


def _compute_graha_maitri(bride_rashi: Rashi, groom_rashi: Rashi) -> KootaResult:
    """Graha Maitri (5 points): Mental/intellectual compatibility via Rashi lords."""
    score = get_graha_maitri_score(bride_rashi, groom_rashi)
    bride_lord = RASHI_LORD[bride_rashi]
    groom_lord = RASHI_LORD[groom_rashi]

    score_labels_mr = {
        5: "परस्पर मित्र — उत्तम",
        4: "एक मित्र, एक तटस्थ — चांगले",
        3: "दोन्ही तटस्थ — ठीक",
        2: "एक मित्र, एक शत्रू — कमी",
        1: "एक तटस्थ, एक शत्रू — कमी",
        0: "परस्पर शत्रू — प्रतिकूल",
    }

    notes_mr = (
        f"मुलीचा राशीपती: {bride_lord.name_mr} | "
        f"मुलाचा राशीपती: {groom_lord.name_mr}. "
        f"{score_labels_mr.get(score, str(score))}."
    )
    notes_en = (
        f"Bride's Rashi lord: {bride_lord.value} | "
        f"Groom's Rashi lord: {groom_lord.value}. "
        f"Graha Maitri score: {score}/5."
    )

    return KootaResult("Graha Maitri", "ग्रह मैत्री", float(score), 5, notes_mr, notes_en)


def _compute_gana(bride_nakshatra: Nakshatra, groom_nakshatra: Nakshatra, graha_maitri_score: float) -> KootaResult:
    """
    Gana (6 points): Temperament compatibility.
    Deva-Deva / Manushya-Manushya / Rakshasa-Rakshasa = 6 (same gana)
    Deva-Manushya / Manushya-Deva = 5
    Manushya-Rakshasa (male Manushya, female Rakshasa) = 1
    Rakshasa-Manushya (male Rakshasa, female Manushya) = 0
    Deva-Rakshasa / Rakshasa-Deva = 0 (most incompatible)

    Cancellation: If Graha Maitri is 5/5, Gana Dosha is cancelled.
    """
    bride_gana = NAKSHATRA_TO_GANA[bride_nakshatra]
    groom_gana = NAKSHATRA_TO_GANA[groom_nakshatra]

    gana_scores = {
        (Gana.DEVA, Gana.DEVA): 6,
        (Gana.MANUSHYA, Gana.MANUSHYA): 6,
        (Gana.RAKSHASA, Gana.RAKSHASA): 6,
        (Gana.DEVA, Gana.MANUSHYA): 5,
        (Gana.MANUSHYA, Gana.DEVA): 5,
        (Gana.MANUSHYA, Gana.RAKSHASA): 1,  # bride Manushya, groom Rakshasa
        (Gana.RAKSHASA, Gana.MANUSHYA): 0,  # bride Rakshasa, groom Manushya
        (Gana.DEVA, Gana.RAKSHASA): 0,
        (Gana.RAKSHASA, Gana.DEVA): 0,
    }

    score = gana_scores.get((bride_gana, groom_gana), 0)

    # Gana Dosha Cancellation (परिहार)
    if score <= 1 and graha_maitri_score == 5:
        notes_mr = f"मुलगी: {bride_gana.name_mr}, मुलगा: {groom_gana.name_mr}. गण दोष रद्द: ग्रहमैत्री उत्तम (५/५) असल्याने गण दोष नष्ट होतो."
        notes_en = f"Bride: {bride_gana.value}, Groom: {groom_gana.value}. Gana Dosha cancelled: Excellent Graha Maitri (5/5) neutralizes Gana Dosha."
        return KootaResult("Gana", "गण", 6.0, 6, notes_mr, notes_en)

    if score == 6:
        notes_mr = f"दोन्ही {bride_gana.name_mr} गण. उत्तम जुळणी."
        notes_en = f"Both {bride_gana.value} Gana. Excellent match."
    elif score >= 5:
        notes_mr = f"मुलगी: {bride_gana.name_mr}, मुलगा: {groom_gana.name_mr}. चांगले."
        notes_en = f"Bride: {bride_gana.value}, Groom: {groom_gana.value}. Good."
    elif score > 0:
        notes_mr = f"मुलगी: {bride_gana.name_mr}, मुलगा: {groom_gana.name_mr}. कमी अनुकूल."
        notes_en = f"Bride: {bride_gana.value}, Groom: {groom_gana.value}. Low compatibility."
    else:
        notes_mr = f"मुलगी: {bride_gana.name_mr}, मुलगा: {groom_gana.name_mr}. ० गुण (शास्त्रात हे अत्यंत प्रतिकूल मानले जाते)."
        notes_en = f"Bride: {bride_gana.value}, Groom: {groom_gana.value}. 0 points (Highly incompatible in classical texts)."

    return KootaResult("Gana", "गण", float(score), 6, notes_mr, notes_en)


def _compute_bhakoot(
    bride_rashi: Rashi, groom_rashi: Rashi, graha_maitri_score: float
) -> tuple[KootaResult, DoshaCancellation]:
    """
    Bhakoot (7 points): Emotional/financial/family harmony.
    Dosha distances: 2/12, 6/8, 5/9 → 0 points (Bhakoot Dosha).
    Otherwise: 7 points.

    Cancellation (परिहार): Cancelled if Rashi lords are same OR friends (Graha Maitri >= 4).
    """
    # Distance from bride to groom (1-indexed)
    dist_bg = ((groom_rashi.value - bride_rashi.value) % 12) + 1
    dist_gb = ((bride_rashi.value - groom_rashi.value) % 12) + 1

    dosha_pairs = {(2, 12), (6, 8), (5, 9), (12, 2), (8, 6), (9, 5)}
    is_dosha = (dist_bg, dist_gb) in dosha_pairs

    cancelled = False
    cancellation_rule_mr = None
    cancellation_rule_en = None

    if is_dosha:
        bride_lord = RASHI_LORD[bride_rashi]
        groom_lord = RASHI_LORD[groom_rashi]
        dosha_type = f"{min(dist_bg, dist_gb)}/{max(dist_bg, dist_gb)}"

        # Cancellation check
        if bride_lord == groom_lord:
            cancelled = True
            cancellation_rule_mr = f"दोन्हींचा राशीपती ({bride_lord.name_mr}) समान आहे."
            cancellation_rule_en = f"Both have same Rashi lord ({bride_lord.value})."
        elif graha_maitri_score >= 4:
            cancelled = True
            cancellation_rule_mr = f"ग्रहमैत्री उत्तम ({int(graha_maitri_score)}/5) आहे."
            cancellation_rule_en = f"Excellent Graha Maitri ({int(graha_maitri_score)}/5)."

        if cancelled:
            score = 7
            notes_mr = (
                f"भकूट दोष ({dosha_type}) निवारित: {cancellation_rule_mr} पूर्ण ७ गुण दिले."
            )
            notes_en = (
                f"Bhakoot Dosha ({dosha_type}) mitigated: {cancellation_rule_en} Full 7 points awarded."
            )
        else:
            score = 0
            notes_mr = (
                f"भकूट दोष ({dosha_type}) — मुलगी {bride_rashi.name_mr}, "
                f"मुलगा {groom_rashi.name_mr}. ० गुण."
            )
            notes_en = (
                f"Bhakoot Dosha ({dosha_type}) — Bride {bride_rashi.name_en}, "
                f"Groom {groom_rashi.name_en}. 0 points."
            )
    else:
        score = 7
        notes_mr = (
            f"भकूट दोष नाही. मुलगी {bride_rashi.name_mr}, "
            f"मुलगा {groom_rashi.name_mr}. ७ गुण."
        )
        notes_en = (
            f"No Bhakoot Dosha. Bride {bride_rashi.name_en}, "
            f"Groom {groom_rashi.name_en}. 7 points."
        )

    koota = KootaResult("Bhakoot", "भकूट", float(score), 7, notes_mr, notes_en)

    dosha = DoshaCancellation(
        dosha_name="Bhakoot Dosha",
        is_present=is_dosha,
        is_cancelled=cancelled,
        cancellation_rule_mr=cancellation_rule_mr,
        cancellation_rule_en=cancellation_rule_en,
        explanation_mr=notes_mr,
        explanation_en=notes_en,
    )

    return koota, dosha


def _compute_nadi(
    bride_nakshatra: Nakshatra,
    groom_nakshatra: Nakshatra,
    bride_rashi: Rashi,
    groom_rashi: Rashi,
    bride_pada: Optional[int] = None,
    groom_pada: Optional[int] = None,
) -> tuple[KootaResult, DoshaCancellation]:
    """
    Nadi (8 points): Health/genetic compatibility (highest weight).
    Same Nadi = Nadi Dosha = 0 points.
    Different Nadi = 8 points.

    Cancellation rules (transparent):
    1. Same Rashi AND same Nakshatra with different Pada → some texts cancel.
    2. If Rashi lords are same planet → some texts cancel.
    3. Same Nakshatra but different Pada (Charan Bhed) → cancelled.
    """
    bride_nadi = NAKSHATRA_TO_NADI[bride_nakshatra]
    groom_nadi = NAKSHATRA_TO_NADI[groom_nakshatra]
    is_dosha = (bride_nadi == groom_nadi)

    if not is_dosha:
        score = 8.0
        notes_mr = (
            f"मुलगी नाडी: {bride_nadi.name_mr} | मुलगा नाडी: {groom_nadi.name_mr}. "
            f"वेगळ्या नाड्या. ८ गुण."
        )
        notes_en = (
            f"Bride Nadi: {bride_nadi.value} | Groom Nadi: {groom_nadi.value}. "
            f"Different Nadis. 8 points."
        )
        koota = KootaResult("Nadi", "नाडी", score, 8, notes_mr, notes_en)
        dosha = DoshaCancellation(
            dosha_name="Nadi Dosha",
            is_present=False,
            is_cancelled=False,
            cancellation_rule_mr=None,
            cancellation_rule_en=None,
            explanation_mr=notes_mr,
            explanation_en=notes_en,
        )
        return koota, dosha

    # Nadi Dosha present — check cancellation rules
    cancelled = False
    cancellation_rule_mr = None
    cancellation_rule_en = None

    # Cancellation Rule 1: Same Nakshatra but different Pada (Charan Bhed)
    if bride_nakshatra == groom_nakshatra:
        if bride_pada is not None and groom_pada is not None and bride_pada != groom_pada:
            cancelled = True
            cancellation_rule_mr = "नाडी दोष रद्द: दोन्हींचे नक्षत्र समान आहे परंतु चरण (पद) वेगळे आहे (चरण भेद)."
            cancellation_rule_en = "Nadi Dosha cancelled: Same nakshatra but different pada (Charan Bhed)."
        # If same Nakshatra and same Pada, it is a severe Ek-Nakshatra Dosha and is NOT cancelled.

    # Cancellation Rule 2: Same Rashi but different Nakshatra
    if not cancelled and bride_rashi == groom_rashi and bride_nakshatra != groom_nakshatra:
        cancelled = True
        cancellation_rule_mr = "नाडी दोष रद्द: दोन्हींची राशी समान आहे परंतु नक्षत्र वेगळे आहे."
        cancellation_rule_en = "Nadi Dosha cancelled: Same Rashi but different Nakshatras."

    # Cancellation Rule 3: Same Rashi lord (e.g. both ruled by Venus: Taurus and Libra)
    if not cancelled:
        bride_lord = RASHI_LORD[bride_rashi]
        groom_lord = RASHI_LORD[groom_rashi]
        if bride_lord == groom_lord and bride_rashi != groom_rashi:
            cancelled = True
            cancellation_rule_mr = (
                f"नाडी दोष रद्द: राशी वेगळ्या असल्या तरी दोन्हींचा राशीपती ({bride_lord.name_mr}) समान आहे."
            )
            cancellation_rule_en = (
                f"Nadi Dosha cancelled: Different Rashis but same Rashi lord ({bride_lord.value})."
            )

    if cancelled:
        score = 8.0
        notes_mr = (
            f"मुलगी नाडी: {bride_nadi.name_mr} | मुलगा नाडी: {groom_nadi.name_mr}. "
            f"नाडी दोष आहे, पण रद्द झाला: {cancellation_rule_mr}"
        )
        notes_en = (
            f"Bride Nadi: {bride_nadi.value} | Groom Nadi: {groom_nadi.value}. "
            f"Nadi Dosha present but cancelled: {cancellation_rule_en}"
        )
    else:
        score = 0.0
        notes_mr = (
            f"मुलगी नाडी: {bride_nadi.name_mr} | मुलगा नाडी: {groom_nadi.name_mr}. "
            f"नाडी दोष आहे. रद्द नाही. ० गुण."
        )
        notes_en = (
            f"Bride Nadi: {bride_nadi.value} | Groom Nadi: {groom_nadi.value}. "
            f"Nadi Dosha present. Not cancelled. 0 points."
        )

    koota = KootaResult("Nadi", "नाडी", score, 8, notes_mr, notes_en)
    dosha = DoshaCancellation(
        dosha_name="Nadi Dosha",
        is_present=True,
        is_cancelled=cancelled,
        cancellation_rule_mr=cancellation_rule_mr,
        cancellation_rule_en=cancellation_rule_en,
        explanation_mr=notes_mr,
        explanation_en=notes_en,
    )
    return koota, dosha


# ---------------------------------------------------------------------------
# Verdict templating
# ---------------------------------------------------------------------------

def _generate_verdict(total: float, active_doshas: list[str]) -> tuple[str, str]:
    """Generate templated Marathi + English verdict based on score and active doshas."""
    dosha_str_mr = " आणि ".join(active_doshas) if active_doshas else ""
    dosha_str_en = " and ".join(active_doshas) if active_doshas else ""

    if total >= 33:
        mr = "उत्तम जुळणी — हे जोडपे एकमेकांसाठी अतिशय अनुकूल आहे."
        en = "Excellent match — this couple is highly compatible with each other."
    elif total >= 25:
        if dosha_str_mr:
            mr = f"चांगली जुळणी — {dosha_str_mr} असल्यास तज्ञांचा सल्ला घ्या."
            en = f"Good match — consider consulting an expert astrologer regarding {dosha_str_en}."
        else:
            mr = "चांगली जुळणी — हे जोडपे एकमेकांसाठी अनुकूल आहे."
            en = "Good match — this couple is compatible."
    elif total >= 18:
        if dosha_str_mr:
            mr = f"साधारण जुळणी — गुण ठीक आहेत पण {dosha_str_mr} तपासा."
            en = f"Average match — scores are acceptable but please examine {dosha_str_en}."
        else:
            mr = "साधारण जुळणी — गुण ठीक आहेत. पुढे विचार करता येतो."
            en = "Average match — scores are acceptable. Can be considered."
    else:
        mr = f"अल्प जुळणी — या जोडप्यासाठी तज्ञ ज्योतिषांचे मार्गदर्शन घ्या."
        en = "Low match score — please seek guidance from an expert astrologer for this couple."

    return mr, en


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def compute_match(bride_kundali: KundaliResult, groom_kundali: KundaliResult) -> MatchResult:
    """
    Compute full Ashtakoot Guna Milan between two kundalis.

    Args:
        bride_kundali: KundaliResult for the bride.
        groom_kundali: KundaliResult for the groom.

    Returns:
        MatchResult with all 8 koota scores, dosha analysis, and verdict.
    """
    bride_rashi = bride_kundali.rashi
    groom_rashi = groom_kundali.rashi
    bride_nak = bride_kundali.nakshatra
    groom_nak = groom_kundali.nakshatra

    if None in (bride_rashi, groom_rashi, bride_nak, groom_nak):
        raise ValueError(
            "Cannot compute match: Rashi or Nakshatra missing in one or both kundalis."
        )

    # Compute all 8 kootas
    varna = _compute_varna(bride_rashi, groom_rashi)
    vashya = _compute_vashya(bride_rashi, groom_rashi)
    tara = _compute_tara(bride_nak, groom_nak)
    yoni = _compute_yoni(bride_nak, groom_nak)
    graha_maitri = _compute_graha_maitri(bride_rashi, groom_rashi)
    gana = _compute_gana(bride_nak, groom_nak, graha_maitri.points_earned)
    bhakoot, bhakoot_dosha = _compute_bhakoot(bride_rashi, groom_rashi, graha_maitri.points_earned)
    
    bride_pada = bride_kundali.pada
    groom_pada = groom_kundali.pada
    nadi, nadi_dosha = _compute_nadi(bride_nak, groom_nak, bride_rashi, groom_rashi, bride_pada, groom_pada)

    total_score = sum([
        varna.points_earned, vashya.points_earned, tara.points_earned,
        yoni.points_earned, graha_maitri.points_earned, gana.points_earned,
        bhakoot.points_earned, nadi.points_earned,
    ])

    # Determine active (uncancelled) doshas for verdict
    active_doshas_mr = []
    if nadi_dosha.is_present and not nadi_dosha.is_cancelled:
        active_doshas_mr.append("नाडी दोष")
    if bhakoot_dosha.is_present and not bhakoot_dosha.is_cancelled:
        active_doshas_mr.append("भकूट दोष")

    # Mangal compatibility note (Deep match)
    bride_mangal = bride_kundali.mangal_dosha
    groom_mangal = groom_kundali.mangal_dosha
    
    bride_sev = bride_mangal.severity if bride_mangal else "NONE"
    groom_sev = groom_mangal.severity if groom_mangal else "NONE"

    if bride_sev == "NONE" and groom_sev == "NONE":
        mangal_note = "दोघांनाही मंगळ दोष नाही (किंवा मंगळ दोष रद्द झाला आहे). ✅"
    elif bride_sev == groom_sev:
        mangal_note = f"दोन्हींचा मंगळ दोष '{bride_sev}' तीव्रतेचा आहे — एकमेकांना रद्द करतात. ✅"
    elif "HIGH" in (bride_sev, groom_sev) and "NONE" in (bride_sev, groom_sev):
        mangal_note = "एकाला कडक मंगळ दोष आहे आणि दुसऱ्याला नाही — अत्यंत काळजीपूर्वक विचार करावा. ❌"
    elif "HIGH" in (bride_sev, groom_sev) and "MILD" in (bride_sev, groom_sev):
        mangal_note = "एकाला कडक तर दुसऱ्याला सौम्य मंगळ दोष आहे — तज्ञांचा सल्ला घ्या. ⚠️"
    elif "MILD" in (bride_sev, groom_sev) and "NONE" in (bride_sev, groom_sev):
        mangal_note = "एकाला सौम्य मंगळ दोष आहे — साधारणपणे चालते, पण तज्ञांचा सल्ला घ्या. ⚠️"
    else:
        mangal_note = "मंगळ दोषाबाबत तज्ञांचा सल्ला घ्या. ⚠️"

    verdict_mr, verdict_en = _generate_verdict(total_score, active_doshas_mr)

    return MatchResult(
        varna=varna,
        vashya=vashya,
        tara=tara,
        yoni=yoni,
        graha_maitri=graha_maitri,
        gana=gana,
        bhakoot=bhakoot,
        nadi=nadi,
        total_score=total_score,
        nadi_dosha=nadi_dosha,
        bhakoot_dosha=bhakoot_dosha,
        mangal_compatibility=mangal_note,
        verdict_mr=verdict_mr,
        verdict_en=verdict_en,
    )
