"""
api/routers/matching.py
POST /api/v1/matchings           → compute Ashtakoot, return free-tier (score only)
GET  /api/v1/matchings/:id       → fetch (locked detail if not paid)
POST /engine/match               → internal pure engine (no DB)

Free tier: total score, manglik status
Paid tier: 8-koota breakdown, dosha analysis, Marathi verdict, PDF
"""
from __future__ import annotations
import logging
import uuid
from datetime import date, time as dtime
from typing import Optional

from fastapi import APIRouter, HTTPException, Path, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import TimeAccuracy as TimeAccuracyEnum, Gender as GenderEnum, RahuMode as RahuModeEnum
from db.session import get_db
from db import repository as repo
from engine.chart import compute_kundali
from engine.matching import compute_match as compute_ashtakoot
from engine.models import TimeAccuracy, RahuMode

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class PersonInput(BaseModel):
    name: str
    gender: GenderEnum
    dob: date
    time_of_birth: Optional[str] = None   # HH:MM
    time_accuracy: TimeAccuracyEnum = TimeAccuracyEnum.EXACT
    place_query: str
    latitude: float
    longitude: float
    tz_iana: str
    rahu_mode: RahuModeEnum = RahuModeEnum.TRUE_NODE
    # Optional: use existing kundali
    kundali_id: Optional[str] = None


class MatchingCreateRequest(BaseModel):
    bride: PersonInput
    groom: PersonInput


class KootaRowOut(BaseModel):
    name_en: str
    name_mr: str
    points_earned: float
    points_max: int
    notes_mr: str
    notes_en: str


class DoshaOut(BaseModel):
    dosha_name: str
    is_present: bool
    is_cancelled: bool
    cancellation_rule_mr: Optional[str]
    explanation_mr: str
    explanation_en: str


class MatchingFreeResponse(BaseModel):
    id: str
    bride_name: str
    groom_name: str
    total_score: float
    total_max: float
    bride_manglik: Optional[bool]
    groom_manglik: Optional[bool]
    bride_manglik_severity: Optional[str] = None
    groom_manglik_severity: Optional[str] = None
    paid: bool
    resume_token: str
    created_at: str
    locked: dict


class MatchingPaidResponse(MatchingFreeResponse):
    koota_breakdown: list[KootaRowOut]
    nadi_dosha: Optional[DoshaOut]
    bhakoot_dosha: Optional[DoshaOut]
    verdict_mr: str
    verdict_en: str
    pdf_url: Optional[str]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_time(s: Optional[str]) -> Optional[dtime]:
    if not s:
        return None
    try:
        h, m = s.split(":")
        return dtime(int(h), int(m))
    except (ValueError, AttributeError):
        return None


def _compute_person(person: PersonInput):
    """Compute kundali for one person (free + paid fields for matching)."""
    birth_time = _parse_time(person.time_of_birth)
    return compute_kundali(
        name=person.name,
        gender=person.gender.value,
        birth_date=person.dob,
        birth_time=birth_time,
        time_accuracy=TimeAccuracy(person.time_accuracy.value),
        place_text=person.place_query,
        latitude=person.latitude,
        longitude=person.longitude,
        tz_iana=person.tz_iana,
        rahu_mode=RahuMode(person.rahu_mode.value),
        compute_paid_fields=True,   # matching always needs paid fields
    )


