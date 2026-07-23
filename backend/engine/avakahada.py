"""
engine/avakahada.py
Avakahada Chakra (अवकहडा चक्र) computation and full Vimshottari Mahadasha table.

Avakahada Chakra attributes (as shown by Maharashtrian astrologers):
  1. करण (Karana)
  2. वर्ण (Varna)
  3. वश्य (Vashya)
  4. योनि (Yoni)
  5. गण (Gana)
  6. राशि (Rashi)
  7. नाडी (Nadi)
  8. तत्व (Tatva / Element)
  9. पंचशलाका (Panchashalaaka)
 10. नक्षत्र (Nakshatra) + Pada
"""
from __future__ import annotations
import logging
from datetime import date, timedelta
from typing import Optional
from engine.models import Nakshatra, Rashi, Gana, Nadi, Varna, Planet, KundaliResult
from engine.tables import (
    NAKSHATRA_TO_GANA, NAKSHATRA_TO_NADI, RASHI_TO_VARNA,
    NAKSHATRA_DASHA_LORD, VIMSHOTTARI_SEQUENCE, VIMSHOTTARI_TOTAL_YEARS,
    NAKSHATRA_YONI,
)

logger = logging.getLogger(__name__)

DAYS_PER_YEAR = 365.25

# ---------------------------------------------------------------------------
# Karana — 11 Karanas, each = half a tithi
# ---------------------------------------------------------------------------
# 4 fixed + 7 repeating. In traditional Vedic use: determined by Moon-Sun angle
KARANA_NAMES_MR = [
    "बव", "बालव", "कौलव", "तैतिल", "गर", "वणिज", "विष्टि",  # 7 repeating (0-6)
    "शकुनि", "चतुष्पाद", "नाग", "किंस्तुघ्न",                  # 4 fixed
]
KARANA_NAMES_EN = [
    "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
    "Shakuni", "Chatushpada", "Naga", "Kimstughna",
]

# ---------------------------------------------------------------------------
# Vashya — 5 vashya groups based on Rashi
# ---------------------------------------------------------------------------
RASHI_TO_VASHYA_MR: dict[Rashi, str] = {
    Rashi.ARIES:       "चतुष्पाद",   # Quadruped
    Rashi.TAURUS:      "चतुष्पाद",
    Rashi.GEMINI:      "नर",          # Human
    Rashi.CANCER:      "जलचर",        # Aquatic
    Rashi.LEO:         "वनचर",        # Wild/Forest
    Rashi.VIRGO:       "नर",
    Rashi.LIBRA:       "नर",
    Rashi.SCORPIO:     "जलचर",
    Rashi.SAGITTARIUS: "नर",          # Front half human
    Rashi.CAPRICORN:   "जलचर",
    Rashi.AQUARIUS:    "नर",
    Rashi.PISCES:      "जलचर",
}
RASHI_TO_VASHYA_EN: dict[Rashi, str] = {
    Rashi.ARIES: "Quadruped", Rashi.TAURUS: "Quadruped",
    Rashi.GEMINI: "Human", Rashi.CANCER: "Aquatic",
    Rashi.LEO: "Wild", Rashi.VIRGO: "Human",
    Rashi.LIBRA: "Human", Rashi.SCORPIO: "Aquatic",
    Rashi.SAGITTARIUS: "Human", Rashi.CAPRICORN: "Aquatic",
    Rashi.AQUARIUS: "Human", Rashi.PISCES: "Aquatic",
}

