"""
db/repository.py
Data-access layer — all DB queries go through here.
Keeps routers thin and testable.
"""
from __future__ import annotations
import uuid
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import (
    BirthProfile, Kundali, Matching, Biodata, Order, WebhookEvent, GeocodeCache,
)
from engine.models import KundaliResult


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _resume_token() -> str:
    return secrets.token_urlsafe(32)


# ──────────────────────────────────────────────────────────────────────────────
# Geocode Cache
# ──────────────────────────────────────────────────────────────────────────────

async def get_geocode_cache(db: AsyncSession, query: str) -> Optional[GeocodeCache]:
    result = await db.execute(
        select(GeocodeCache).where(GeocodeCache.query_normalized == query.lower().strip())
    )
    return result.scalar_one_or_none()


async def save_geocode_cache(db: AsyncSession, query: str, display_name: str,
                              lat: float, lng: float, tz: str) -> GeocodeCache:
    row = GeocodeCache(
        query_normalized=query.lower().strip(),
        display_name=display_name,
        latitude=lat,
        longitude=lng,
        tz_iana=tz,
    )
    db.add(row)
    await db.flush()
    return row


# ──────────────────────────────────────────────────────────────────────────────
# Birth Profile
# ──────────────────────────────────────────────────────────────────────────────

async def create_birth_profile(db: AsyncSession, result: KundaliResult,
                                gender: str, rahu_mode: str) -> BirthProfile:
    # asyncpg requires datetime.time, not a string, for TIME columns
    from datetime import time as _time
    tob_raw = result.time_of_birth
    if isinstance(tob_raw, str) and tob_raw:
        h, m = tob_raw.split(":")[:2]
        tob: Optional[_time] = _time(int(h), int(m))
    elif isinstance(tob_raw, _time):
        tob = tob_raw
    else:
        tob = None

    profile = BirthProfile(
        id=uuid.uuid4(),
        name=result.name,
        gender=gender,
        dob=result.dob,
        time_of_birth=tob,
        time_accuracy=result.time_accuracy.value,
        place_text=result.place_text,
        latitude=result.latitude,
        longitude=result.longitude,
        tz_iana=result.tz_iana,
        rahu_mode=rahu_mode,
    )
    db.add(profile)
    await db.flush()
    return profile


# ──────────────────────────────────────────────────────────────────────────────
# Kundali
# ──────────────────────────────────────────────────────────────────────────────

async def create_kundali(db: AsyncSession, birth_profile: BirthProfile,
                          result: KundaliResult, chart_svg: Optional[str] = None) -> Kundali:
    kundali = Kundali(
        id=uuid.uuid4(),
        birth_profile_id=birth_profile.id,
        rashi_value=result.rashi.value if result.rashi else None,
        nakshatra_value=result.nakshatra.value if result.nakshatra else None,
        pada=result.pada,
        lagna_value=result.lagna.value if result.lagna else None,
        lagna_reliable=result.lagna_reliable,
        gana=result.gana.value if result.gana else None,
        nadi=result.nadi.value if result.nadi else None,
        varna=result.varna.value if result.varna else None,
        chart_d1_svg=chart_svg,
        paid=False,
        resume_token=_resume_token(),
        # Auto-expire unpaid drafts after 30 days
        expires_at=_utcnow() + timedelta(days=30),
    )
    db.add(kundali)
    await db.flush()
    return kundali


async def get_kundali(db: AsyncSession, kundali_id: uuid.UUID) -> Optional[Kundali]:
    result = await db.execute(
        select(Kundali)
        .options(selectinload(Kundali.birth_profile))
        .where(Kundali.id == kundali_id)
    )
    return result.scalar_one_or_none()


async def get_kundali_by_token(db: AsyncSession, token: str) -> Optional[Kundali]:
    result = await db.execute(
        select(Kundali)
        .options(selectinload(Kundali.birth_profile))
        .where(Kundali.resume_token == token)
    )
    return result.scalar_one_or_none()


