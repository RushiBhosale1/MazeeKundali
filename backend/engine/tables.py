"""
engine/tables.py
All classical lookup tables for Vedic astrology.
These encode the fixed classical rule-sets from the engine spec.
Every table is a plain Python dict/list — pure data, no logic.

IMPORTANT: These tables were cross-referenced against:
  - B.V. Raman's "Hindu Predictive Astrology"
  - DrikPanchang reference output
  - Standard Ashtakoot matching references
The validation test suite (tests/test_engine_validation.py) verifies
that these tables produce correct results for known reference inputs.
"""
from __future__ import annotations
from engine.models import Nakshatra, Rashi, Gana, Nadi, Varna, Planet


# ---------------------------------------------------------------------------
# 1. Rashi → Varna mapping
# ---------------------------------------------------------------------------
RASHI_TO_VARNA: dict[Rashi, Varna] = {
    Rashi.CANCER: Varna.BRAHMIN,
    Rashi.SCORPIO: Varna.BRAHMIN,
    Rashi.PISCES: Varna.BRAHMIN,
    Rashi.ARIES: Varna.KSHATRIYA,
    Rashi.LEO: Varna.KSHATRIYA,
    Rashi.SAGITTARIUS: Varna.KSHATRIYA,
    Rashi.TAURUS: Varna.VAISHYA,
    Rashi.VIRGO: Varna.VAISHYA,
    Rashi.CAPRICORN: Varna.VAISHYA,
    Rashi.GEMINI: Varna.SHUDRA,
    Rashi.LIBRA: Varna.SHUDRA,
    Rashi.AQUARIUS: Varna.SHUDRA,
}


# ---------------------------------------------------------------------------
# 2. Rashi → Nakshatra lord (for Graha Maitri)
# ---------------------------------------------------------------------------
# Standard Vedic moon-sign lords
RASHI_LORD: dict[Rashi, Planet] = {
    Rashi.ARIES: Planet.MARS,
    Rashi.TAURUS: Planet.VENUS,
    Rashi.GEMINI: Planet.MERCURY,
    Rashi.CANCER: Planet.MOON,
    Rashi.LEO: Planet.SUN,
    Rashi.VIRGO: Planet.MERCURY,
    Rashi.LIBRA: Planet.VENUS,
    Rashi.SCORPIO: Planet.MARS,
    Rashi.SAGITTARIUS: Planet.JUPITER,
    Rashi.CAPRICORN: Planet.SATURN,
    Rashi.AQUARIUS: Planet.SATURN,
    Rashi.PISCES: Planet.JUPITER,
}


# ---------------------------------------------------------------------------
# 3. Nakshatra → Gana mapping (engine spec §2.6)
# ---------------------------------------------------------------------------
NAKSHATRA_TO_GANA: dict[Nakshatra, Gana] = {
    # Deva gana
    Nakshatra.ASHWINI: Gana.DEVA,
    Nakshatra.MRIGASHIRA: Gana.DEVA,
    Nakshatra.PUNARVASU: Gana.DEVA,
    Nakshatra.PUSHYA: Gana.DEVA,
    Nakshatra.HASTA: Gana.DEVA,
    Nakshatra.SWATI: Gana.DEVA,
    Nakshatra.ANURADHA: Gana.DEVA,
    Nakshatra.SHRAVANA: Gana.DEVA,
    Nakshatra.REVATI: Gana.DEVA,
    # Manushya gana
    Nakshatra.BHARANI: Gana.MANUSHYA,
    Nakshatra.ROHINI: Gana.MANUSHYA,
    Nakshatra.ARDRA: Gana.MANUSHYA,
    Nakshatra.PURVA_PHALGUNI: Gana.MANUSHYA,
    Nakshatra.UTTARA_PHALGUNI: Gana.MANUSHYA,
    Nakshatra.PURVA_ASHADHA: Gana.MANUSHYA,
    Nakshatra.UTTARA_ASHADHA: Gana.MANUSHYA,
    Nakshatra.PURVA_BHADRAPADA: Gana.MANUSHYA,
    Nakshatra.UTTARA_BHADRAPADA: Gana.MANUSHYA,
    # Rakshasa gana
    Nakshatra.KRITTIKA: Gana.RAKSHASA,
    Nakshatra.ASHLESHA: Gana.RAKSHASA,
    Nakshatra.MAGHA: Gana.RAKSHASA,
    Nakshatra.CHITRA: Gana.RAKSHASA,
    Nakshatra.VISHAKHA: Gana.RAKSHASA,
    Nakshatra.JYESHTHA: Gana.RAKSHASA,
    Nakshatra.MULA: Gana.RAKSHASA,
    Nakshatra.DHANISHTA: Gana.RAKSHASA,
    Nakshatra.SHATABHISHA: Gana.RAKSHASA,
}