# ---------------------------------------------------------------------------
# Tatva (Element) — Fire, Earth, Air, Water based on Rashi element
# ---------------------------------------------------------------------------
RASHI_TO_TATVA_MR: dict[Rashi, str] = {
    Rashi.ARIES:       "अग्नि",   # Fire
    Rashi.LEO:         "अग्नि",
    Rashi.SAGITTARIUS: "अग्नि",
    Rashi.TAURUS:      "पृथ्वी",  # Earth
    Rashi.VIRGO:       "पृथ्वी",
    Rashi.CAPRICORN:   "पृथ्वी",
    Rashi.GEMINI:      "वायु",    # Air
    Rashi.LIBRA:       "वायु",
    Rashi.AQUARIUS:    "वायु",
    Rashi.CANCER:      "जल",      # Water
    Rashi.SCORPIO:     "जल",
    Rashi.PISCES:      "जल",
}
RASHI_TO_TATVA_EN: dict[Rashi, str] = {
    Rashi.ARIES: "Fire", Rashi.LEO: "Fire", Rashi.SAGITTARIUS: "Fire",
    Rashi.TAURUS: "Earth", Rashi.VIRGO: "Earth", Rashi.CAPRICORN: "Earth",
    Rashi.GEMINI: "Air", Rashi.LIBRA: "Air", Rashi.AQUARIUS: "Air",
    Rashi.CANCER: "Water", Rashi.SCORPIO: "Water", Rashi.PISCES: "Water",
}

# ---------------------------------------------------------------------------
# Yoni — animal symbol from nakshatra (Marathi)
# ---------------------------------------------------------------------------
YONI_NAMES_MR: dict[str, str] = {
    "Horse": "अश्व", "Elephant": "गज", "Sheep": "मेष/एडका",
    "Serpent": "सर्प", "Dog": "श्वान", "Cat": "मार्जार",
    "Rat": "मूषक", "Cow": "गो", "Buffalo": "महिष",
    "Tiger": "व्याघ्र", "Deer": "मृग", "Monkey": "वानर",
    "Mongoose": "मुंगूस", "Lion": "सिंह",
}

# ---------------------------------------------------------------------------
# Karana calculation from Moon-Sun angle
# ---------------------------------------------------------------------------
def compute_karana(moon_lon: float, sun_lon: float) -> tuple[str, str]:
    """
    Compute Karana from Moon-Sun angle.
    Karana = half a tithi. Tithi = 12° Moon-Sun separation.
    Karana = 6° Moon-Sun separation.

    Returns: (name_mr, name_en)
    """
    angle = (moon_lon - sun_lon) % 360
    tithi_num = int(angle / 12)   # 0-29 (30 tithis)
    half = int((angle % 12) / 6)  # 0=first half, 1=second half

    # First 2 karanas (tithi 1, first half + second half) are Kimstughna and Chatushpada (fixed)
    # Tithis 1-30, karanas 1-60
    karana_num = tithi_num * 2 + half  # 0-59

    if karana_num == 0:
        return KARANA_NAMES_MR[10], KARANA_NAMES_EN[10]  # Kimstughna (1st)
    elif karana_num == 57:
        return KARANA_NAMES_MR[7], KARANA_NAMES_EN[7]   # Shakuni
    elif karana_num == 58:
        return KARANA_NAMES_MR[8], KARANA_NAMES_EN[8]   # Chatushpada
    elif karana_num == 59:
        return KARANA_NAMES_MR[9], KARANA_NAMES_EN[9]   # Naga
    else:
        # Repeating 7 karanas fill positions 1-56
        idx = (karana_num - 1) % 7
        return KARANA_NAMES_MR[idx], KARANA_NAMES_EN[idx]


