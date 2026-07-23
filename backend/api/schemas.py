"""
api/schemas.py
Pydantic v2 request/response models for the REST API.

These are the public shapes — they differ from engine/models.py (internal dataclasses).
The API layer explicitly controls which fields are exposed based on paid status.

Free-tier vs Paid-tier gating is done here:
  - KundaliFreeResponse: only free fields
  - KundaliPaidResponse: extends with premium fields
  - The GET /kundalis/:id endpoint returns one or the other based on DB paid=True flag
"""
from __future__ import annotations
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


# ---------------------------------------------------------------------------
# Shared primitives
# ---------------------------------------------------------------------------

class TimeAccuracy(str, Enum):
    EXACT = "exact"
    APPROXIMATE = "approximate"
    UNKNOWN = "unknown"


class RahuMode(str, Enum):
    TRUE_NODE = "true_node"
    MEAN_NODE = "mean_node"


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


# ---------------------------------------------------------------------------
# Geocoding
# ---------------------------------------------------------------------------

class PlaceCandidate(BaseModel):
    display_name: str
    latitude: float
    longitude: float
    tz_iana: str


class GeocodeResponse(BaseModel):
    places: List[PlaceCandidate]


# ---------------------------------------------------------------------------
# Kundali — Request
# ---------------------------------------------------------------------------

class KundaliCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    gender: Gender
    dob: date = Field(..., description="Date of birth (YYYY-MM-DD)")
    time_of_birth: Optional[str] = Field(
        None,
        description="Local birth time in HH:MM format. Null if unknown.",
        pattern=r"^\d{2}:\d{2}$",
    )
    time_accuracy: TimeAccuracy = TimeAccuracy.EXACT
    place_query: str = Field(..., min_length=2, max_length=200)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    tz_iana: str = Field(..., description="IANA timezone string, e.g. 'Asia/Kolkata'")
    rahu_mode: RahuMode = RahuMode.TRUE_NODE


# ---------------------------------------------------------------------------
# Kundali — Free-tier response (always returned)
# ---------------------------------------------------------------------------

class RashiInfo(BaseModel):
    value: int          # 0–11
    name_en: str        # "Scorpio"
    name_mr: str        # "वृश्चिक"


class NakshatraInfo(BaseModel):
    value: int          # 0–26
    name_en: str
    name_mr: str
    pada: int           # 1–4


class GanaInfo(BaseModel):
    value: str          # "Deva"
    name_mr: str        # "देव"


class NadiInfo(BaseModel):
    value: str          # "Madhya"
    name_mr: str        # "मध्य"


class VarnaInfo(BaseModel):
    value: str          # "Brahmin"
    name_mr: str        # "ब्राह्मण"


class LockedFields(BaseModel):
    """Which premium sections are locked for this kundali."""
    planet_positions: bool = True
    navamsa_chart: bool = True
    mangal_dosha: bool = True
    dasha: bool = True
    written_analysis: bool = True


class KundaliFreeResponse(BaseModel):
    id: UUID
    name: str
    gender: str
    dob: date
    time_of_birth: Optional[str]
    time_accuracy: TimeAccuracy
    place_text: str
    latitude: float
    longitude: float
    tz_iana: str
    lagna_reliable: bool

    # Free-tier fields
    rashi: Optional[RashiInfo]
    nakshatra: Optional[NakshatraInfo]
    lagna: Optional[RashiInfo]
    gana: Optional[GanaInfo]
    nadi: Optional[NadiInfo]
    varna: Optional[VarnaInfo]

    # Chart SVG (D1 only — free)
    chart_d1_svg: Optional[str]

    # Lock state
    paid: bool
    resume_token: str = ""
    locked: LockedFields

    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Kundali — Paid-tier additions
# ---------------------------------------------------------------------------

class PlanetPositionResponse(BaseModel):
    planet_en: str          # "Moon"
    planet_mr: str          # "चंद्र"
    rashi: RashiInfo
    degree_in_rashi: float  # 0–29.99
    dms: Optional[str] = None  # "04:46:28" (Degrees:Minutes:Seconds)
    house: int              # 1–12
    nakshatra: NakshatraInfo
    retrograde: bool
    is_exalted: bool
    is_debilitated: bool


