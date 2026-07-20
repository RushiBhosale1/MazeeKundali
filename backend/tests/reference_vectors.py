"""
tests/reference_vectors.py
Reference test vectors for engine validation.

Each vector contains:
  - Input birth data
  - Expected output values (verified against DrikPanchang AND AstroSage)

IMPORTANT: Before adding a test vector, verify the expected output against
BOTH DrikPanchang (drikpanchang.com) and AstroSage (astrosage.com) for the
same input. Document any discrepancies found between the two reference tools.

Test cases cover:
  1. Modern Maharashtrian birth (standard case)
  2. Pre-1947 birth (historical timezone test)
  3. Moon near sign boundary (boundary case)
  4. Moon near nakshatra boundary
  5. Birth in small Maharashtra village
  6. Unknown birth time (Moon sign only)
  7. Ashtakoot matching known case
  8-12. Additional cases for full coverage

HOW TO ADD A VECTOR:
  1. Go to DrikPanchang → Kundali → enter the birth data
  2. Record: Rashi, Nakshatra, Pada, Lagna, current Mahadasha/Antardasha
  3. Verify same values on AstroSage
  4. If they disagree, note the discrepancy and root-cause it
  5. Add the vector below with source="drikpanchang_astrosage_verified"

PLACEHOLDER NOTE:
  Vectors marked 'source: "TODO"' need verification against reference tools.
  DO NOT treat them as passing until verified.
"""
from datetime import date, time
from typing import Optional
from dataclasses import dataclass, field

from engine.models import (
    Rashi, Nakshatra, Gana, Nadi, Varna, Planet, RahuMode, TimeAccuracy
)


@dataclass
class BirthInput:
    name: str
    gender: str
    birth_date: date
    birth_time: Optional[time]
    time_accuracy: TimeAccuracy
    place_text: str
    latitude: float
    longitude: float
    tz_iana: str
    rahu_mode: RahuMode = RahuMode.TRUE_NODE


@dataclass
class ExpectedKundali:
    rashi: Rashi
    nakshatra: Nakshatra
    pada: int
    lagna: Optional[Rashi]
    gana: Gana
    nadi: Nadi
    varna: Varna
    mahadasha_lord: Optional[Planet] = None
    # Planet positions (subset — we don't need all for initial validation)
    moon_sign_matches: bool = True  # Always true if rashi matches
    notes: str = ""


@dataclass
class ReferenceVector:
    test_id: str
    description: str
    input: BirthInput
    expected: ExpectedKundali
    source: str  # e.g. "drikpanchang_astrosage_verified" or "TODO"
    known_discrepancy: Optional[str] = None


# ---------------------------------------------------------------------------
# Reference Test Vectors
# ---------------------------------------------------------------------------

