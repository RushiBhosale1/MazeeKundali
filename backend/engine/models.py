"""
engine/models.py
Shared data models / dataclasses used throughout the engine.
These are pure Python dataclasses — no SQLAlchemy, no Pydantic.
The API layer will convert these to Pydantic response models.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class Planet(str, Enum):
    SUN = "Sun"
    MOON = "Moon"
    MARS = "Mars"
    MERCURY = "Mercury"
    JUPITER = "Jupiter"
    VENUS = "Venus"
    SATURN = "Saturn"
    RAHU = "Rahu"
    KETU = "Ketu"

    @property
    def name_mr(self) -> str:
        return PLANET_NAMES_MR[self]


PLANET_NAMES_MR: dict[Planet, str] = {
    Planet.SUN: "सूर्य",
    Planet.MOON: "चंद्र",
    Planet.MARS: "मंगळ",
    Planet.MERCURY: "बुध",
    Planet.JUPITER: "गुरु",
    Planet.VENUS: "शुक्र",
    Planet.SATURN: "शनि",
    Planet.RAHU: "राहू",
    Planet.KETU: "केतू",
}


class Rashi(int, Enum):
    ARIES = 0        # मेष
    TAURUS = 1       # वृषभ
    GEMINI = 2       # मिथुन
    CANCER = 3       # कर्क
    LEO = 4          # सिंह
    VIRGO = 5        # कन्या
    LIBRA = 6        # तुळ
    SCORPIO = 7      # वृश्चिक
    SAGITTARIUS = 8  # धनु
    CAPRICORN = 9    # मकर
    AQUARIUS = 10    # कुंभ
    PISCES = 11      # मीन

    @property
    def name_en(self) -> str:
        return RASHI_NAMES_EN[self]

    @property
    def name_mr(self) -> str:
        return RASHI_NAMES_MR[self]


RASHI_NAMES_EN: dict[Rashi, str] = {
    Rashi.ARIES: "Aries", Rashi.TAURUS: "Taurus", Rashi.GEMINI: "Gemini",
    Rashi.CANCER: "Cancer", Rashi.LEO: "Leo", Rashi.VIRGO: "Virgo",
    Rashi.LIBRA: "Libra", Rashi.SCORPIO: "Scorpio", Rashi.SAGITTARIUS: "Sagittarius",
    Rashi.CAPRICORN: "Capricorn", Rashi.AQUARIUS: "Aquarius", Rashi.PISCES: "Pisces",
}

RASHI_NAMES_MR: dict[Rashi, str] = {
    Rashi.ARIES: "मेष", Rashi.TAURUS: "वृषभ", Rashi.GEMINI: "मिथुन",
    Rashi.CANCER: "कर्क", Rashi.LEO: "सिंह", Rashi.VIRGO: "कन्या",
    Rashi.LIBRA: "तुळ", Rashi.SCORPIO: "वृश्चिक", Rashi.SAGITTARIUS: "धनु",
    Rashi.CAPRICORN: "मकर", Rashi.AQUARIUS: "कुंभ", Rashi.PISCES: "मीन",
}


class Nakshatra(int, Enum):
    ASHWINI = 0
    BHARANI = 1
    KRITTIKA = 2
    ROHINI = 3
    MRIGASHIRA = 4
    ARDRA = 5
    PUNARVASU = 6
    PUSHYA = 7
    ASHLESHA = 8
    MAGHA = 9
    PURVA_PHALGUNI = 10
    UTTARA_PHALGUNI = 11
    HASTA = 12
    CHITRA = 13
    SWATI = 14
    VISHAKHA = 15
    ANURADHA = 16
    JYESHTHA = 17
    MULA = 18
    PURVA_ASHADHA = 19
    UTTARA_ASHADHA = 20
    SHRAVANA = 21
    DHANISHTA = 22
    SHATABHISHA = 23
    PURVA_BHADRAPADA = 24
    UTTARA_BHADRAPADA = 25
    REVATI = 26

    @property
    def name_en(self) -> str:
        return NAKSHATRA_NAMES_EN[self]

    @property
    def name_mr(self) -> str:
        return NAKSHATRA_NAMES_MR[self]


NAKSHATRA_NAMES_EN: dict[Nakshatra, str] = {
    Nakshatra.ASHWINI: "Ashwini", Nakshatra.BHARANI: "Bharani",
    Nakshatra.KRITTIKA: "Krittika", Nakshatra.ROHINI: "Rohini",
    Nakshatra.MRIGASHIRA: "Mrigashira", Nakshatra.ARDRA: "Ardra",
    Nakshatra.PUNARVASU: "Punarvasu", Nakshatra.PUSHYA: "Pushya",
    Nakshatra.ASHLESHA: "Ashlesha", Nakshatra.MAGHA: "Magha",
    Nakshatra.PURVA_PHALGUNI: "Purva Phalguni", Nakshatra.UTTARA_PHALGUNI: "Uttara Phalguni",
    Nakshatra.HASTA: "Hasta", Nakshatra.CHITRA: "Chitra",
    Nakshatra.SWATI: "Swati", Nakshatra.VISHAKHA: "Vishakha",
    Nakshatra.ANURADHA: "Anuradha", Nakshatra.JYESHTHA: "Jyeshtha",
    Nakshatra.MULA: "Mula", Nakshatra.PURVA_ASHADHA: "Purva Ashadha",
    Nakshatra.UTTARA_ASHADHA: "Uttara Ashadha", Nakshatra.SHRAVANA: "Shravana",
    Nakshatra.DHANISHTA: "Dhanishta", Nakshatra.SHATABHISHA: "Shatabhisha",
    Nakshatra.PURVA_BHADRAPADA: "Purva Bhadrapada",
    Nakshatra.UTTARA_BHADRAPADA: "Uttara Bhadrapada", Nakshatra.REVATI: "Revati",
}

NAKSHATRA_NAMES_MR: dict[Nakshatra, str] = {
    Nakshatra.ASHWINI: "अश्विनी", Nakshatra.BHARANI: "भरणी",
    Nakshatra.KRITTIKA: "कृत्तिका", Nakshatra.ROHINI: "रोहिणी",
    Nakshatra.MRIGASHIRA: "मृगशीर्ष", Nakshatra.ARDRA: "आर्द्रा",
    Nakshatra.PUNARVASU: "पुनर्वसू", Nakshatra.PUSHYA: "पुष्य",
    Nakshatra.ASHLESHA: "आश्लेषा", Nakshatra.MAGHA: "मघा",
    Nakshatra.PURVA_PHALGUNI: "पूर्वा फाल्गुनी", Nakshatra.UTTARA_PHALGUNI: "उत्तरा फाल्गुनी",
    Nakshatra.HASTA: "हस्त", Nakshatra.CHITRA: "चित्रा",
    Nakshatra.SWATI: "स्वाती", Nakshatra.VISHAKHA: "विशाखा",
    Nakshatra.ANURADHA: "अनुराधा", Nakshatra.JYESHTHA: "ज्येष्ठा",
    Nakshatra.MULA: "मूळ", Nakshatra.PURVA_ASHADHA: "पूर्वाषाढा",
    Nakshatra.UTTARA_ASHADHA: "उत्तराषाढा", Nakshatra.SHRAVANA: "श्रवण",
    Nakshatra.DHANISHTA: "धनिष्ठा", Nakshatra.SHATABHISHA: "शततारका",
    Nakshatra.PURVA_BHADRAPADA: "पूर्वा भाद्रपदा",
    Nakshatra.UTTARA_BHADRAPADA: "उत्तरा भाद्रपदा", Nakshatra.REVATI: "रेवती",
}


class Gana(str, Enum):
    DEVA = "Deva"
    MANUSHYA = "Manushya"
    RAKSHASA = "Rakshasa"

    @property
    def name_mr(self) -> str:
        return {"Deva": "देव", "Manushya": "मनुष्य", "Rakshasa": "राक्षस"}[self.value]


class Nadi(str, Enum):
    AADI = "Aadi"
    MADHYA = "Madhya"
    ANTYA = "Antya"

    @property
    def name_mr(self) -> str:
        return {"Aadi": "आदी", "Madhya": "मध्य", "Antya": "अंत्य"}[self.value]


class Varna(str, Enum):
    BRAHMIN = "Brahmin"
    KSHATRIYA = "Kshatriya"
    VAISHYA = "Vaishya"
    SHUDRA = "Shudra"

    @property
    def name_mr(self) -> str:
        return {
            "Brahmin": "ब्राह्मण", "Kshatriya": "क्षत्रिय",
            "Vaishya": "वैश्य", "Shudra": "शूद्र",
        }[self.value]

    @property
    def rank(self) -> int:
        return {"Brahmin": 4, "Kshatriya": 3, "Vaishya": 2, "Shudra": 1}[self.value]


class RahuMode(str, Enum):
    TRUE_NODE = "true_node"
    MEAN_NODE = "mean_node"


class TimeAccuracy(str, Enum):
    EXACT = "exact"
    APPROXIMATE = "approximate"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Core result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class PlaceResult:
    display_name: str
    latitude: float
    longitude: float
    tz_iana: str
    source: str = "nominatim"  # "cache" | "nominatim" | "manual"


@dataclass
class PlanetPosition:
    planet: Planet
    longitude: float          # sidereal degrees (0–360)
    rashi: Rashi
    degree_in_rashi: float    # 0–29.99° within the sign
    house: int                # 1–12 (Whole Sign)
    nakshatra: Nakshatra
    pada: int                 # 1–4
    degree_in_nakshatra: float
    retrograde: bool
    is_exalted: bool = False
    is_debilitated: bool = False


@dataclass
class DashaResult:
    mahadasha_lord: Planet
    mahadasha_start: date
    mahadasha_end: date
    antardasha_lord: Planet
    antardasha_start: date
    antardasha_end: date
    # Stretch: pratyantardasha; skip for MVP


@dataclass
class MangalDoshaResult:
    is_manglik: bool
    severity: str                  # "HIGH" | "MILD" | "NONE"
    reference_point: str           # "Lagna" | "Moon" | "Venus"
    mars_house: Optional[int]      # which house Mars is in from the reference point
    cancellation_applied: bool
    cancellation_rule: Optional[str]
    explanation_mr: str
    explanation_en: str


@dataclass
class KundaliResult:
    """
    Full output of the kundali computation pipeline.
    The API layer will decide which fields to expose based on paid status.
    """
    # Birth identity (echo back)
    name: str
    gender: str
    dob: date
    time_of_birth: Optional[str]   # "HH:MM" local; None if unknown
    time_accuracy: TimeAccuracy
    place_text: str
    latitude: float
    longitude: float
    tz_iana: str
    utc_datetime: Optional[datetime]  # None if time unknown

    # Engine settings used
    ayanamsa: str = "lahiri"
    house_system: str = "whole_sign"
    rahu_mode: RahuMode = RahuMode.TRUE_NODE

    # --- FREE TIER ---
    rashi: Optional[Rashi] = None
    nakshatra: Optional[Nakshatra] = None
    pada: Optional[int] = None
    lagna: Optional[Rashi] = None
    gana: Optional[Gana] = None
    nadi: Optional[Nadi] = None
    varna: Optional[Varna] = None

    # --- PAID TIER ---
    planet_positions: List[PlanetPosition] = field(default_factory=list)
    dasha: Optional[DashaResult] = None
    mangal_dosha: Optional[MangalDoshaResult] = None

    # Flags
    lagna_reliable: bool = True  # False if time_accuracy != EXACT