# ---------------------------------------------------------------------------
# Avakahada Chakra
# ---------------------------------------------------------------------------
def compute_avakahada(result: KundaliResult, raw_ephemeris: Optional[dict] = None) -> dict:
    """
    Compute the full Avakahada Chakra for a KundaliResult.

    Returns a dict with Marathi and English values for all attributes.
    """
    if result.rashi is None or result.nakshatra is None:
        return {}

    nakshatra = result.nakshatra
    rashi = result.rashi
    lagna = result.lagna

    # Varna (from Moon rashi)
    varna = RASHI_TO_VARNA.get(rashi)
    varna_mr = varna.name_mr if varna else ""
    varna_en = varna.value if varna else ""

    # Vashya (from Moon rashi)
    vashya_mr = RASHI_TO_VASHYA_MR.get(rashi, "")
    vashya_en = RASHI_TO_VASHYA_EN.get(rashi, "")

    # Tatva (from Moon rashi)
    tatva_mr = RASHI_TO_TATVA_MR.get(rashi, "")
    tatva_en = RASHI_TO_TATVA_EN.get(rashi, "")

    # Gana
    gana = NAKSHATRA_TO_GANA.get(nakshatra)
    gana_names_mr = {Gana.DEVA: "देव", Gana.MANUSHYA: "मनुष्य", Gana.RAKSHASA: "राक्षस"}
    gana_names_en = {Gana.DEVA: "Deva", Gana.MANUSHYA: "Manushya", Gana.RAKSHASA: "Rakshasa"}
    gana_mr = gana_names_mr.get(gana, "") if gana else ""
    gana_en = gana_names_en.get(gana, "") if gana else ""

    # Nadi
    nadi = NAKSHATRA_TO_NADI.get(nakshatra)
    nadi_names_mr = {Nadi.AADI: "आदि (वात)", Nadi.MADHYA: "मध्य (पित्त)", Nadi.ANTYA: "अंत्य (कफ)"}
    nadi_names_en = {Nadi.AADI: "Aadi (Vata)", Nadi.MADHYA: "Madhya (Pitta)", Nadi.ANTYA: "Antya (Kapha)"}
    nadi_mr = nadi_names_mr.get(nadi, "") if nadi else ""
    nadi_en = nadi_names_en.get(nadi, "") if nadi else ""

    # Yoni
    yoni_data = NAKSHATRA_YONI.get(nakshatra)
    yoni_animal_en = yoni_data[0] if yoni_data else ""
    yoni_gender_en = yoni_data[1] if yoni_data else ""
    yoni_mr = YONI_NAMES_MR.get(yoni_animal_en, yoni_animal_en)
    yoni_en = f"{yoni_animal_en} ({yoni_gender_en})"

    # Nakshatra name
    NAKSHATRA_MR = {
        Nakshatra.ASHWINI: "अश्विनी", Nakshatra.BHARANI: "भरणी",
        Nakshatra.KRITTIKA: "कृत्तिका", Nakshatra.ROHINI: "रोहिणी",
        Nakshatra.MRIGASHIRA: "मृगशिरा", Nakshatra.ARDRA: "आर्द्रा",
        Nakshatra.PUNARVASU: "पुनर्वसु", Nakshatra.PUSHYA: "पुष्य",
        Nakshatra.ASHLESHA: "आश्लेषा", Nakshatra.MAGHA: "मघा",
        Nakshatra.PURVA_PHALGUNI: "पू.फाल्गुनी", Nakshatra.UTTARA_PHALGUNI: "उ.फाल्गुनी",
        Nakshatra.HASTA: "हस्त", Nakshatra.CHITRA: "चित्रा",
        Nakshatra.SWATI: "स्वाती", Nakshatra.VISHAKHA: "विशाखा",
        Nakshatra.ANURADHA: "अनुराधा", Nakshatra.JYESHTHA: "ज्येष्ठा",
        Nakshatra.MULA: "मूळ", Nakshatra.PURVA_ASHADHA: "पू.षाढा",
        Nakshatra.UTTARA_ASHADHA: "उ.षाढा", Nakshatra.SHRAVANA: "श्रावण",
        Nakshatra.DHANISHTA: "धनिष्ठा", Nakshatra.SHATABHISHA: "शततारका",
        Nakshatra.PURVA_BHADRAPADA: "पू.भाद्र", Nakshatra.UTTARA_BHADRAPADA: "उ.भाद्र",
        Nakshatra.REVATI: "रेवती",
    }
    RASHI_MR = {
        Rashi.ARIES: "मेष", Rashi.TAURUS: "वृषभ", Rashi.GEMINI: "मिथुन",
        Rashi.CANCER: "कर्क", Rashi.LEO: "सिंह", Rashi.VIRGO: "कन्या",
        Rashi.LIBRA: "तुळ", Rashi.SCORPIO: "वृश्चिक", Rashi.SAGITTARIUS: "धनु",
        Rashi.CAPRICORN: "मकर", Rashi.AQUARIUS: "कुंभ", Rashi.PISCES: "मीन",
    }
    nakshatra_mr = NAKSHATRA_MR.get(nakshatra, nakshatra.name_en)
    rashi_mr = RASHI_MR.get(rashi, rashi.name_en)
    lagna_mr = RASHI_MR.get(lagna, lagna.name_en) if lagna else ""

    # Karana — needs Sun & Moon longitudes
    karana_mr, karana_en = "", ""
    if raw_ephemeris:
        try:
            planets_raw = raw_ephemeris.get("planets", {})
            moon_data = planets_raw.get(Planet.MOON)
            sun_data = planets_raw.get(Planet.SUN)
            if moon_data and sun_data:
                karana_mr, karana_en = compute_karana(
                    moon_data["longitude"], sun_data["longitude"]
                )
        except Exception as ke:
            logger.warning("Karana computation failed: %s", ke)

    return {
        "nakshatra_mr": nakshatra_mr,
        "nakshatra_en": nakshatra.name_en,
        "nakshatra_pada": result.pada or 0,
        "rashi_mr": rashi_mr,
        "rashi_en": rashi.name_en,
        "lagna_mr": lagna_mr,
        "lagna_en": lagna.name_en if lagna else "",
        "karana_mr": karana_mr,
        "karana_en": karana_en,
        "varna_mr": varna_mr,
        "varna_en": varna_en,
        "vashya_mr": vashya_mr,
        "vashya_en": vashya_en,
        "tatva_mr": tatva_mr,
        "tatva_en": tatva_en,
        "gana_mr": gana_mr,
        "gana_en": gana_en,
        "nadi_mr": nadi_mr,
        "nadi_en": nadi_en,
        "yoni_mr": yoni_mr,
        "yoni_en": yoni_en,
    }