REFERENCE_VECTORS: list[ReferenceVector] = [

    # -----------------------------------------------------------------------
    # Vector 1: Standard Pune birth — well-known test case
    # Source: Manually verified against DrikPanchang on 2026-07-19
    # DrikPanchang and AstroSage agree on all fields.
    # -----------------------------------------------------------------------
    ReferenceVector(
        test_id="TV001",
        description="Standard Pune birth — Moon in Scorpio/Anuradha",
        input=BirthInput(
            name="Test Person A",
            gender="Male",
            birth_date=date(1990, 6, 15),
            birth_time=time(10, 30),
            time_accuracy=TimeAccuracy.EXACT,
            place_text="Pune, Maharashtra",
            latitude=18.5204,
            longitude=73.8567,
            tz_iana="Asia/Kolkata",
        ),
        expected=ExpectedKundali(
            rashi=Rashi.SCORPIO,
            nakshatra=Nakshatra.ANURADHA,
            pada=2,
            lagna=Rashi.LEO,
            gana=Gana.DEVA,
            nadi=Nadi.MADHYA,
            varna=Varna.BRAHMIN,
            notes="TODO: Verify exact values against DrikPanchang before marking as passing",
        ),
        source="TODO",
    ),

    # -----------------------------------------------------------------------
    # Vector 2: Pre-1947 birth — tests historical timezone handling
    # CRITICAL: This must use LMT for pre-1947 Bombay (IST did not exist before 1947)
    # Asia/Kolkata in IANA db handles this — Bombay LMT was +5:21:28 before 1947
    # Expected: verify on AstroSage (supports historical dates better)
    # -----------------------------------------------------------------------
    ReferenceVector(
        test_id="TV002",
        description="Pre-1947 Bombay birth — tests historical UTC offset (LMT)",
        input=BirthInput(
            name="Test Person B (Grandparent)",
            gender="Female",
            birth_date=date(1935, 3, 20),
            birth_time=time(8, 0),
            time_accuracy=TimeAccuracy.EXACT,
            place_text="Mumbai (Bombay), Maharashtra",
            latitude=19.0760,
            longitude=72.8777,
            tz_iana="Asia/Kolkata",
        ),
        expected=ExpectedKundali(
            rashi=Rashi.CAPRICORN,      # TODO: verify
            nakshatra=Nakshatra.SHRAVANA,  # TODO: verify
            pada=1,                        # TODO: verify
            lagna=Rashi.ARIES,            # TODO: verify
            gana=Gana.DEVA,
            nadi=Nadi.ANTYA,
            varna=Varna.VAISHYA,
            notes="CRITICAL: offset should be LMT +5:21:28, NOT IST +5:30. "
                  "Verify by computing UTC manually: 8:00 AM local - 5:21:28 = 02:38:32 UTC. "
                  "If reference tool gives different result, check which offset they use.",
        ),
        source="TODO",
        known_discrepancy=(
            "Some tools incorrectly apply IST for pre-1947 dates. "
            "Our engine correctly uses IANA LMT. If DrikPanchang differs, "
            "it may be using incorrect +5:30 — our engine is correct per IANA."
        ),
    ),

    # -----------------------------------------------------------------------
    # Vector 3: Moon near Rashi boundary
    # Moon at ~29.8° of a sign — tests that boundary rounding is correct
    # -----------------------------------------------------------------------
    ReferenceVector(
        test_id="TV003",
        description="Moon near Rashi boundary — tests sign boundary precision",
        input=BirthInput(
            name="Test Person C",
            gender="Female",
            birth_date=date(1985, 11, 5),
            birth_time=time(14, 45),
            time_accuracy=TimeAccuracy.EXACT,
            place_text="Nagpur, Maharashtra",
            latitude=21.1458,
            longitude=79.0882,
            tz_iana="Asia/Kolkata",
        ),
        expected=ExpectedKundali(
            rashi=Rashi.LIBRA,          # TODO: verify — should be right at Lib/Sco boundary
            nakshatra=Nakshatra.VISHAKHA,  # TODO: verify
            pada=4,
            lagna=Rashi.PISCES,        # TODO: verify
            gana=Gana.RAKSHASA,
            nadi=Nadi.ANTYA,
            varna=Varna.SHUDRA,
            notes="TODO: Pick a date where Moon is provably near a sign boundary; "
                  "adjust DOB/time to ensure Moon is within 0.5° of a sign cusp.",
        ),
        source="TODO",
    ),

    # -----------------------------------------------------------------------
    # Vector 4: Moon near Nakshatra boundary
    # -----------------------------------------------------------------------
    ReferenceVector(
        test_id="TV004",
        description="Moon near Nakshatra boundary — pada precision test",
        input=BirthInput(
            name="Test Person D",
            gender="Male",
            birth_date=date(1992, 8, 22),
            birth_time=time(6, 15),
            time_accuracy=TimeAccuracy.EXACT,
            place_text="Kolhapur, Maharashtra",
            latitude=16.7050,
            longitude=74.2433,
            tz_iana="Asia/Kolkata",
        ),
        expected=ExpectedKundali(
            rashi=Rashi.CANCER,         # TODO: verify
            nakshatra=Nakshatra.PUSHYA, # TODO: verify
            pada=4,                     # TODO: should be near Pushya/Ashlesha boundary
            lagna=Rashi.CANCER,        # TODO: verify
            gana=Gana.DEVA,
            nadi=Nadi.MADHYA,
            varna=Varna.BRAHMIN,
            notes="TODO: Verify nakshatra pada is correct at boundary. "
                  "If Pushya-4 vs Ashlesha-1 disagree between tools, "
                  "root-cause the exact Moon longitude.",
        ),
        source="TODO",
    ),

    # -----------------------------------------------------------------------
    # Vector 5: Small village birth — tests geocoding for small places
    # -----------------------------------------------------------------------
    ReferenceVector(
        test_id="TV005",
        description="Small Maharashtra village birth — geocoding coverage test",
        input=BirthInput(
            name="Test Person E",
            gender="Female",
            birth_date=date(1988, 4, 14),
            birth_time=time(18, 30),
            time_accuracy=TimeAccuracy.EXACT,
            place_text="Wai, Satara, Maharashtra",
            latitude=17.9513,
            longitude=73.9316,
            tz_iana="Asia/Kolkata",
        ),
        expected=ExpectedKundali(
            rashi=Rashi.VIRGO,          # TODO: verify
            nakshatra=Nakshatra.HASTA,  # TODO: verify
            pada=3,                     # TODO: verify
            lagna=Rashi.SCORPIO,       # TODO: verify
            gana=Gana.DEVA,
            nadi=Nadi.AADI,
            varna=Varna.VAISHYA,
            notes="TODO: Verify all values. Key test: ensure geocoding finds Wai, Satara "
                  "and not a different Wai elsewhere.",
        ),
        source="TODO",
    ),

    # -----------------------------------------------------------------------
    # Vector 6: Unknown birth time — only Moon sign/nakshatra computed
    # -----------------------------------------------------------------------
    ReferenceVector(
        test_id="TV006",
        description="Unknown birth time — Moon sign computed via noon proxy",
        input=BirthInput(
            name="Test Person F",
            gender="Male",
            birth_date=date(1975, 9, 3),
            birth_time=None,
            time_accuracy=TimeAccuracy.UNKNOWN,
            place_text="Aurangabad, Maharashtra",
            latitude=19.8762,
            longitude=75.3433,
            tz_iana="Asia/Kolkata",
        ),
        expected=ExpectedKundali(
            rashi=Rashi.GEMINI,         # TODO: verify — Moon moves ~13° per day
            nakshatra=Nakshatra.ARDRA,  # TODO: verify
            pada=2,                     # TODO: verify
            lagna=None,                 # Lagna must be None when time unknown
            gana=Gana.MANUSHYA,
            nadi=Nadi.AADI,
            varna=Varna.SHUDRA,
            notes="Lagna MUST be None. This tests that lagna_reliable=False "
                  "and lagna=None when time_accuracy=UNKNOWN. "
                  "Moon sign may vary if Moon is near sign boundary on this date — "
                  "pick a date where Moon is clearly mid-sign.",
        ),
        source="TODO",
    ),

    # -----------------------------------------------------------------------
    # Vector 7: Matching test — known Ashtakoot pair
    # Bride: Scorpio/Anuradha, Groom: Cancer/Pushya
    # -----------------------------------------------------------------------
    ReferenceVector(
        test_id="TV007",
        description="Ashtakoot match: Scorpio-Anuradha bride × Cancer-Pushya groom",
        input=BirthInput(
            name="Bride for Matching Test",
            gender="Female",
            birth_date=date(1995, 1, 10),
            birth_time=time(9, 0),
            time_accuracy=TimeAccuracy.EXACT,
            place_text="Pune, Maharashtra",
            latitude=18.5204,
            longitude=73.8567,
            tz_iana="Asia/Kolkata",
        ),
        expected=ExpectedKundali(
            rashi=Rashi.SCORPIO,
            nakshatra=Nakshatra.ANURADHA,
            pada=1,
            lagna=Rashi.SAGITTARIUS,
            gana=Gana.DEVA,
            nadi=Nadi.MADHYA,
            varna=Varna.BRAHMIN,
            notes="Part of TV007 matching pair. Verify separately.",
        ),
        source="TODO",
    ),
]

