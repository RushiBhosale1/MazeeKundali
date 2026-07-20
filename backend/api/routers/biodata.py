"""
api/routers/biodata.py
POST /api/v1/biodatas                          → create / start new biodata
PATCH /api/v1/biodatas/:id                     → incremental save per step
GET  /api/v1/biodatas/:id                      → fetch (with template)
POST /api/v1/biodatas/:id/link-kundali         → auto-fill horoscope from kundali
GET  /api/v1/biodatas/:id/resume/:token        → resume from saved link
"""
from __future__ import annotations
import logging
import uuid
from typing import Optional, Any

from fastapi import APIRouter, HTTPException, Path, Body, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from db import repository
from db.models import Biodata

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class BiodataCreateRequest(BaseModel):
    template_id: str = "traditional"  # traditional | modern | religious ...
    kundali_id: Optional[str] = None


class BiodataStepPatch(BaseModel):
    """PATCH — send whichever section changed. Others untouched."""
    personal_info: Optional[dict[str, Any]] = None
    family_info:   Optional[dict[str, Any]] = None
    education_info: Optional[dict[str, Any]] = None
    horoscope_info: Optional[dict[str, Any]] = None
    expectations: Optional[str] = None
    template_id: Optional[str] = None
    photo_url: Optional[str] = None


class LinkKundaliRequest(BaseModel):
    kundali_id: str


class BiodataResponse(BaseModel):
    id: str
    template_id: str
    personal_info: Optional[dict] = None
    family_info:   Optional[dict] = None
    education_info: Optional[dict] = None
    horoscope_info: Optional[dict] = None
    expectations: Optional[str] = None
    photo_url: Optional[str] = None
    paid: bool
    resume_token: str
    created_at: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/biodatas", status_code=201, response_model=BiodataResponse)
async def create_biodata(request: BiodataCreateRequest, db: AsyncSession = Depends(get_db)):
    """Start a new biodata. Returns ID + resume token for incremental saving."""
    
    k_id = uuid.UUID(request.kundali_id) if request.kundali_id else None
    
    biodata = await repository.create_biodata(
        db=db,
        template_id=request.template_id,
        kundali_id=k_id
    )

    # If kundali provided, pre-fill horoscope
    if k_id:
        horoscope_info = await _autofill_from_kundali_db(db, k_id)
        if horoscope_info:
            biodata = await repository.update_biodata(db, biodata.id, horoscope_info=horoscope_info)
            
    logger.info("Biodata created: id=%s template=%s", biodata.id, request.template_id)
    return _to_response(biodata)


@router.get("/biodatas/{biodata_id}", response_model=BiodataResponse)
async def get_biodata(biodata_id: uuid.UUID = Path(...), db: AsyncSession = Depends(get_db)):
    biodata = await repository.get_biodata(db, biodata_id)
    if not biodata:
        raise HTTPException(status_code=404, detail="बायोडाटा सापडला नाही.")
    return _to_response(biodata)


@router.patch("/biodatas/{biodata_id}", response_model=BiodataResponse)
async def patch_biodata(patch: BiodataStepPatch, biodata_id: uuid.UUID = Path(...), db: AsyncSession = Depends(get_db)):
    """Incremental save — each form step calls this."""
    biodata = await repository.get_biodata(db, biodata_id)
    if not biodata:
        raise HTTPException(status_code=404, detail="बायोडाटा सापडला नाही.")

    update_kwargs = {}
    if patch.personal_info  is not None: update_kwargs["personal_info"]  = patch.personal_info
    if patch.family_info    is not None: update_kwargs["family_info"]    = patch.family_info
    if patch.education_info is not None: update_kwargs["education_info"] = patch.education_info
    if patch.horoscope_info is not None: update_kwargs["horoscope_info"] = patch.horoscope_info
    if patch.expectations   is not None: update_kwargs["expectations"]   = patch.expectations
    if patch.template_id    is not None: update_kwargs["template_id"]    = patch.template_id
    if patch.photo_url      is not None: update_kwargs["photo_url"]      = patch.photo_url

    if update_kwargs:
        biodata = await repository.update_biodata(db, biodata_id, **update_kwargs)
        
    return _to_response(biodata)