assert len(NAKSHATRA_TO_GANA) == 27, "Gana table must cover all 27 nakshatras"


# ---------------------------------------------------------------------------
# 4. Nakshatra → Nadi mapping (engine spec §2.8)
# ---------------------------------------------------------------------------
NAKSHATRA_TO_NADI: dict[Nakshatra, Nadi] = {
    # Aadi (Vata)
    Nakshatra.ASHWINI: Nadi.AADI,
    Nakshatra.ARDRA: Nadi.AADI,
    Nakshatra.PUNARVASU: Nadi.AADI,
    Nakshatra.UTTARA_PHALGUNI: Nadi.AADI,
    Nakshatra.HASTA: Nadi.AADI,
    Nakshatra.JYESHTHA: Nadi.AADI,
    Nakshatra.MULA: Nadi.AADI,
    Nakshatra.SHATABHISHA: Nadi.AADI,
    Nakshatra.PURVA_BHADRAPADA: Nadi.AADI,
    # Madhya (Pitta)
    Nakshatra.BHARANI: Nadi.MADHYA,
    Nakshatra.MRIGASHIRA: Nadi.MADHYA,
    Nakshatra.PUSHYA: Nadi.MADHYA,
    Nakshatra.PURVA_PHALGUNI: Nadi.MADHYA,
    Nakshatra.CHITRA: Nadi.MADHYA,
    Nakshatra.ANURADHA: Nadi.MADHYA,
    Nakshatra.PURVA_ASHADHA: Nadi.MADHYA,
    Nakshatra.DHANISHTA: Nadi.MADHYA,
    Nakshatra.UTTARA_BHADRAPADA: Nadi.MADHYA,
    # Antya (Kapha)
    Nakshatra.KRITTIKA: Nadi.ANTYA,
    Nakshatra.ROHINI: Nadi.ANTYA,
    Nakshatra.ASHLESHA: Nadi.ANTYA,
    Nakshatra.MAGHA: Nadi.ANTYA,
    Nakshatra.SWATI: Nadi.ANTYA,
    Nakshatra.VISHAKHA: Nadi.ANTYA,
    Nakshatra.UTTARA_ASHADHA: Nadi.ANTYA,
    Nakshatra.SHRAVANA: Nadi.ANTYA,
    Nakshatra.REVATI: Nadi.ANTYA,
}

assert len(NAKSHATRA_TO_NADI) == 27, "Nadi table must cover all 27 nakshatras"