async def unlock_kundali(db: AsyncSession, kundali_id: uuid.UUID,
                          paid_data: dict) -> None:
    """Mark kundali as paid and populate paid-tier fields."""
    await db.execute(
        update(Kundali)
        .where(Kundali.id == kundali_id)
        .values(
            paid=True,
            paid_at=_utcnow(),
            expires_at=_utcnow() + timedelta(days=365 * 2),  # 2 years for paid
            planet_positions=paid_data.get("planet_positions"),
            mangal_dosha=paid_data.get("mangal_dosha"),
            dasha=paid_data.get("dasha"),
            written_analysis=paid_data.get("written_analysis"),
        )
    )


async def set_kundali_pdf(db: AsyncSession, kundali_id: uuid.UUID, pdf_url: str) -> None:
    await db.execute(
        update(Kundali).where(Kundali.id == kundali_id).values(pdf_url=pdf_url)
    )


# ──────────────────────────────────────────────────────────────────────────────
# Matching
# ──────────────────────────────────────────────────────────────────────────────

async def create_matching(
    db: AsyncSession,
    total_score: int,
    bride_manglik: Optional[bool],
    groom_manglik: Optional[bool],
    bride_manglik_severity: Optional[str],
    groom_manglik_severity: Optional[str],
    koota_breakdown: list,
    dosha_analysis: dict,
    verdict_mr: str,
    verdict_en: str,
    bride_kundali_id: Optional[uuid.UUID] = None,
    groom_kundali_id: Optional[uuid.UUID] = None,
    bride_profile_id: Optional[uuid.UUID] = None,
    groom_profile_id: Optional[uuid.UUID] = None
) -> Matching:
    matching = Matching(
        id=uuid.uuid4(),
        bride_kundali_id=bride_kundali_id,
        groom_kundali_id=groom_kundali_id,
        bride_birth_profile_id=bride_profile_id,
        groom_birth_profile_id=groom_profile_id,
        total_score=total_score,
        total_max=36,
        bride_manglik=bride_manglik,
        groom_manglik=groom_manglik,
        bride_manglik_severity=bride_manglik_severity,
        groom_manglik_severity=groom_manglik_severity,
        paid=False,
        koota_breakdown=koota_breakdown,
        dosha_analysis=dosha_analysis,
        verdict_mr=verdict_mr,
        verdict_en=verdict_en,
        resume_token=_resume_token(),
        expires_at=_utcnow() + timedelta(days=30),
    )
    db.add(matching)
    await db.flush()
    return matching


async def get_matching(db: AsyncSession, matching_id: uuid.UUID) -> Optional[Matching]:
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Matching)
        .options(
            selectinload(Matching.bride_birth_profile),
            selectinload(Matching.groom_birth_profile),
            selectinload(Matching.bride_kundali).selectinload(Kundali.birth_profile),
            selectinload(Matching.groom_kundali).selectinload(Kundali.birth_profile),
        )
        .where(Matching.id == matching_id)
    )
    return result.scalar_one_or_none()


async def unlock_matching(db: AsyncSession, matching_id: uuid.UUID) -> None:
    await db.execute(
        update(Matching)
        .where(Matching.id == matching_id)
        .values(
            paid=True,
            paid_at=_utcnow(),
            expires_at=_utcnow() + timedelta(days=365 * 2),
        )
    )


# ──────────────────────────────────────────────────────────────────────────────
# Order
# ──────────────────────────────────────────────────────────────────────────────

async def create_order(db: AsyncSession, product_type: str, amount_paise: int,
                        kundali_id: Optional[uuid.UUID] = None,
                        matching_id: Optional[uuid.UUID] = None,
                        biodata_id: Optional[uuid.UUID] = None,
                        phone: Optional[str] = None,
                        email: Optional[str] = None) -> Order:
    order = Order(
        id=uuid.uuid4(),
        product_type=product_type,
        amount_paise=amount_paise,
        kundali_id=kundali_id,
        matching_id=matching_id,
        biodata_id=biodata_id,
        status="created",
        customer_phone=phone,
        customer_email=email,
    )
    db.add(order)
    await db.flush()
    return order