@router.post("/biodatas/{biodata_id}/link-kundali")
async def link_kundali(body: LinkKundaliRequest, biodata_id: uuid.UUID = Path(...), db: AsyncSession = Depends(get_db)):
    """Auto-fill horoscope_info from a linked kundali."""
    biodata = await repository.get_biodata(db, biodata_id)
    if not biodata:
        raise HTTPException(status_code=404, detail="बायोडाटा सापडला नाही.")

    try:
        k_id = uuid.UUID(body.kundali_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="चुकीचा कुंडली ID.")

    kundali = await repository.get_kundali(db, k_id)
    if not kundali:
        raise HTTPException(status_code=404, detail="कुंडली सापडली नाही. ID तपासा.")

    paid = kundali.paid
    horoscope = _extract_horoscope(kundali.chart_data, paid_only=not paid)

    # If the linked kundali is paid, the biodata becomes fully unlocked for free!
    if paid:
        await repository.update_biodata(db, biodata_id, horoscope_info=horoscope, kundali_id=k_id, paid=True)
    else:
        await repository.update_biodata(db, biodata_id, horoscope_info=horoscope, kundali_id=k_id)

    return {
        "status": "linked",
        "horoscope_info": horoscope,
        "from_paid_kundali": paid,
        "note_mr": "कुंडलीमधून माहिती भरली गेली." if paid else "फक्त मोफत माहिती भरली गेली. संपूर्ण माहितीसाठी कुंडली अनलॉक करा.",
    }


@router.get("/biodatas/{biodata_id}/resume/{token}")
async def resume_biodata(biodata_id: uuid.UUID, token: str, db: AsyncSession = Depends(get_db)):
    """Resume biodata from a saved link."""
    biodata = await repository.get_biodata_by_token(db, biodata_id, token)
    if not biodata:
        raise HTTPException(status_code=403, detail="अवैध लिंक किंवा बायोडाटा सापडला नाही.")
    return _to_response(biodata)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _to_response(record: Biodata) -> BiodataResponse:
    return BiodataResponse(
        id=str(record.id),
        template_id=record.template_id,
        personal_info=record.personal_info,
        family_info=record.family_info,
        education_info=record.education_info,
        horoscope_info=record.horoscope_info,
        expectations=record.expectations,
        photo_url=record.photo_url,
        paid=record.paid,
        resume_token=record.resume_token,
        created_at=str(record.created_at),
    )


async def _autofill_from_kundali_db(db: AsyncSession, kundali_id: uuid.UUID) -> Optional[dict]:
    """Look up kundali in DB and extract horoscope fields."""
    try:
        kundali = await repository.get_kundali(db, kundali_id)
        if not kundali or not kundali.chart_data:
            return None
        return _extract_horoscope(kundali.chart_data, paid_only=not kundali.paid)
    except Exception:
        return None


def _extract_horoscope(chart_data: dict, paid_only: bool) -> dict:
    """Extract horoscope fields from kundali chart_data dictionary."""
    if not chart_data:
        return {}

    info: dict = {
        "rashi_en": chart_data.get("rashi"),
        "rashi_mr": chart_data.get("rashi_mr"),
        "nakshatra_en": chart_data.get("nakshatra"),
        "nakshatra_mr": chart_data.get("nakshatra_mr"),
        "pada": chart_data.get("pada"),
        "gana_mr": chart_data.get("gana_mr") or chart_data.get("gana"),
        "nadi_mr": chart_data.get("nadi_mr") or chart_data.get("nadi"),
        "varna_mr": chart_data.get("varna_mr") or chart_data.get("varna"),
    }

    # Paid-only fields
    if not paid_only:
        mangal = chart_data.get("mangal_dosha")
        if mangal:
            info["mangal_dosha"] = mangal.get("status", False)
            info["mangal_dosha_explanation_mr"] = mangal.get("explanation_mr")
            
        info["lagna_en"] = chart_data.get("lagna")
        info["lagna_mr"] = chart_data.get("lagna_mr")

    return info
