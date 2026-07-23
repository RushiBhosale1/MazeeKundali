"""
engine/avakahada.py
Avakahada Chakra (अवकहडा चक्र) computation and full Vimshottari Mahadasha table.

Avakahada Chakra attributes (as shown by Maharashtrian astrologers):
  1. योग (Yoga)
  2. करण (Karana)
  3. वर्ण (Varna)
  4. तत्व (Tatva / Element)
  5. वश्य (Vashya)
  6. वर्ग (Varga)
  7. योनि (Yoni)
  8. गण (Gana)
  9. युंजा (Yunja)
 10. नाडी (Nadi)
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
# 27 Yogas (योग)
# ---------------------------------------------------------------------------
YOGA_NAMES_MR = [
    "विष्कंभ", "प्रीती", "आयुष्मान", "सौभाग्य", "शोभन", "अतिगंड", "सुकर्मा",
    "धृती", "शूल", "गंड", "वृद्धी", "ध्रुव", "व्याघात", "हर्षण", "वज्र",
    "सिद्धी", "व्यतिपात", "वरीयान", "परिघ", "शिव", "सिद्ध", "साध्य",
    "शुभ", "शुक्ल", "ब्रह्म", "इंद्र", "वैधृती"
]
YOGA_NAMES_EN = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma",
    "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva", "Siddha", "Sadhya",
    "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"
]

# ---------------------------------------------------------------------------
# 30 Tithis (तिथी)
# ---------------------------------------------------------------------------
TITHI_NAMES_MR = [
    "शुक्ल प्रतिपदा", "शुक्ल द्वितीया", "शुक्ल तृतीया", "शुक्ल चतुर्थी", "शुक्ल पंचमी",
    "शुक्ल षष्ठी", "शुक्ल सप्तमी", "शुक्ल अष्टमी", "शुक्ल नवमी", "शुक्ल दशमी",
    "शुक्ल एकादशी", "शुक्ल द्वादशी", "शुक्ल त्रयोदशी", "शुक्ल चतुर्दशी", "पूर्णिमा",
    "कृष्ण प्रतिपदा", "कृष्ण द्वितीया", "कृष्ण तृतीया", "कृष्ण चतुर्थी", "कृष्ण पंचमी",
    "कृष्ण षष्ठी", "कृष्ण सप्तमी", "कृष्ण अष्टमी", "कृष्ण नवमी", "कृष्ण दशमी",
    "कृष्ण एकादशी", "कृष्ण द्वादशी", "कृष्ण त्रयोदशी", "कृष्ण चतुर्दशी", "अमावास्या"
]

# ---------------------------------------------------------------------------
# Karana (करण) — 11 Karanas
# ---------------------------------------------------------------------------
KARANA_NAMES_MR = [
    "बव", "बालव", "कौलव", "तैतिल", "गर", "वणिज", "विष्टि",  # 7 repeating (0-6)
    "शकुनि", "चतुष्पाद", "नाग", "किंस्तुघ्न",                  # 4 fixed
]
KARANA_NAMES_EN = [
    "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
    "Shakuni", "Chatushpada", "Naga", "Kimstughna",
]

# ---------------------------------------------------------------------------
# Varga (वर्ग) — 8 Vargas (Garuda, Marjala, Simha, Shvana, Sarpa, Musaka, Gaja, Vrisha)
# ---------------------------------------------------------------------------
NAKSHATRA_VARGA_MR: dict[Nakshatra, str] = {
    Nakshatra.ASHWINI:           "गरुड",
    Nakshatra.BHARANI:           "मार्जार",
    Nakshatra.KRITTIKA:          "सिंह",
    Nakshatra.ROHINI:            "श्वान",
    Nakshatra.MRIGASHIRA:        "सर्प",
    Nakshatra.ARDRA:             "मूषक",
    Nakshatra.PUNARVASU:         "मार्जार",
    Nakshatra.PUSHYA:            "मूषक",
    Nakshatra.ASHLESHA:          "मार्जार",
    Nakshatra.MAGHA:             "मूषक",
    Nakshatra.PURVA_PHALGUNI:    "मूषक",
    Nakshatra.UTTARA_PHALGUNI:   "गो (वृषभ)",
    Nakshatra.HASTA:             "महिष",
    Nakshatra.CHITRA:            "व्याघ्र",
    Nakshatra.SWATI:             "महिष",
    Nakshatra.VISHAKHA:          "व्याघ्र",
    Nakshatra.ANURADHA:          "मृग",
    Nakshatra.JYESHTHA:          "मृग",
    Nakshatra.MULA:              "श्वान",
    Nakshatra.PURVA_ASHADHA:     "वानर",
    Nakshatra.UTTARA_ASHADHA:    "मुंगूस",
    Nakshatra.SHRAVANA:          "वानर",
    Nakshatra.DHANISHTA:         "सिंह",
    Nakshatra.SHATABHISHA:       "अश्व",
    Nakshatra.PURVA_BHADRAPADA:  "सिंह",
    Nakshatra.UTTARA_BHADRAPADA: "गो (वृषभ)",
    Nakshatra.REVATI:            "गज",
}

# ---------------------------------------------------------------------------
# Yunja (युंजा) — 3 Yunjas. Traditional Maharashtrian Jyotish uses:
# पाद्य (Nakshatras 1-9), मध्य (10-18), अंत्य (19-27)
# ---------------------------------------------------------------------------
NAKSHATRA_YUNJA_MR: dict[Nakshatra, str] = {
    # पाद्य — First 9 nakshatras (Ashwini to Ashlesha)
    Nakshatra.ASHWINI: "पाद्य", Nakshatra.BHARANI: "पाद्य", Nakshatra.KRITTIKA: "पाद्य",
    Nakshatra.ROHINI: "पाद्य", Nakshatra.MRIGASHIRA: "पाद्य", Nakshatra.ARDRA: "पाद्य",
    Nakshatra.PUNARVASU: "पाद्य", Nakshatra.PUSHYA: "पाद्य", Nakshatra.ASHLESHA: "पाद्य",
    # मध्य — Middle 9 nakshatras (Magha to Jyeshtha)
    Nakshatra.MAGHA: "मध्य", Nakshatra.PURVA_PHALGUNI: "मध्य", Nakshatra.UTTARA_PHALGUNI: "मध्य",
    Nakshatra.HASTA: "मध्य", Nakshatra.CHITRA: "मध्य", Nakshatra.SWATI: "मध्य",
    Nakshatra.VISHAKHA: "मध्य", Nakshatra.ANURADHA: "मध्य", Nakshatra.JYESHTHA: "मध्य",
    # अंत्य — Last 9 nakshatras (Mula to Revati)
    Nakshatra.MULA: "अंत्य", Nakshatra.PURVA_ASHADHA: "अंत्य", Nakshatra.UTTARA_ASHADHA: "अंत्य",
    Nakshatra.SHRAVANA: "अंत्य", Nakshatra.DHANISHTA: "अंत्य", Nakshatra.SHATABHISHA: "अंत्य",
    Nakshatra.PURVA_BHADRAPADA: "अंत्य", Nakshatra.UTTARA_BHADRAPADA: "अंत्य", Nakshatra.REVATI: "अंत्य"
}

# ---------------------------------------------------------------------------
# Vashya — 5 vashya groups based on Rashi
# Traditional Maharashtrian Jyotish classification:
#   चतुष्पाद — Aries, Taurus, first half Sagittarius, Capricorn
#   नर — Gemini, Virgo, Libra, Aquarius, second half Sagittarius
#   जलचर — Cancer, Capricorn (part), Pisces
#   वनचर — Leo
#   कीट — Scorpio (insect/reptile class)
# ---------------------------------------------------------------------------
RASHI_TO_VASHYA_MR: dict[Rashi, str] = {
    Rashi.ARIES:       "चतुष्पाद",
    Rashi.TAURUS:      "चतुष्पाद",
    Rashi.GEMINI:      "नर",
    Rashi.CANCER:      "जलचर",
    Rashi.LEO:         "वनचर",
    Rashi.VIRGO:       "नर",
    Rashi.LIBRA:       "नर",
    Rashi.SCORPIO:     "कीट",       # Scorpio = insect/reptile (कीट) — NOT जलचर
    Rashi.SAGITTARIUS: "चतुष्पाद",  # Sagittarius front = horse (चतुष्पाद)
    Rashi.CAPRICORN:   "चतुष्पाद",  # Capricorn = sea-goat but classified as चतुष्पाद in Maharashtrian
    Rashi.AQUARIUS:    "नर",
    Rashi.PISCES:      "जलचर",
}
RASHI_TO_VASHYA_EN: dict[Rashi, str] = {
    Rashi.ARIES: "Quadruped", Rashi.TAURUS: "Quadruped",
    Rashi.GEMINI: "Human", Rashi.CANCER: "Aquatic",
    Rashi.LEO: "Wild", Rashi.VIRGO: "Human",
    Rashi.LIBRA: "Human", Rashi.SCORPIO: "Insect/Reptile (Keeta)",
    Rashi.SAGITTARIUS: "Quadruped", Rashi.CAPRICORN: "Quadruped",
    Rashi.AQUARIUS: "Human", Rashi.PISCES: "Aquatic",
}

# ---------------------------------------------------------------------------
# Tatva (Element) — Traditional Maharashtrian Jyotish uses Sanskrit terms:
#   अग्नि (Fire), भूमि (Earth), वायु (Air), वारि (Water — traditional term)
# ---------------------------------------------------------------------------
RASHI_TO_TATVA_MR: dict[Rashi, str] = {
    Rashi.ARIES:       "अग्नि",
    Rashi.LEO:         "अग्नि",
    Rashi.SAGITTARIUS: "अग्नि",
    Rashi.TAURUS:      "भूमि",
    Rashi.VIRGO:       "भूमि",
    Rashi.CAPRICORN:   "भूमि",
    Rashi.GEMINI:      "वायु",
    Rashi.LIBRA:       "वायु",
    Rashi.AQUARIUS:    "वायु",
    Rashi.CANCER:      "वारि",   # Traditional Marathi: वारि (not जल)
    Rashi.SCORPIO:     "वारि",
    Rashi.PISCES:      "वारि",
}
RASHI_TO_TATVA_EN: dict[Rashi, str] = {
    Rashi.ARIES: "Fire", Rashi.LEO: "Fire", Rashi.SAGITTARIUS: "Fire",
    Rashi.TAURUS: "Earth", Rashi.VIRGO: "Earth", Rashi.CAPRICORN: "Earth",
    Rashi.GEMINI: "Air", Rashi.LIBRA: "Air", Rashi.AQUARIUS: "Air",
    Rashi.CANCER: "Water (Vari)", Rashi.SCORPIO: "Water (Vari)", Rashi.PISCES: "Water (Vari)",
}

# ---------------------------------------------------------------------------
# Yoni — animal symbol from nakshatra (Marathi)
# ---------------------------------------------------------------------------
YONI_NAMES_MR: dict[str, str] = {
    "Horse": "अश्व", "Elephant": "गज", "Sheep": "मेष",
    "Serpent": "सर्प", "Dog": "श्वान", "Cat": "मार्जार",
    "Rat": "मूषक", "Cow": "गो", "Buffalo": "महिष",
    "Tiger": "व्याघ्र", "Deer": "मृग", "Monkey": "वानर",
    "Mongoose": "मुंगूस", "Lion": "सिंह",
}


def format_dms(deg_float: float) -> str:
    """Format degrees float into DD:MM:SS format (अंश:कला:विकला)."""
    deg = int(deg_float)
    rem_min = (deg_float - deg) * 60
    minutes = int(rem_min)
    seconds = int(round((rem_min - minutes) * 60))
    if seconds >= 60:
        seconds = 0
        minutes += 1
    if minutes >= 60:
        minutes = 0
        deg += 1
    return f"{deg:02d}:{minutes:02d}:{seconds:02d}"


# ---------------------------------------------------------------------------
# Karana, Yoga, Tithi calculation from Moon-Sun angle
# ---------------------------------------------------------------------------
def compute_karana(moon_lon: float, sun_lon: float) -> tuple[str, str]:
    """Compute Karana from Moon-Sun angle."""
    angle = (moon_lon - sun_lon) % 360
    tithi_num = int(angle / 12)
    half = int((angle % 12) / 6)
    karana_num = tithi_num * 2 + half

    if karana_num == 0:
        return KARANA_NAMES_MR[10], KARANA_NAMES_EN[10]
    elif karana_num == 57:
        return KARANA_NAMES_MR[7], KARANA_NAMES_EN[7]
    elif karana_num == 58:
        return KARANA_NAMES_MR[8], KARANA_NAMES_EN[8]
    elif karana_num == 59:
        return KARANA_NAMES_MR[9], KARANA_NAMES_EN[9]
    else:
        idx = (karana_num - 1) % 7
        return KARANA_NAMES_MR[idx], KARANA_NAMES_EN[idx]


def compute_yoga(moon_lon: float, sun_lon: float) -> tuple[str, str]:
    """Compute Nitya Yoga from (Moon + Sun) longitude."""
    yoga_span = 360.0 / 27  # 13.3333°
    idx = int(((moon_lon + sun_lon) % 360) / yoga_span) % 27
    return YOGA_NAMES_MR[idx], YOGA_NAMES_EN[idx]


def compute_tithi(moon_lon: float, sun_lon: float) -> str:
    """Compute Tithi from (Moon - Sun) longitude angle."""
    idx = int(((moon_lon - sun_lon) % 360) / 12.0) % 30
    return TITHI_NAMES_MR[idx]


# ---------------------------------------------------------------------------
# Avakahada Chakra
# ---------------------------------------------------------------------------
def compute_avakahada(result: KundaliResult, raw_ephemeris: Optional[dict] = None) -> dict:
    """
    Compute the full Avakahada Chakra for a KundaliResult.
    """
    if result.rashi is None or result.nakshatra is None:
        return {}

    nakshatra = result.nakshatra
    rashi = result.rashi
    lagna = result.lagna

    # Varna
    varna = RASHI_TO_VARNA.get(rashi)
    varna_mr = varna.name_mr if varna else ""
    varna_en = varna.value if varna else ""

    # Vashya
    vashya_mr = RASHI_TO_VASHYA_MR.get(rashi, "")
    vashya_en = RASHI_TO_VASHYA_EN.get(rashi, "")

    # Tatva
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

    # Varga & Yunja
    varga_mr = NAKSHATRA_VARGA_MR.get(nakshatra, "")
    yunja_mr = NAKSHATRA_YUNJA_MR.get(nakshatra, "")

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

    # Karana, Yoga, Tithi
    karana_mr, karana_en = "", ""
    yoga_mr, yoga_en = "", ""
    tithi_mr = ""
    if raw_ephemeris:
        try:
            planets_raw = raw_ephemeris.get("planets", {})
            moon_data = planets_raw.get(Planet.MOON)
            sun_data = planets_raw.get(Planet.SUN)
            if moon_data and sun_data:
                m_lon = moon_data["longitude"]
                s_lon = sun_data["longitude"]
                karana_mr, karana_en = compute_karana(m_lon, s_lon)
                yoga_mr, yoga_en = compute_yoga(m_lon, s_lon)
                tithi_mr = compute_tithi(m_lon, s_lon)
        except Exception as ke:
            logger.warning("Karana/Yoga/Tithi computation failed: %s", ke)

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
        "yoga_mr": yoga_mr,
        "yoga_en": yoga_en,
        "tithi_mr": tithi_mr,
        "varna_mr": varna_mr,
        "varna_en": varna_en,
        "vashya_mr": vashya_mr,
        "vashya_en": vashya_en,
        "tatva_mr": tatva_mr,
        "tatva_en": tatva_en,
        "varga_mr": varga_mr,
        "varga_en": varga_mr,
        "yunja_mr": yunja_mr,
        "yunja_en": yunja_mr,
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
    """Compute ALL 9 Mahadasha periods from birth."""
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
