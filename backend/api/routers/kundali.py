"""
api/routers/kundali.py
POST /api/v1/kundalis        — create & compute kundali (free tier)
GET  /api/v1/kundalis/:id    — fetch (returns locked fields if not paid)
POST /engine/kundali         — internal pure engine endpoint (no DB)

For Phase 0/1: uses in-memory store (dict) as a simple stand-in for the DB.
Phase 1 will replace this with a real PostgreSQL-backed repo.
This lets us fully test and demo the engine without setting up DB first.
"""
from __future__ import annotations
import logging
import uuid
import secrets
from datetime import datetime, time as dtime
from typing import Optional

from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

from api.schemas import (
    KundaliCreateRequest, KundaliFreeResponse, KundaliPaidResponse,
    RashiInfo, NakshatraInfo, GanaInfo, NadiInfo, VarnaInfo, LockedFields,
    PlanetPositionResponse, DashaResponse, MangalDoshaResponse, WrittenAnalysis,
)
from db.session import get_db
from db import repository as repo
from engine.chart import compute_kundali
from engine.models import TimeAccuracy, RahuMode, KundaliResult
from engine.templates import generate_written_analysis

logger = logging.getLogger(__name__)
router = APIRouter()

# Legacy in-memory store — kept for engine/kundali endpoint only
_store: dict[str, dict] = {}


def _parse_time(time_str: Optional[str]) -> Optional[dtime]:
    """Parse 'HH:MM' string to time object."""
    if not time_str:
        return None
    try:
        h, m = time_str.split(":")
        return dtime(int(h), int(m))
    except (ValueError, AttributeError):
        return None


def _rashi_info(rashi) -> Optional[RashiInfo]:
    if rashi is None:
        return None
    return RashiInfo(value=rashi.value, name_en=rashi.name_en, name_mr=rashi.name_mr)


def _nakshatra_info(nakshatra, pada) -> Optional[NakshatraInfo]:
    if nakshatra is None:
        return None
    return NakshatraInfo(
        value=nakshatra.value,
        name_en=nakshatra.name_en,
        name_mr=nakshatra.name_mr,
        pada=pada or 1,
    )


def _build_free_response(record: dict, result: KundaliResult) -> KundaliFreeResponse:
    paid = record.get("paid", False)
    chart_svg = record.get("chart_d1_svg")
    if paid and result.lagna is not None and result.planet_positions:
        try:
            from engine.svg_chart import render_north_indian_svg
            pr = {pp.planet.value: pp.rashi.value for pp in result.planet_positions}
            rr = {pp.planet.value for pp in result.planet_positions if pp.retrograde}
            chart_svg = render_north_indian_svg(
                lagna_rashi=result.lagna.value,
                planet_rashis=pr,
                retrogrades=rr,
                width=360,
                lang="mr",
            )
        except Exception as svg_err:
            logger.warning("Dynamic SVG generation with planets failed: %s", svg_err)

    return KundaliFreeResponse(
        id=record["id"],
        name=result.name,
        gender=result.gender,
        dob=result.dob,
        time_of_birth=result.time_of_birth,
        time_accuracy=result.time_accuracy,
        place_text=result.place_text,
        latitude=result.latitude,
        longitude=result.longitude,
        tz_iana=result.tz_iana,
        lagna_reliable=result.lagna_reliable,
        rashi=_rashi_info(result.rashi),
        nakshatra=_nakshatra_info(result.nakshatra, result.pada),
        lagna=_rashi_info(result.lagna),
        gana=GanaInfo(value=result.gana.value, name_mr=result.gana.name_mr) if result.gana else None,
        nadi=NadiInfo(value=result.nadi.value, name_mr=result.nadi.name_mr) if result.nadi else None,
        varna=VarnaInfo(value=result.varna.value, name_mr=result.varna.name_mr) if result.varna else None,
        chart_d1_svg=chart_svg,
        paid=paid,
        resume_token=record.get("resume_token", ""),
        locked=LockedFields(
            planet_positions=not paid,
            navamsa_chart=not paid,
            mangal_dosha=not paid,
            dasha=not paid,
            written_analysis=not paid,
        ),
        created_at=record["created_at"],
    )