async def get_order(db: AsyncSession, order_id: uuid.UUID) -> Optional[Order]:
    result = await db.execute(select(Order).where(Order.id == order_id))
    return result.scalar_one_or_none()


async def get_order_by_razorpay_id(db: AsyncSession, razorpay_order_id: str) -> Optional[Order]:
    result = await db.execute(
        select(Order).where(Order.razorpay_order_id == razorpay_order_id)
    )
    return result.scalar_one_or_none()


async def mark_order_paid(db: AsyncSession, order_id: uuid.UUID,
                           razorpay_payment_id: str, razorpay_signature: str,
                           razorpay_order_id: str) -> None:
    await db.execute(
        update(Order)
        .where(Order.id == order_id)
        .values(
            status="paid",
            paid_at=_utcnow(),
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature,
            razorpay_order_id=razorpay_order_id,
        )
    )


# ──────────────────────────────────────────────────────────────────────────────
# Webhook Events (idempotency)
# ──────────────────────────────────────────────────────────────────────────────

async def get_webhook_event(db: AsyncSession, event_id: str) -> Optional[WebhookEvent]:
    result = await db.execute(
        select(WebhookEvent).where(WebhookEvent.event_id == event_id)
    )
    return result.scalar_one_or_none()


async def create_webhook_event(db: AsyncSession, event_id: str, event_type: str,
                                payload: dict) -> WebhookEvent:
    event = WebhookEvent(
        id=uuid.uuid4(),
        event_id=event_id,
        event_type=event_type,
        payload=payload,
    )
    db.add(event)
    await db.flush()
    return event


async def mark_webhook_processed(db: AsyncSession, event_id: str,
                                  error: Optional[str] = None) -> None:
    await db.execute(
        update(WebhookEvent)
        .where(WebhookEvent.event_id == event_id)
        .values(
            processed=True,
            processed_at=_utcnow(),
            error=error,
        )
    )

# ──────────────────────────────────────────────────────────────────────────────
# Biodata
# ──────────────────────────────────────────────────────────────────────────────

async def create_biodata(db: AsyncSession, template_id: str = "traditional", kundali_id: Optional[uuid.UUID] = None) -> Biodata:
    biodata = Biodata(
        id=uuid.uuid4(),
        template_id=template_id,
        kundali_id=kundali_id,
        resume_token=_resume_token(),
        paid=True,
    )
    db.add(biodata)
    await db.flush()
    return biodata

async def get_biodata(db: AsyncSession, biodata_id: uuid.UUID) -> Optional[Biodata]:
    result = await db.execute(select(Biodata).where(Biodata.id == biodata_id))
    return result.scalar_one_or_none()

async def get_biodata_by_token(db: AsyncSession, biodata_id: uuid.UUID, token: str) -> Optional[Biodata]:
    result = await db.execute(
        select(Biodata).where(Biodata.id == biodata_id, Biodata.resume_token == token)
    )
    return result.scalar_one_or_none()

async def update_biodata(db: AsyncSession, biodata_id: uuid.UUID, **kwargs) -> Optional[Biodata]:
    biodata = await get_biodata(db, biodata_id)
    if not biodata:
        return None
    for key, value in kwargs.items():
        if hasattr(biodata, key):
            setattr(biodata, key, value)
    await db.flush()
    return biodata

async def unlock_biodata(db: AsyncSession, biodata_id: uuid.UUID) -> None:
    await db.execute(
        update(Biodata)
        .where(Biodata.id == biodata_id)
        .values(
            paid=True,
            paid_at=_utcnow()
        )
    )

# ──────────────────────────────────────────────────────────────────────────────
# Admin Utilities
# ──────────────────────────────────────────────────────────────────────────────

async def get_all_orders(db: AsyncSession, limit: int = 200) -> list[Order]:
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.kundali),
            selectinload(Order.matching),
            selectinload(Order.biodata)
        )
        .order_by(Order.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())

async def get_recent_webhooks(db: AsyncSession, limit: int = 100) -> list[WebhookEvent]:
    result = await db.execute(
        select(WebhookEvent).order_by(WebhookEvent.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())