class DashaResponse(BaseModel):
    mahadasha_lord_en: str
    mahadasha_lord_mr: str
    mahadasha_start: date
    mahadasha_end: date
    antardasha_lord_en: str
    antardasha_lord_mr: str
    antardasha_start: date
    antardasha_end: date


class MangalDoshaResponse(BaseModel):
    is_manglik: bool
    reference_point: str
    mars_house: Optional[int]
    cancellation_applied: bool
    cancellation_rule: Optional[str]
    explanation_mr: str
    explanation_en: str


class WrittenAnalysis(BaseModel):
    rashi_analysis_mr: str
    nakshatra_analysis_mr: str
    lagna_analysis_mr: str
    gana_analysis_mr: str
    nadi_analysis_mr: str
    dasha_analysis_mr: str
    yogas_detected_mr: str = ""   # Special yoga combinations (Rajayoga, Gajakesari etc)
    conclusion_mr: str = ""        # Final conclusion/निष्कर्ष paragraph


class KundaliPaidResponse(KundaliFreeResponse):
    """Extends free response with all paid fields unlocked."""
    planet_positions: List[PlanetPositionResponse]
    navamsa_chart_svg: Optional[str]
    moon_chart_svg: Optional[str] = None
    chalit_chart_svg: Optional[str] = None
    mangal_dosha: Optional[MangalDoshaResponse]
    dasha: Optional[DashaResponse]
    written_analysis: Optional[WrittenAnalysis]
    pdf_url: Optional[str]
    # New detailed fields
    avakahada: Optional["AvakahadadResponse"] = None
    mahadasha_table: List["MahadashaPeriod"] = []
    locked: LockedFields = LockedFields(
        planet_positions=False,
        navamsa_chart=False,
        mangal_dosha=False,
        dasha=False,
        written_analysis=False,
    )


class AvakahadadResponse(BaseModel):
    """Avakahada Chakra — 10 traditional Vedic attributes from Moon's nakshatra."""
    nakshatra_mr: str
    nakshatra_en: str
    nakshatra_pada: int
    rashi_mr: str
    rashi_en: str
    lagna_mr: str
    lagna_en: str
    karana_mr: str = ""
    karana_en: str = ""
    yoga_mr: str = ""
    yoga_en: str = ""
    tithi_mr: str = ""
    varna_mr: str = ""
    varna_en: str = ""
    vashya_mr: str = ""
    vashya_en: str = ""
    tatva_mr: str = ""
    tatva_en: str = ""
    varga_mr: str = ""
    varga_en: str = ""
    yunja_mr: str = ""
    yunja_en: str = ""
    gana_mr: str = ""
    gana_en: str = ""
    nadi_mr: str = ""
    nadi_en: str = ""
    yoni_mr: str = ""
    yoni_en: str = ""


class MahadashaPeriod(BaseModel):
    """One entry in the full Vimshottari Mahadasha table."""
    lord_en: str
    lord_mr: str
    start_date: date
    end_date: date
    years: int


# ---------------------------------------------------------------------------
# Matching — Request & Response
# ---------------------------------------------------------------------------

class PersonBirthDetails(BaseModel):
    """Inline birth details when no existing kundali_id is given."""
    name: str = Field(..., min_length=1, max_length=100)
    gender: Gender
    dob: date
    time_of_birth: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    time_accuracy: TimeAccuracy = TimeAccuracy.EXACT
    place_query: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    tz_iana: str


class MatchCreateRequest(BaseModel):
    # Either provide an existing kundali_id OR inline birth details
    bride_kundali_id: Optional[UUID] = None
    bride_details: Optional[PersonBirthDetails] = None
    groom_kundali_id: Optional[UUID] = None
    groom_details: Optional[PersonBirthDetails] = None

    def model_post_init(self, __context) -> None:
        if not self.bride_kundali_id and not self.bride_details:
            raise ValueError("Provide either bride_kundali_id or bride_details")
        if not self.groom_kundali_id and not self.groom_details:
            raise ValueError("Provide either groom_kundali_id or groom_details")


class KootaRowResponse(BaseModel):
    name_en: str
    name_mr: str
    points_earned: float
    points_max: int
    notes_mr: str
    notes_en: str
    interpretation_mr: Optional[str] = None
    interpretation_en: Optional[str] = None
    boy_trait: Optional[str] = None
    girl_trait: Optional[str] = None
    area_of_life_mr: Optional[str] = None