def _build_paid_response(record: dict, result: KundaliResult) -> KundaliPaidResponse:
    free = _build_free_response(record, result)

    # Planet positions
    planet_positions = []
    for pp in result.planet_positions:
        planet_positions.append(PlanetPositionResponse(
            planet_en=pp.planet.value,
            planet_mr=pp.planet.name_mr,
            rashi=_rashi_info(pp.rashi),
            degree_in_rashi=round(pp.degree_in_rashi, 2),
            house=pp.house,
            nakshatra=_nakshatra_info(pp.nakshatra, pp.pada),
            retrograde=pp.retrograde,
            is_exalted=pp.is_exalted,
            is_debilitated=pp.is_debilitated,
        ))

    # Dasha
    dasha_resp = None
    if result.dasha:
        d = result.dasha
        dasha_resp = DashaResponse(
            mahadasha_lord_en=d.mahadasha_lord.value,
            mahadasha_lord_mr=d.mahadasha_lord.name_mr,
            mahadasha_start=d.mahadasha_start,
            mahadasha_end=d.mahadasha_end,
            antardasha_lord_en=d.antardasha_lord.value,
            antardasha_lord_mr=d.antardasha_lord.name_mr,
            antardasha_start=d.antardasha_start,
            antardasha_end=d.antardasha_end,
        )

    # Mangal Dosha
    mangal_resp = None
    if result.mangal_dosha:
        md = result.mangal_dosha
        mangal_resp = MangalDoshaResponse(
            is_manglik=md.is_manglik,
            reference_point=md.reference_point,
            mars_house=md.mars_house,
            cancellation_applied=md.cancellation_applied,
            cancellation_rule=md.cancellation_rule,
            explanation_mr=md.explanation_mr,
            explanation_en=md.explanation_en,
        )

    # Written analysis (templated)
    analysis = generate_written_analysis(result) if result.planet_positions else None

    # Navamsa chart SVG (D9) — computed from planet positions
    navamsa_chart_svg: Optional[str] = None
    if result.lagna is not None and result.planet_positions:
        try:
            from engine.svg_chart import render_north_indian_svg
            from engine.ephemeris import longitude_to_navamsa_rashi as _nav_rashi
            pr_d9: dict[str, int] = {}
            rr_d9: set[str] = set()
            for pp in result.planet_positions:
                pr_d9[pp.planet.value] = _nav_rashi(pp.longitude).value
                if pp.retrograde:
                    rr_d9.add(pp.planet.value)
            # Navamsa Lagna — from raw ephemeris if available
            raw = getattr(result, '_raw_ephemeris', None)
            nav_lagna_rashi = None
            if raw:
                nav_lagna_rashi = _nav_rashi(raw['lagna_longitude']).value
            elif result.lagna is not None:
                # Fall back: use lagna longitude approximation
                nav_lagna_rashi = result.lagna.value
            if nav_lagna_rashi is not None:
                navamsa_chart_svg = render_north_indian_svg(
                    lagna_rashi=nav_lagna_rashi,
                    planet_rashis=pr_d9,
                    retrogrades=rr_d9,
                    width=360,
                    lang="mr",
                )
        except Exception as nav_err:
            logger.warning("Navamsa SVG generation failed: %s", nav_err)

    # Chandra (Moon) chart SVG — Moon's rashi as Lagna
    moon_chart_svg: Optional[str] = None
    if result.rashi is not None and result.planet_positions:
        try:
            from engine.svg_chart import render_north_indian_svg
            pr_d1 = {pp.planet.value: pp.rashi.value for pp in result.planet_positions}
            rr_d1 = {pp.planet.value for pp in result.planet_positions if pp.retrograde}
            moon_chart_svg = render_north_indian_svg(
                lagna_rashi=result.rashi.value,
                planet_rashis=pr_d1,
                retrogrades=rr_d1,
                width=360,
                lang="mr",
            )
        except Exception as moon_err:
            logger.warning("Moon SVG generation failed: %s", moon_err)

    return KundaliPaidResponse(
        **free.model_dump(),
        planet_positions=planet_positions,
        navamsa_chart_svg=navamsa_chart_svg,
        moon_chart_svg=moon_chart_svg,
        mangal_dosha=mangal_resp,
        dasha=dasha_resp,
        written_analysis=analysis,
        pdf_url=record.get("pdf_url"),
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/kundalis", response_model=KundaliFreeResponse, status_code=201)
async def create_kundali(
    request: KundaliCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Create and compute a new kundali from birth data.
    Saves to DB. Returns computed kundali fields.
    """
    birth_time = _parse_time(request.time_of_birth)
    time_accuracy = TimeAccuracy(request.time_accuracy.value)
    rahu_mode = RahuMode(request.rahu_mode.value)

    try:
        result = compute_kundali(
            name=request.name,
            gender=request.gender.value,
            birth_date=request.dob,
            birth_time=birth_time,
            time_accuracy=time_accuracy,
            place_text=request.place_query,
            latitude=request.latitude,
            longitude=request.longitude,
            tz_iana=request.tz_iana,
            rahu_mode=rahu_mode,
            compute_paid_fields=True,
        )
    except Exception as e:
        logger.exception("Kundali computation failed: %s", e)
        raise HTTPException(
            status_code=500,
            detail="कुंडली गणना मध्ये समस्या आली. कृपया पुन्हा प्रयत्न करा."
        )

    # Generate North Indian SVG chart
    chart_svg: Optional[str] = None
    if result.lagna is not None:
        try:
            from engine.svg_chart import render_north_indian_svg
            pr = {pp.planet.value: pp.rashi.value for pp in result.planet_positions} if result.planet_positions else {}
            rr = {pp.planet.value for pp in result.planet_positions if pp.retrograde} if result.planet_positions else set()
            chart_svg = render_north_indian_svg(
                lagna_rashi=result.lagna.value,
                planet_rashis=pr,
                retrogrades=rr,
                width=360,
                lang="mr",
            )
        except Exception as svg_err:
            logger.warning("SVG generation failed: %s", svg_err)

    # Save to DB
    birth_profile = await repo.create_birth_profile(db, result, request.gender.value, request.rahu_mode.value)
    kundali_db = await repo.create_kundali(db, birth_profile, result, chart_svg=chart_svg)

    logger.info("Kundali created: id=%s name=%s rashi=%s", kundali_db.id, request.name, result.rashi)

    return KundaliFreeResponse(
        id=kundali_db.id,
        name=result.name,
        gender=result.gender,
        dob=result.dob,
        time_of_birth=result.time_of_birth,
        time_accuracy=result.time_accuracy,
        place_text=result.place_text,
        latitude=result.latitude,
        longitude=result.longitude,
        tz_iana=result.tz_iana,
        lagna_reliable=result.lagna_reliable,
        rashi=_rashi_info(result.rashi),
        nakshatra=_nakshatra_info(result.nakshatra, result.pada),
        lagna=_rashi_info(result.lagna),
        gana=GanaInfo(value=result.gana.value, name_mr=result.gana.name_mr) if result.gana else None,
        nadi=NadiInfo(value=result.nadi.value, name_mr=result.nadi.name_mr) if result.nadi else None,
        varna=VarnaInfo(value=result.varna.value, name_mr=result.varna.name_mr) if result.varna else None,
        chart_d1_svg=chart_svg,
        paid=False,
        resume_token=kundali_db.resume_token,
        locked=LockedFields(
            planet_positions=True, navamsa_chart=True,
            mangal_dosha=True, dasha=True, written_analysis=True,
        ),
        created_at=kundali_db.created_at,
    )


@router.get("/kundalis/{kundali_id}")  # No response_model — returns Union[Free, Paid]
async def get_kundali(
    kundali_id: str = Path(..., description="Kundali UUID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch a kundali by ID from DB.
    Returns free-tier fields always; all fields if paid=True.
    """
    try:
        kid = uuid.UUID(kundali_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid kundali ID.")

    kundali_db = await repo.get_kundali(db, kid)
    if not kundali_db:
        raise HTTPException(status_code=404, detail="कुंडली सापडली नाही.")

    profile = kundali_db.birth_profile
    if not profile:
        raise HTTPException(status_code=404, detail="कुंडली प्रोफाइल सापडली नाही.")

    paid = kundali_db.paid

    # Re-compute engine result (always; free fields are fast)
    birth_time = _parse_time(str(profile.time_of_birth)[:5] if profile.time_of_birth else None)
    result = compute_kundali(
        name=profile.name,
        gender=profile.gender,
        birth_date=profile.dob,
        birth_time=birth_time,
        time_accuracy=TimeAccuracy(profile.time_accuracy),
        place_text=profile.place_text,
        latitude=profile.latitude,
        longitude=profile.longitude,
        tz_iana=profile.tz_iana,
        rahu_mode=RahuMode(profile.rahu_mode),
        compute_paid_fields=paid,
    )

    # Build base free response
    free = KundaliFreeResponse(
        id=kundali_db.id,
        name=result.name,
        gender=result.gender,
        dob=result.dob,
        time_of_birth=result.time_of_birth,
        time_accuracy=result.time_accuracy,
        place_text=result.place_text,
        latitude=result.latitude,
        longitude=result.longitude,
        tz_iana=result.tz_iana,
        lagna_reliable=result.lagna_reliable,
        rashi=_rashi_info(result.rashi),
        nakshatra=_nakshatra_info(result.nakshatra, result.pada),
        lagna=_rashi_info(result.lagna),
        gana=GanaInfo(value=result.gana.value, name_mr=result.gana.name_mr) if result.gana else None,
        nadi=NadiInfo(value=result.nadi.value, name_mr=result.nadi.name_mr) if result.nadi else None,
        varna=VarnaInfo(value=result.varna.value, name_mr=result.varna.name_mr) if result.varna else None,
        chart_d1_svg=kundali_db.chart_d1_svg,
        paid=paid,
        resume_token=kundali_db.resume_token or "",
        locked=LockedFields(
            planet_positions=not paid, navamsa_chart=not paid,
            mangal_dosha=not paid, dasha=not paid, written_analysis=not paid,
        ),
        created_at=kundali_db.created_at,
    )

    if not paid:
        return free

    # Paid response — use pre-stored paid data from DB + re-computed result
    record = {
        "id": kundali_db.id,
        "result": result,
        "paid": True,
        "resume_token": kundali_db.resume_token or "",
        "chart_d1_svg": kundali_db.chart_d1_svg,
        "pdf_url": kundali_db.pdf_url,
        "created_at": kundali_db.created_at,
    }
    return _build_paid_response(record, result)


# ---------------------------------------------------------------------------
# Internal engine endpoint — full compute (no DB, no paywall)
# Used by Manglik checker, admin validation, chart preview
# ---------------------------------------------------------------------------

@router.post("/engine/kundali")
async def engine_kundali_endpoint(request: KundaliCreateRequest):
    """
    Pure engine endpoint — no DB, no payment gate.
    Returns FULL paid-tier data: all 9 planet positions, dasha, mangal_dosha.
    Used by: Manglik checker standalone page, chart SVG preview, admin tests.
    Production: restrict to internal network / add API key header.
    """
    birth_time = _parse_time(request.time_of_birth)

    try:
        result: KundaliResult = compute_kundali(
            name=request.name,
            gender=request.gender.value,
            birth_date=request.dob,
            birth_time=birth_time,
            time_accuracy=TimeAccuracy(request.time_accuracy.value),
            place_text=request.place_query,
            latitude=request.latitude,
            longitude=request.longitude,
            tz_iana=request.tz_iana,
            rahu_mode=RahuMode(request.rahu_mode.value if request.rahu_mode else "true_node"),
            compute_paid_fields=True,
        )
    except Exception as e:
        logger.exception("Engine compute failed: %s", e)
        raise HTTPException(status_code=500, detail="गणना अयशस्वी झाली. पुन्हा प्रयत्न करा.")

    md = result.mangal_dosha
    dasha = result.dasha

    return {
        "rashi": result.rashi.name_en if result.rashi is not None else None,
        "rashi_mr": result.rashi.name_mr if result.rashi is not None else None,
        "nakshatra": result.nakshatra.name_en if result.nakshatra is not None else None,
        "nakshatra_mr": result.nakshatra.name_mr if result.nakshatra is not None else None,
        "pada": result.pada,
        "lagna": result.lagna.name_en if result.lagna is not None else None,
        "lagna_reliable": result.lagna_reliable,
        "gana": result.gana.value if result.gana is not None else None,
        "nadi": result.nadi.value if result.nadi is not None else None,
        "varna": result.varna.value if result.varna is not None else None,
        "mangal_dosha": {
            "is_manglik": md.is_manglik,
            "reference_point": md.reference_point,
            "mars_house": md.mars_house,
            "cancellation_applied": md.cancellation_applied,
            "cancellation_rule": md.cancellation_rule,
            "explanation_mr": md.explanation_mr,
            "explanation_en": md.explanation_en,
        } if md else None,
        "dasha": {
            "mahadasha": dasha.mahadasha_lord.value if dasha else None,
            "mahadasha_mr": dasha.mahadasha_lord.name_mr if dasha else None,
            "antardasha": dasha.antardasha_lord.value if dasha else None,
            "antardasha_mr": dasha.antardasha_lord.name_mr if dasha else None,
            "mahadasha_start": str(dasha.mahadasha_start) if dasha else None,
            "mahadasha_end": str(dasha.mahadasha_end) if dasha else None,
        } if dasha else None,
        "planet_positions": [
            {
                "planet_en": pp.planet.value,
                "planet_mr": pp.planet.name_mr,
                "rashi": {
                    "value": pp.rashi.value,
                    "name_en": pp.rashi.name_en,
                    "name_mr": pp.rashi.name_mr,
                },
                "degree_in_rashi": round(pp.degree_in_rashi, 4),
                "house": pp.house,
                "retrograde": pp.retrograde,
                "is_exalted": pp.is_exalted,
                "is_debilitated": pp.is_debilitated,
            }
            for pp in result.planet_positions
        ],
    }