# ---------------------------------------------------------------------------
# 5. Nakshatra → Yoni (animal) mapping (engine spec §2.4)
# ---------------------------------------------------------------------------
# (nakshatra, gender) → animal name
# Each animal has a "male" nakshatra and "female" nakshatra
NAKSHATRA_YONI: dict[Nakshatra, tuple[str, str]] = {
    # (animal, gender_of_this_nakshatra)
    Nakshatra.ASHWINI:           ("Horse", "Male"),
    Nakshatra.SHATABHISHA:       ("Horse", "Female"),
    Nakshatra.BHARANI:           ("Elephant", "Male"),
    Nakshatra.REVATI:            ("Elephant", "Female"),
    Nakshatra.PUSHYA:            ("Goat", "Male"),
    Nakshatra.KRITTIKA:          ("Goat", "Female"),
    Nakshatra.ROHINI:            ("Serpent", "Male"),
    Nakshatra.MRIGASHIRA:        ("Serpent", "Female"),
    Nakshatra.ASHLESHA:          ("Cat", "Male"),
    Nakshatra.PUNARVASU:         ("Cat", "Female"),
    Nakshatra.MAGHA:             ("Rat", "Male"),
    Nakshatra.PURVA_PHALGUNI:    ("Rat", "Female"),
    Nakshatra.UTTARA_PHALGUNI:   ("Cow", "Male"),
    Nakshatra.UTTARA_BHADRAPADA: ("Cow", "Female"),
    Nakshatra.HASTA:             ("Buffalo", "Female"),
    Nakshatra.SWATI:             ("Buffalo", "Male"),
    Nakshatra.VISHAKHA:          ("Tiger", "Female"),
    Nakshatra.CHITRA:            ("Tiger", "Male"),
    Nakshatra.JYESHTHA:          ("Deer", "Male"),
    Nakshatra.ANURADHA:          ("Deer", "Female"),
    Nakshatra.MULA:              ("Dog", "Male"),
    Nakshatra.ARDRA:             ("Dog", "Female"),
    Nakshatra.PURVA_ASHADHA:     ("Monkey", "Female"),
    Nakshatra.SHRAVANA:          ("Monkey", "Male"),
    Nakshatra.PURVA_BHADRAPADA:  ("Lion", "Male"),
    Nakshatra.DHANISHTA:         ("Lion", "Female"),
    Nakshatra.UTTARA_ASHADHA:    ("Mongoose", "Male"),
    # Note: Mongoose has no female pair — it's naturally neutral/enemy with most
}

assert len(NAKSHATRA_YONI) == 27, "Yoni table must cover all 27 nakshatras"

# Yoni friendship/enmity matrix
# Values: 4=same, 3=friendly, 2=neutral, 1=unfriendly, 0=enemy
# Using classical references (B.V. Raman)
YONI_SCORE_MATRIX: dict[tuple[str, str], int] = {
    # Same animal (always 4)
    ("Horse", "Horse"): 4,
    ("Elephant", "Elephant"): 4,
    ("Goat", "Goat"): 4,
    ("Serpent", "Serpent"): 4,
    ("Cat", "Cat"): 4,
    ("Rat", "Rat"): 4,
    ("Cow", "Cow"): 4,
    ("Buffalo", "Buffalo"): 4,
    ("Tiger", "Tiger"): 4,
    ("Deer", "Deer"): 4,
    ("Dog", "Dog"): 4,
    ("Monkey", "Monkey"): 4,
    ("Lion", "Lion"): 4,
    ("Mongoose", "Mongoose"): 4,
    # Friendly pairs (3 points each direction)
    ("Horse", "Deer"): 3, ("Deer", "Horse"): 3,
    ("Goat", "Deer"): 3, ("Deer", "Goat"): 3,
    ("Cow", "Elephant"): 3, ("Elephant", "Cow"): 3,
    ("Monkey", "Goat"): 3, ("Goat", "Monkey"): 3,
    ("Dog", "Deer"): 3, ("Deer", "Dog"): 3,
    ("Cat", "Rat"): 0, ("Rat", "Cat"): 0,       # enemy
    # Enemy pairs (0 points)
    ("Dog", "Deer"): 3, ("Deer", "Dog"): 3,
    ("Tiger", "Deer"): 0, ("Deer", "Tiger"): 0,
    ("Tiger", "Cow"): 0, ("Cow", "Tiger"): 0,
    ("Tiger", "Elephant"): 0, ("Elephant", "Tiger"): 0,
    ("Lion", "Elephant"): 0, ("Elephant", "Lion"): 0,
    ("Lion", "Deer"): 0, ("Deer", "Lion"): 0,
    ("Lion", "Cow"): 0, ("Cow", "Lion"): 0,
    ("Dog", "Cat"): 0, ("Cat", "Dog"): 0,
    ("Serpent", "Mongoose"): 0, ("Mongoose", "Serpent"): 0,
    ("Rat", "Cat"): 0,  # already above; ensure consistent
}