class DoshaCancellationResponse(BaseModel):
    dosha_name: str
    is_present: bool
    is_cancelled: bool
    cancellation_rule_mr: Optional[str]
    cancellation_rule_en: Optional[str]
    explanation_mr: str
    explanation_en: str


class MatchFreeResponse(BaseModel):
    id: UUID
    bride_name: str
    groom_name: str
    total_score: float
    total_max: int = 36
    bride_manglik: Optional[bool]   # yes/no only in free tier
    groom_manglik: Optional[bool]
    paid: bool
    locked: dict = {"koota_breakdown": True, "dosha_details": True, "verdict": True}
    created_at: datetime


class MatchPaidResponse(MatchFreeResponse):
    koota_breakdown: List[KootaRowResponse]
    nadi_dosha: DoshaCancellationResponse
    bhakoot_dosha: DoshaCancellationResponse
    mangal_compatibility: Optional[str]
    verdict_mr: str
    verdict_en: str
    pdf_url: Optional[str]
    locked: dict = {"koota_breakdown": False, "dosha_details": False, "verdict": False}


# ---------------------------------------------------------------------------
# Biodata — Request & Response
# ---------------------------------------------------------------------------

class BiodataCreateRequest(BaseModel):
    kundali_id: Optional[UUID] = None  # Optional link for auto-fill


class BiodataPersonalInfo(BaseModel):
    full_name: str
    dob: Optional[date] = None
    height_cm: Optional[int] = None
    blood_group: Optional[str] = None
    native_district: Optional[str] = None


class BiodataFamilyInfo(BaseModel):
    father_name: Optional[str] = None
    father_occupation: Optional[str] = None
    mother_name: Optional[str] = None
    mother_maiden_name: Optional[str] = None
    siblings: Optional[str] = None
    kul_daivat: Optional[str] = None  # Community-specific, optional
    gotra: Optional[str] = None


class BiodataEducationCareer(BaseModel):
    education: Optional[str] = None
    college: Optional[str] = None
    year_of_passing: Optional[int] = None
    occupation: Optional[str] = None
    employer: Optional[str] = None
    annual_income: Optional[str] = None  # String to allow "5-7 LPA" format


class BiodataHoroscopeInfo(BaseModel):
    rashi: Optional[str] = None
    nakshatra: Optional[str] = None
    gana: Optional[str] = None
    nadi: Optional[str] = None
    mangal_dosha: Optional[bool] = None
    # auto_filled: True if this came from a linked kundali
    auto_filled: bool = False


class BiodataUpdateRequest(BaseModel):
    personal_info: Optional[BiodataPersonalInfo] = None
    family_info: Optional[BiodataFamilyInfo] = None
    education_career: Optional[BiodataEducationCareer] = None
    horoscope_info: Optional[BiodataHoroscopeInfo] = None
    expectations: Optional[str] = None
    template_id: Optional[str] = None
    language: Optional[str] = "mr"


class BiodataResponse(BaseModel):
    id: UUID
    kundali_id: Optional[UUID]
    personal_info: Optional[BiodataPersonalInfo]
    family_info: Optional[BiodataFamilyInfo]
    education_career: Optional[BiodataEducationCareer]
    horoscope_info: Optional[BiodataHoroscopeInfo]
    expectations: Optional[str]
    photo_url: Optional[str]
    template_id: Optional[str]
    language: str
    pdf_url: Optional[str]
    created_at: datetime


# ---------------------------------------------------------------------------
# Orders / Payment
# ---------------------------------------------------------------------------

class ProductType(str, Enum):
    KUNDALI = "kundali"
    MATCHING = "matching"
    BIODATA = "biodata"
    BUNDLE = "bundle"


class OrderCreateRequest(BaseModel):
    product_type: ProductType
    related_kundali_id: Optional[UUID] = None
    related_match_id: Optional[UUID] = None
    related_biodata_id: Optional[UUID] = None


class OrderResponse(BaseModel):
    id: UUID
    product_type: ProductType
    amount: float
    currency: str = "INR"
    gateway_order_id: str
    razorpay_key_id: str    # Public key for frontend checkout
    status: str


class OrderStatusResponse(BaseModel):
    id: UUID
    status: str             # "created" | "paid" | "failed"
    paid: bool
    paid_at: Optional[datetime]