def _build_free_response(matching_id: uuid.UUID, request: MatchingCreateRequest,
                          score: int, bride_manglik, groom_manglik,
                          resume_token: str, created_at) -> MatchingFreeResponse:
    return MatchingFreeResponse(
        id=str(matching_id),
        bride_name=request.bride.name,
        groom_name=request.groom.name,
        total_score=score,
        total_max=36,
        bride_manglik=bride_manglik,
        groom_manglik=groom_manglik,
        paid=False,
        resume_token=resume_token,
        created_at=str(created_at),
        locked={
            "koota_breakdown": True,
            "dosha_analysis": True,
            "verdict": True,
            "pdf": True,
        },
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("/matchings", status_code=201)
async def create_matching(request: MatchingCreateRequest, db: AsyncSession = Depends(get_db)):
    """
    Compute Ashtakoot matching for bride + groom.
    Returns free tier: total score + manglik status.
    Koota breakdown and verdict require payment.
    """
    try:
        bride_result = _compute_person(request.bride)
        groom_result = _compute_person(request.groom)
    except Exception as e:
        logger.exception("Kundali computation failed during matching: %s", e)
        raise HTTPException(
            status_code=500,
            detail="गणना मध्ये समस्या आली. कृपया पुन्हा प्रयत्न करा."
        )

    # Run Ashtakoot
    try:
        match_result = compute_ashtakoot(bride_result, groom_result)
    except Exception as e:
        logger.exception("Ashtakoot matching failed: %s", e)
        raise HTTPException(status_code=500, detail="जुळणी गणना अपयशी. पुन्हा प्रयत्न करा.")

    # Save to database
    bride_profile = await repo.create_birth_profile(db, bride_result, gender=request.bride.gender.value, rahu_mode=request.bride.rahu_mode.value)
    groom_profile = await repo.create_birth_profile(db, groom_result, gender=request.groom.gender.value, rahu_mode=request.groom.rahu_mode.value)

    koota_breakdown = [
        {
            "name_en": k.name_en,
            "name_mr": k.name_mr,
            "points_earned": k.points_earned,
            "points_max": k.points_max,
            "notes_mr": k.notes_mr,
            "notes_en": k.notes_en,
        }
        for k in match_result.kootas
    ]
    
    dosha_analysis = {
        "nadi_dosha": {
            "dosha_name": match_result.nadi_dosha.dosha_name,
            "is_present": match_result.nadi_dosha.is_present,
            "is_cancelled": match_result.nadi_dosha.is_cancelled,
            "cancellation_rule_mr": match_result.nadi_dosha.cancellation_rule_mr,
            "explanation_mr": match_result.nadi_dosha.explanation_mr,
            "explanation_en": match_result.nadi_dosha.explanation_en,
        } if match_result.nadi_dosha else None,
        "bhakoot_dosha": {
            "dosha_name": match_result.bhakoot_dosha.dosha_name,
            "is_present": match_result.bhakoot_dosha.is_present,
            "is_cancelled": match_result.bhakoot_dosha.is_cancelled,
            "cancellation_rule_mr": match_result.bhakoot_dosha.cancellation_rule_mr,
            "explanation_mr": match_result.bhakoot_dosha.explanation_mr,
            "explanation_en": match_result.bhakoot_dosha.explanation_en,
        } if match_result.bhakoot_dosha else None,
    }

    bride_manglik = bride_result.mangal_dosha.is_manglik if bride_result.mangal_dosha else None
    groom_manglik = groom_result.mangal_dosha.is_manglik if groom_result.mangal_dosha else None
    
    bride_manglik_sev = bride_result.mangal_dosha.severity if bride_result.mangal_dosha else None
    groom_manglik_sev = groom_result.mangal_dosha.severity if groom_result.mangal_dosha else None

    # Call AI or basic logic for verdicts - we can just stub it for now
    verdict_mr = "एकूण गुण: " + str(match_result.total_score) + "/३६"
    verdict_en = "Total Score: " + str(match_result.total_score) + "/36"

    matching_db = await repo.create_matching(
        db=db,
        total_score=match_result.total_score,
        bride_manglik=bride_manglik,
        groom_manglik=groom_manglik,
        bride_manglik_severity=bride_manglik_sev,
        groom_manglik_severity=groom_manglik_sev,
        koota_breakdown=koota_breakdown,
        dosha_analysis=dosha_analysis,
        verdict_mr=verdict_mr,
        verdict_en=verdict_en,
        bride_profile_id=bride_profile.id,
        groom_profile_id=groom_profile.id,
    )

    return MatchingFreeResponse(
        id=str(matching_db.id),
        bride_name=request.bride.name,
        groom_name=request.groom.name,
        total_score=match_result.total_score,
        total_max=36,
        bride_manglik=bride_manglik,
        groom_manglik=groom_manglik,
        bride_manglik_severity=bride_manglik_sev,
        groom_manglik_severity=groom_manglik_sev,
        paid=False,
        resume_token=matching_db.resume_token,
        created_at=str(matching_db.created_at),
        locked={
            "koota_breakdown": True,
            "dosha_analysis": True,
            "verdict": True,
            "pdf": True,
        },
    )



@router.get("/matchings/{matching_id}")
async def get_matching(matching_id: str = Path(...), db: AsyncSession = Depends(get_db)):
    """
    Fetch matching result.
    If paid: return full koota breakdown + dosha + verdict.
    If not paid: return score only with locked flags.
    """
    try:
        mid = uuid.UUID(matching_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid matching ID")

    record = await repo.get_matching(db, mid)
    if not record:
        raise HTTPException(status_code=404, detail="जुळणी सापडली नाही.")

    bride_name = record.bride_birth_profile.name if record.bride_birth_profile else (record.bride_kundali.birth_profile.name if record.bride_kundali else "वधू")
    groom_name = record.groom_birth_profile.name if record.groom_birth_profile else (record.groom_kundali.birth_profile.name if record.groom_kundali else "वर")

    if record.paid:
        koota_rows = []
        if record.koota_breakdown:
            koota_rows = [
                KootaRowOut(
                    name_en=k["name_en"],
                    name_mr=k["name_mr"],
                    points_earned=k["points_earned"],
                    points_max=k["points_max"],
                    notes_mr=k["notes_mr"],
                    notes_en=k["notes_en"],
                )
                for k in record.koota_breakdown
            ]

        nadi_dosha = None
        bhakoot_dosha = None
        if record.dosha_analysis:
            n = record.dosha_analysis.get("nadi_dosha")
            if n:
                nadi_dosha = DoshaOut(
                    dosha_name=n["dosha_name"],
                    is_present=n["is_present"],
                    is_cancelled=n["is_cancelled"],
                    cancellation_rule_mr=n.get("cancellation_rule_mr"),
                    explanation_mr=n["explanation_mr"],
                    explanation_en=n["explanation_en"]
                )
            b = record.dosha_analysis.get("bhakoot_dosha")
            if b:
                bhakoot_dosha = DoshaOut(
                    dosha_name=b["dosha_name"],
                    is_present=b["is_present"],
                    is_cancelled=b["is_cancelled"],
                    cancellation_rule_mr=b.get("cancellation_rule_mr"),
                    explanation_mr=b["explanation_mr"],
                    explanation_en=b["explanation_en"]
                )

        return MatchingPaidResponse(
            id=str(record.id),
            bride_name=bride_name,
            groom_name=groom_name,
            total_score=record.total_score,
            total_max=36,
            bride_manglik=record.bride_manglik,
            groom_manglik=record.groom_manglik,
            bride_manglik_severity=record.bride_manglik_severity,
            groom_manglik_severity=record.groom_manglik_severity,
            paid=True,
            resume_token=record.resume_token,
            created_at=str(record.created_at),
            locked={
                "koota_breakdown": False,
                "dosha_analysis": False,
                "verdict": False,
                "pdf": False,
            },
            koota_breakdown=koota_rows,
            nadi_dosha=nadi_dosha,
            bhakoot_dosha=bhakoot_dosha,
            verdict_mr=record.verdict_mr or "",
            verdict_en=record.verdict_en or "",
            pdf_url=record.pdf_url,
        )
    else:
        return MatchingFreeResponse(
            id=str(record.id),
            bride_name=bride_name,
            groom_name=groom_name,
            total_score=record.total_score,
            total_max=36,
            bride_manglik=record.bride_manglik,
            groom_manglik=record.groom_manglik,
            bride_manglik_severity=record.bride_manglik_severity,
            groom_manglik_severity=record.groom_manglik_severity,
            paid=False,
            resume_token=record.resume_token,
            created_at=str(record.created_at),
            locked={
                "koota_breakdown": True,
                "dosha_analysis": True,
                "verdict": True,
                "pdf": True,
            },
        )


# ── Internal("/engine/match")
async def engine_match_endpoint(request: MatchingCreateRequest):
    """
    Internal pure engine endpoint — no DB storage.
    Returns full koota breakdown + verdict immediately.
    """
    bride_result = _compute_person(request.bride)
    groom_result = _compute_person(request.groom)
    match_result = compute_ashtakoot(bride_result, groom_result)

    return {
        "total_score": match_result.total_score,
        "total_max": 36,
        "verdict_mr": match_result.verdict_mr,
        "verdict_en": match_result.verdict_en,
        "koota_breakdown": [
            {
                "name_en": k.name_en,
                "name_mr": k.name_mr,
                "earned": k.points_earned,
                "max": k.points_max,
                "notes_mr": k.notes_mr,
            }
            for k in match_result.kootas
        ],
        "nadi_dosha": {
            "is_present": match_result.nadi_dosha.is_present,
            "is_cancelled": match_result.nadi_dosha.is_cancelled,
            "explanation_mr": match_result.nadi_dosha.explanation_mr,
        } if match_result.nadi_dosha else None,
        "bride_manglik": bride_result.mangal_dosha.is_manglik if bride_result.mangal_dosha else None,
        "groom_manglik": groom_result.mangal_dosha.is_manglik if groom_result.mangal_dosha else None,
    }