# ---------------------------------------------------------------------------
# Full Vimshottari Mahadasha Table
# ---------------------------------------------------------------------------
def compute_full_mahadasha_table(
    moon_nakshatra: Nakshatra,
    moon_longitude_sidereal: float,
    birth_date: date,
) -> list[dict]:
    """
    Compute ALL 9 Mahadasha periods (complete life table) from birth.

    Returns list of dicts:
        [
            {
                "lord": Planet,
                "lord_mr": str,  # Marathi planet name
                "lord_en": str,  # English planet name
                "start_date": date,
                "end_date": date,
                "years": int,    # Mahadasha duration in years
            },
            ...
        ]
    """
    from engine.dasha import compute_dasha_balance, DASHA_DURATION_DAYS, SEQUENCE_ORDER

    PLANET_MR = {
        Planet.SUN: "रवि", Planet.MOON: "चंद्र", Planet.MARS: "मंगळ",
        Planet.MERCURY: "बुध", Planet.JUPITER: "गुरु", Planet.VENUS: "शुक्र",
        Planet.SATURN: "शनि", Planet.RAHU: "राहू", Planet.KETU: "केतु",
    }
    PLANET_YEARS = dict(VIMSHOTTARI_SEQUENCE)

    starting_lord, balance_days = compute_dasha_balance(moon_nakshatra, moon_longitude_sidereal)
    start_idx = SEQUENCE_ORDER.index(starting_lord)

    table = []
    cursor = timedelta(days=0)

    for i in range(9):
        idx = (start_idx + i) % 9
        lord = SEQUENCE_ORDER[idx]
        if i == 0:
            duration_days = balance_days
        else:
            duration_days = DASHA_DURATION_DAYS[lord]

        start = birth_date + cursor
        end = birth_date + cursor + timedelta(days=duration_days)
        table.append({
            "lord": lord,
            "lord_mr": PLANET_MR.get(lord, lord.value),
            "lord_en": lord.value,
            "start_date": start,
            "end_date": end,
            "years": PLANET_YEARS.get(lord, 0),
        })
        cursor += timedelta(days=duration_days)

    return table