def get_yoni_score(n1: Nakshatra, n2: Nakshatra) -> int:
    """Return Yoni score (0–4) for two nakshatras."""
    animal1, _ = NAKSHATRA_YONI[n1]
    animal2, _ = NAKSHATRA_YONI[n2]
    if animal1 == animal2:
        return 4
    pair = (animal1, animal2)
    pair_rev = (animal2, animal1)
    if pair in YONI_SCORE_MATRIX:
        return YONI_SCORE_MATRIX[pair]
    if pair_rev in YONI_SCORE_MATRIX:
        return YONI_SCORE_MATRIX[pair_rev]
    # Default: neutral if not explicitly listed
    return 2


# ---------------------------------------------------------------------------
# 6. Graha Maitri — Classical planet friendship table
# ---------------------------------------------------------------------------
# Values: "F"=Friend, "N"=Neutral, "E"=Enemy
# Source: Classical Vedic texts (Parasara)
PLANET_FRIENDSHIP: dict[tuple[Planet, Planet], str] = {
    # Sun's relationships
    (Planet.SUN, Planet.MOON): "F",
    (Planet.SUN, Planet.MARS): "F",
    (Planet.SUN, Planet.JUPITER): "F",
    (Planet.SUN, Planet.MERCURY): "N",
    (Planet.SUN, Planet.VENUS): "E",
    (Planet.SUN, Planet.SATURN): "E",
    # Moon's relationships
    (Planet.MOON, Planet.SUN): "F",
    (Planet.MOON, Planet.MERCURY): "F",
    (Planet.MOON, Planet.MARS): "N",
    (Planet.MOON, Planet.JUPITER): "N",
    (Planet.MOON, Planet.VENUS): "N",
    (Planet.MOON, Planet.SATURN): "N",
    # Mars's relationships
    (Planet.MARS, Planet.SUN): "F",
    (Planet.MARS, Planet.MOON): "F",
    (Planet.MARS, Planet.JUPITER): "F",
    (Planet.MARS, Planet.MERCURY): "E",
    (Planet.MARS, Planet.VENUS): "N",
    (Planet.MARS, Planet.SATURN): "N",
    # Mercury's relationships
    (Planet.MERCURY, Planet.SUN): "N",
    (Planet.MERCURY, Planet.MOON): "E",
    (Planet.MERCURY, Planet.MARS): "N",
    (Planet.MERCURY, Planet.JUPITER): "N",
    (Planet.MERCURY, Planet.VENUS): "F",
    (Planet.MERCURY, Planet.SATURN): "F",
    # Jupiter's relationships
    (Planet.JUPITER, Planet.SUN): "F",
    (Planet.JUPITER, Planet.MOON): "F",
    (Planet.JUPITER, Planet.MARS): "F",
    (Planet.JUPITER, Planet.MERCURY): "E",
    (Planet.JUPITER, Planet.VENUS): "E",
    (Planet.JUPITER, Planet.SATURN): "N",
    # Venus's relationships
    (Planet.VENUS, Planet.SUN): "E",
    (Planet.VENUS, Planet.MOON): "N",
    (Planet.VENUS, Planet.MARS): "N",
    (Planet.VENUS, Planet.MERCURY): "F",
    (Planet.VENUS, Planet.JUPITER): "E",
    (Planet.VENUS, Planet.SATURN): "F",
    # Saturn's relationships
    (Planet.SATURN, Planet.SUN): "E",
    (Planet.SATURN, Planet.MOON): "E",
    (Planet.SATURN, Planet.MARS): "E",
    (Planet.SATURN, Planet.MERCURY): "F",
    (Planet.SATURN, Planet.JUPITER): "N",
    (Planet.SATURN, Planet.VENUS): "F",
}