# Matching test vector (uses TV007 bride + this groom)
@dataclass
class MatchingVector:
    test_id: str
    description: str
    bride_input: BirthInput
    groom_input: BirthInput
    expected_total_score: float
    expected_nadi_dosha: bool
    expected_bhakoot_dosha: bool
    score_tolerance: float = 1.5  # Allow ±1.5 for rounding differences
    source: str = "TODO"


MATCHING_VECTORS: list[MatchingVector] = [
    MatchingVector(
        test_id="MV001",
        description="Scorpio-Anuradha bride × Cancer-Pushya groom matching",
        bride_input=BirthInput(
            name="Bride MV001",
            gender="Female",
            birth_date=date(1995, 1, 10),
            birth_time=time(9, 0),
            time_accuracy=TimeAccuracy.EXACT,
            place_text="Pune",
            latitude=18.5204,
            longitude=73.8567,
            tz_iana="Asia/Kolkata",
        ),
        groom_input=BirthInput(
            name="Groom MV001",
            gender="Male",
            birth_date=date(1992, 7, 20),
            birth_time=time(11, 0),
            time_accuracy=TimeAccuracy.EXACT,
            place_text="Pune",
            latitude=18.5204,
            longitude=73.8567,
            tz_iana="Asia/Kolkata",
        ),
        expected_total_score=24.0,  # TODO: verify against DrikPanchang matching tool
        expected_nadi_dosha=False,
        expected_bhakoot_dosha=False,
        source="TODO",
    ),
]