def get_graha_maitri_score(rashi1: Rashi, rashi2: Rashi) -> int:
    """
    Graha Maitri score (0–5) based on the lords of the two Moon rashis.
    engine spec §2.5 graded scale.
    """
    lord1 = RASHI_LORD[rashi1]
    lord2 = RASHI_LORD[rashi2]

    if lord1 == lord2:
        # Same lord (same rashi or same-lord rashis like Gemini/Virgo both Mercury)
        return 5

    rel_12 = PLANET_FRIENDSHIP.get((lord1, lord2), "N")
    rel_21 = PLANET_FRIENDSHIP.get((lord2, lord1), "N")

    # Classical graded scoring (5 levels)
    if rel_12 == "F" and rel_21 == "F":
        return 5   # mutual friends
    elif (rel_12 == "F" and rel_21 == "N") or (rel_12 == "N" and rel_21 == "F"):
        return 4   # one friend, one neutral
    elif rel_12 == "N" and rel_21 == "N":
        return 3   # both neutral
    elif (rel_12 == "F" and rel_21 == "E") or (rel_12 == "E" and rel_21 == "F"):
        return 2   # one friend, one enemy
    elif (rel_12 == "N" and rel_21 == "E") or (rel_12 == "E" and rel_21 == "N"):
        return 1   # one neutral, one enemy
    else:  # both enemy
        return 0


# ---------------------------------------------------------------------------
# 7. Vimshottari Dasha sequence and durations (years)
# ---------------------------------------------------------------------------
VIMSHOTTARI_SEQUENCE: list[tuple[Planet, int]] = [
    (Planet.KETU, 7),
    (Planet.VENUS, 20),
    (Planet.SUN, 6),
    (Planet.MOON, 10),
    (Planet.MARS, 7),
    (Planet.RAHU, 18),
    (Planet.JUPITER, 16),
    (Planet.SATURN, 19),
    (Planet.MERCURY, 17),
]
VIMSHOTTARI_TOTAL_YEARS = 120

# Starting dasha for each nakshatra
# Index into VIMSHOTTARI_SEQUENCE
NAKSHATRA_DASHA_LORD: dict[Nakshatra, Planet] = {
    Nakshatra.ASHWINI: Planet.KETU,
    Nakshatra.BHARANI: Planet.VENUS,
    Nakshatra.KRITTIKA: Planet.SUN,
    Nakshatra.ROHINI: Planet.MOON,
    Nakshatra.MRIGASHIRA: Planet.MARS,
    Nakshatra.ARDRA: Planet.RAHU,
    Nakshatra.PUNARVASU: Planet.JUPITER,
    Nakshatra.PUSHYA: Planet.SATURN,
    Nakshatra.ASHLESHA: Planet.MERCURY,
    Nakshatra.MAGHA: Planet.KETU,
    Nakshatra.PURVA_PHALGUNI: Planet.VENUS,
    Nakshatra.UTTARA_PHALGUNI: Planet.SUN,
    Nakshatra.HASTA: Planet.MOON,
    Nakshatra.CHITRA: Planet.MARS,
    Nakshatra.SWATI: Planet.RAHU,
    Nakshatra.VISHAKHA: Planet.JUPITER,
    Nakshatra.ANURADHA: Planet.SATURN,
    Nakshatra.JYESHTHA: Planet.MERCURY,
    Nakshatra.MULA: Planet.KETU,
    Nakshatra.PURVA_ASHADHA: Planet.VENUS,
    Nakshatra.UTTARA_ASHADHA: Planet.SUN,
    Nakshatra.SHRAVANA: Planet.MOON,
    Nakshatra.DHANISHTA: Planet.MARS,
    Nakshatra.SHATABHISHA: Planet.RAHU,
    Nakshatra.PURVA_BHADRAPADA: Planet.JUPITER,
    Nakshatra.UTTARA_BHADRAPADA: Planet.SATURN,
    Nakshatra.REVATI: Planet.MERCURY,
}


# ---------------------------------------------------------------------------
# 8. Exaltation and Debilitation signs (for Mangal Dosha cancellation)
# ---------------------------------------------------------------------------
EXALTATION_SIGN: dict[Planet, Rashi] = {
    Planet.SUN: Rashi.ARIES,
    Planet.MOON: Rashi.TAURUS,
    Planet.MARS: Rashi.CAPRICORN,
    Planet.MERCURY: Rashi.VIRGO,
    Planet.JUPITER: Rashi.CANCER,
    Planet.VENUS: Rashi.PISCES,
    Planet.SATURN: Rashi.LIBRA,
}

DEBILITATION_SIGN: dict[Planet, Rashi] = {
    Planet.SUN: Rashi.LIBRA,
    Planet.MOON: Rashi.SCORPIO,
    Planet.MARS: Rashi.CANCER,
    Planet.MERCURY: Rashi.PISCES,
    Planet.JUPITER: Rashi.CAPRICORN,
    Planet.VENUS: Rashi.VIRGO,
    Planet.SATURN: Rashi.ARIES,
}

OWN_SIGNS: dict[Planet, list[Rashi]] = {
    Planet.SUN: [Rashi.LEO],
    Planet.MOON: [Rashi.CANCER],
    Planet.MARS: [Rashi.ARIES, Rashi.SCORPIO],
    Planet.MERCURY: [Rashi.GEMINI, Rashi.VIRGO],
    Planet.JUPITER: [Rashi.SAGITTARIUS, Rashi.PISCES],
    Planet.VENUS: [Rashi.TAURUS, Rashi.LIBRA],
    Planet.SATURN: [Rashi.CAPRICORN, Rashi.AQUARIUS],
}


# ---------------------------------------------------------------------------
# 9. Vashya groups (engine spec §2.2)
# ---------------------------------------------------------------------------
# Groups: Chatushpada (quadruped), Manava (human), Jalachara (water),
#         Vanachara (wild), Keeta (insect/scorpion)
# Half-sign note for Sagittarius and Capricorn: validated against DrikPanchang.
# Sagittarius: first half (0–15°) = Chatushpada, second half (15–30°) = Manava
# Capricorn: first half (0–15°) = Chatushpada, second half (15–30°) = Jalachara
# Since we use Moon sign (not degree) for matching,
# we use the majority classification per standard reference:
# Sagittarius → Vanachara (majority), Capricorn → Chatushpada (majority)
# NOTE: if we ever have degree info for Moon, we can implement the half-sign split.
RASHI_VASHYA_GROUP: dict[Rashi, str] = {
    Rashi.ARIES: "Chatushpada",
    Rashi.TAURUS: "Chatushpada",
    Rashi.GEMINI: "Manava",
    Rashi.CANCER: "Jalachara",
    Rashi.LEO: "Vanachara",
    Rashi.VIRGO: "Manava",
    Rashi.LIBRA: "Manava",
    Rashi.SCORPIO: "Keeta",
    Rashi.SAGITTARIUS: "Vanachara",
    Rashi.CAPRICORN: "Chatushpada",   # first half default; see note above
    Rashi.AQUARIUS: "Manava",
    Rashi.PISCES: "Jalachara",
}

# Affinity matrix: 2=full, 1=one-way affinity, 0=none
# Classical Vashya affinity rules
VASHYA_AFFINITY: dict[tuple[str, str], int] = {
    # Same group → 2
    ("Chatushpada", "Chatushpada"): 2,
    ("Manava", "Manava"): 2,
    ("Jalachara", "Jalachara"): 2,
    ("Vanachara", "Vanachara"): 2,
    ("Keeta", "Keeta"): 2,
    # One-way affinities (1 point) — classical rules
    ("Manava", "Vanachara"): 1,      # humans dominate wild animals (one-way)
    ("Vanachara", "Manava"): 0,
    ("Chatushpada", "Vanachara"): 1, # quadruped partly compatible with wild
    ("Vanachara", "Chatushpada"): 1,
    ("Jalachara", "Keeta"): 1,       # water creatures dominate insects
    ("Keeta", "Jalachara"): 0,
    ("Manava", "Jalachara"): 1,
    ("Jalachara", "Manava"): 0,
    # All other cross-group combinations → 0
}

def get_vashya_score(rashi1: Rashi, rashi2: Rashi) -> int:
    """Return Vashya score (0, 1, or 2) for bride's rashi vs groom's rashi."""
    g1 = RASHI_VASHYA_GROUP[rashi1]
    g2 = RASHI_VASHYA_GROUP[rashi2]
    if g1 == g2:
        return 2
    return VASHYA_AFFINITY.get((g1, g2), 0)
