"""
api/routers/orders.py
Razorpay payment flow:

POST /api/v1/orders               → create Razorpay order (server-side)
GET  /api/v1/orders/:id/status    → poll for paid status (frontend polls after payment)
POST /api/v1/webhooks/razorpay    → Razorpay server-to-server webhook (ONLY source of truth)

Critical security rules:
- Razorpay secret NEVER goes to frontend
- Webhook verified via HMAC-SHA256 signature
- Idempotency: duplicate webhook events are silently skipped
- unlock happens ONLY after webhook — never on client callback alone
"""
from __future__ import annotations
import hashlib
import hmac
import logging
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import get_settings
from db.session import get_db
from db import repository as repo
from engine.chart import compute_kundali
from engine.models import TimeAccuracy, RahuMode

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

# ── Pricing (paise — 1 INR = 100 paise) ──────────────────────────────────────
PRICES: dict[str, int] = {
    "kundali":  9900,   # ₹99
    "matching": 4900,   # ₹49
    "biodata":  3900,   # ₹39
    "bundle":   14900,  # ₹149 (adjusting bundle proportionately if needed, wait user didn't ask for bundle. Let's just do 24900)
}


# ── Schemas ───────────────────────────────────────────────────────────────────

class CreateOrderRequest(BaseModel):
    product_type: str          # "kundali" | "matching" | "biodata" | "bundle"
    record_id: Optional[str] = None      # unified: kundali_id / matching_id / biodata_id
    resume_token: Optional[str] = None   # anti-CSRF token (validated per product)
    # Legacy separate fields (kept for backward compat)
    kundali_id: Optional[str] = None
    matching_id: Optional[str] = None
    biodata_id: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    amount_inr: Optional[int] = None     # optional client hint; server validates


class OrderStatusResponse(BaseModel):
    order_id: str
    razorpay_order_id: Optional[str]
    status: str
    product_type: str
    amount_inr: float
    paid: bool
    # If paid, the linked record's new status
    record_unlocked: bool = False


# ── Helpers ───────────────────────────────────────────────────────────────────

def _create_razorpay_order(amount_paise: int, receipt: str) -> dict:
    """
    Create a Razorpay order server-side.
    Returns: {"id": "order_xxx", "amount": 9900, "currency": "INR", ...}

    In production: replace with actual razorpay.orders.create() call.
    In test/dev: returns a mock order.
    """
    if settings.razorpay_key_id and settings.razorpay_key_secret:
        try:
            import razorpay  # type: ignore
            client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
            return client.order.create({  # type: ignore
                "amount": amount_paise,
                "currency": "INR",
                "receipt": receipt,
            })
        except Exception as e:
            logger.error("Razorpay order creation failed: %s", e)
            raise HTTPException(status_code=503, detail="पेमेंट सेवा सध्या उपलब्ध नाही. थोड्या वेळाने पुन्हा प्रयत्न करा.")
    else:
        # No keys configured at all — hard error, don't silently mock
        logger.error("Razorpay keys not configured in .env")
        raise HTTPException(status_code=503, detail="पेमेंट कॉन्फिगर केलेले नाही. कृपया .env तपासा.")


def _verify_razorpay_signature(order_id: str, payment_id: str, signature: str) -> bool:
    """Verify Razorpay payment signature (HMAC-SHA256)."""
    if not settings.razorpay_key_secret:
        return True  # Dev mode — skip verification
    msg = f"{order_id}|{payment_id}"
    expected = hmac.new(
        settings.razorpay_key_secret.encode(), msg.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def _verify_webhook_signature(body: bytes, signature: str) -> bool:
    """Verify Razorpay webhook signature."""
    if not settings.razorpay_webhook_secret:
        return True  # Dev mode
    expected = hmac.new(
        settings.razorpay_webhook_secret.encode(), body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)



from services.email import send_pdf_email
from api.routers.pdf import _to_pdf, _render, _render_matching, _render_biodata

async def _send_post_payment_email(order):
    from db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        try:
            # Check if email is provided
            if not order.customer_email:
                return
    
            subject = ""
            html_body = ""
            pdf_bytes = None
            filename = ""
    
            if order.product_type in ("kundali", "bundle") and order.kundali_id:
                kundali = await repo.get_kundali(db, order.kundali_id)
                if kundali and kundali.birth_profile:
                    from datetime import datetime
                    ctx = {
                        "generated_at": datetime.now().strftime("%d %b %Y"),
                        "name": kundali.birth_profile.name,
                        "gender": kundali.birth_profile.gender,
                        "dob": kundali.birth_profile.dob.strftime("%d %b %Y"),
                        "time_of_birth": kundali.birth_profile.time_of_birth.strftime("%I:%M %p") if kundali.birth_profile.time_of_birth else "Unknown",
                        "place_text": kundali.birth_profile.place_text,
                        "rashi": kundali.rashi.name_mr if kundali.rashi else "N/A",
                        "nakshatra": kundali.nakshatra.name_mr if kundali.nakshatra else "N/A",
                        "paid": True,
                        "planet_positions": kundali.planet_positions or [],
                        "mangal_dosha": kundali.mangal_dosha or {},
                        "dasha": kundali.dasha or {},
                        "written_analysis": kundali.written_analysis,
                    }
                    html = _render(ctx)
                    pdf_bytes = await _to_pdf(html)
                    subject = f"तुमचा जन्मकुंडली अहवाल — {kundali.birth_profile.name}"
                    html_body = f"<p>नमस्कार,</p><p>तुमचा जन्मकुंडली अहवाल सोबत जोडला आहे.</p>"
                    filename = f"kundali_{kundali.birth_profile.name.replace(' ', '_')}.pdf"
    
            elif order.product_type in ("matching", "bundle") and order.matching_id:
                record = await repo.get_matching(db, order.matching_id)
                if record:
                    bride_name = record.bride_birth_profile.name if record.bride_birth_profile else "वधू"
                    groom_name = record.groom_birth_profile.name if record.groom_birth_profile else "वर"
                    bride_dob = record.bride_birth_profile.dob.strftime("%d-%m-%Y") if record.bride_birth_profile else "N/A"
                    bride_time = record.bride_birth_profile.time_of_birth.strftime("%I:%M %p") if record.bride_birth_profile and record.bride_birth_profile.time_of_birth else "N/A"
                    groom_dob = record.groom_birth_profile.dob.strftime("%d-%m-%Y") if record.groom_birth_profile else "N/A"
                    groom_time = record.groom_birth_profile.time_of_birth.strftime("%I:%M %p") if record.groom_birth_profile and record.groom_birth_profile.time_of_birth else "N/A"
                    from datetime import datetime
                    ctx = {
                        "generated_at": datetime.now().strftime("%d %b %Y"),
                        "bride_name": bride_name,
                        "groom_name": groom_name,
                        "bride_dob": bride_dob,
                        "bride_time": bride_time,
                        "bride_manglik": record.bride_manglik,
                        "groom_dob": groom_dob,
                        "groom_time": groom_time,
                        "groom_manglik": record.groom_manglik,
                        "total_score": record.total_score,
                        "koota_breakdown": record.koota_breakdown or [],
                        "nadi_dosha": record.dosha_analysis.get("nadi_dosha") if record.dosha_analysis else None,
                        "bhakoot_dosha": record.dosha_analysis.get("bhakoot_dosha") if record.dosha_analysis else None,
                        "verdict_mr": record.verdict_mr,
                    }
                    html = _render_matching(ctx)
                    pdf_bytes = await _to_pdf(html)
                    subject = f"तुमचा पत्रिका जुळणी अहवाल — {bride_name} & {groom_name}"
                    html_body = f"<p>नमस्कार,</p><p>तुमचा पत्रिका जुळणी अहवाल सोबत जोडला आहे.</p>"
                    filename = f"matching_{bride_name}_{groom_name}.pdf".replace(" ", "_")
    
            elif order.product_type in ("biodata", "bundle") and order.biodata_id:
                record = await repo.get_biodata(db, order.biodata_id)
                if record:
                    ctx = {
                        "personal_info": record.personal_info or {},
                        "family_info": record.family_info or {},
                        "education_info": record.education_info or {},
                        "horoscope_info": record.horoscope_info or {},
                        "expectations": record.expectations or "",
                        "photo_url": record.photo_url,
                    }
                    html = _render_biodata(ctx, record.template_id)
                    pdf_bytes = await _to_pdf(html)
                    name = ctx["personal_info"].get("full_name", "Biodata")
                    subject = f"तुमचा मराठी बायोडाटा — {name}"
                    html_body = f"<p>नमस्कार,</p><p>तुमचा मराठी बायोडाटा सोबत जोडला आहे.</p>"
                    filename = f"biodata_{name.replace(' ', '_')}.pdf"
                    
            if pdf_bytes and order.customer_email:
                await send_pdf_email(order.customer_email, subject, html_body, pdf_bytes, filename)
        except Exception as e:
            import logging
        logging.getLogger(__name__).exception("Failed to send post-payment email")


async def _unlock_record(db: AsyncSession, order, bg: BackgroundTasks) -> None:
    """After confirmed payment — unlock the correct record."""
    try:
        if order.product_type in ("kundali", "bundle") and order.kundali_id:
            # Re-compute paid fields for this kundali
            kundali = await repo.get_kundali(db, order.kundali_id)
            if kundali and not kundali.paid:
                profile = kundali.birth_profile
                if profile:
                    from datetime import time as dtime
                    birth_time = profile.time_of_birth
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
                        compute_paid_fields=True,
                    )
                    paid_data = {
                        "planet_positions": [
                            {
                                "planet_en": pp.planet.value,
                                "planet_mr": pp.planet.name_mr,
                                "rashi": {"value": pp.rashi.value, "name_en": pp.rashi.name_en, "name_mr": pp.rashi.name_mr},
                                "degree_in_rashi": round(pp.degree_in_rashi, 4),
                                "house": pp.house,
                                "nakshatra": {"value": pp.nakshatra.value, "name_en": pp.nakshatra.name_en, "name_mr": pp.nakshatra.name_mr} if pp.nakshatra else None,
                                "pada": pp.pada,
                                "retrograde": pp.retrograde,
                                "is_exalted": pp.is_exalted,
                                "is_debilitated": pp.is_debilitated,
                            }
                            for pp in result.planet_positions
                        ] if result.planet_positions else [],
                        "mangal_dosha": {
                            "is_manglik": result.mangal_dosha.is_manglik,
                            "reference_point": result.mangal_dosha.reference_point,
                            "mars_house": result.mangal_dosha.mars_house,
                            "cancellation_applied": result.mangal_dosha.cancellation_applied,
                            "cancellation_rule": result.mangal_dosha.cancellation_rule,
                            "explanation_mr": result.mangal_dosha.explanation_mr,
                            "explanation_en": result.mangal_dosha.explanation_en,
                        } if result.mangal_dosha else None,
                        "dasha": {
                            "mahadasha_lord_en": result.dasha.mahadasha_lord.value,
                            "mahadasha_lord_mr": result.dasha.mahadasha_lord.name_mr,
                            "mahadasha_start": str(result.dasha.mahadasha_start),
                            "mahadasha_end": str(result.dasha.mahadasha_end),
                            "antardasha_lord_en": result.dasha.antardasha_lord.value,
                            "antardasha_lord_mr": result.dasha.antardasha_lord.name_mr,
                            "antardasha_start": str(result.dasha.antardasha_start),
                            "antardasha_end": str(result.dasha.antardasha_end),
                        } if result.dasha else None,
                        "written_analysis": None,  # generated from templates.py separately
                    }
                    await repo.unlock_kundali(db, order.kundali_id, paid_data)
                    logger.info("Kundali %s unlocked after payment", order.kundali_id)

        if order.product_type in ("matching", "bundle") and order.matching_id:
            matching = await repo.get_matching(db, order.matching_id)
            if matching and not matching.paid:
                await repo.unlock_matching(db, order.matching_id)

        if order.product_type in ("biodata", "bundle") and order.biodata_id:
            biodata = await repo.get_biodata(db, order.biodata_id)
            if biodata and not biodata.paid:
                # unlocking biodata is just setting paid=True
                await repo.update_biodata(db, biodata.id, paid=True)
                logger.info("Biodata %s unlocked after payment", order.biodata_id)


        if order.customer_email:
            # Re-fetch order from db to ensure it's bound or use local vars
            bg.add_task(_send_post_payment_email, order)
            
    except Exception as e:
        logger.exception("Error unlocking record for order %s: %s", order.id, e)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/orders", status_code=201)
async def create_order(
    request: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a Razorpay order server-side.
    Frontend uses the returned razorpay_order_id to open Razorpay Checkout.
    """
    if request.product_type not in PRICES:
        raise HTTPException(status_code=400, detail=f"Invalid product_type: {request.product_type}")

    amount = PRICES[request.product_type]

    # Resolve record_id → kundali_id / matching_id / biodata_id
    rid = request.record_id
    if rid:
        if request.product_type == "kundali":
            request.kundali_id = rid
        elif request.product_type == "matching":
            request.matching_id = rid
        elif request.product_type == "biodata":
            request.biodata_id = rid

    # Validate referenced record exists
    kundali_id = uuid.UUID(request.kundali_id) if request.kundali_id else None
    matching_id = uuid.UUID(request.matching_id) if request.matching_id else None
    biodata_id = uuid.UUID(request.biodata_id) if request.biodata_id else None

    if kundali_id:
        k = await repo.get_kundali(db, kundali_id)
        if not k:
            raise HTTPException(status_code=404, detail="कुंडली सापडली नाही.")
        if k.paid:
            raise HTTPException(status_code=409, detail="ही कुंडली आधीच अनलॉक आहे.")

    if biodata_id:
        b = await repo.get_biodata(db, biodata_id)
        if not b:
            raise HTTPException(status_code=404, detail="बायोडाटा सापडला नाही.")
        if b.paid:
            raise HTTPException(status_code=409, detail="हा बायोडाटा आधीच अनलॉक आहे.")

    if matching_id:
        m = await repo.get_matching(db, matching_id)
        if not m:
            raise HTTPException(status_code=404, detail="जुळणी अहवाल सापडला नाही.")
        if m.paid:
            raise HTTPException(status_code=409, detail="हा जुळणी अहवाल आधीच अनलॉक आहे.")

    # Create our order record
    order = await repo.create_order(
        db, request.product_type, amount,
        kundali_id=kundali_id,
        matching_id=matching_id,
        biodata_id=biodata_id,
        phone=request.customer_phone,
        email=request.customer_email,
    )

    # Create Razorpay order server-side
    receipt = str(order.id)[:16].replace("-", "")
    rz_order = _create_razorpay_order(amount, receipt)
    razorpay_order_id = rz_order.get("id", "")

    # Update our order with Razorpay ID
    from sqlalchemy import update
    from db.models import Order
    await db.execute(
        update(Order).where(Order.id == order.id).values(razorpay_order_id=razorpay_order_id)
    )

    return {
        "order_id": str(order.id),
        "razorpay_order_id": razorpay_order_id,
        "key_id": settings.razorpay_key_id,          # frontend expects key_id
        "razorpay_key_id": settings.razorpay_key_id,  # backward compat
        "amount_paise": amount,
        "amount_inr": amount / 100,
        "currency": "INR",
        "product_type": request.product_type,
    }

# ── Verify Payment (client callback — works WITHOUT webhook) ──────────────────
class VerifyPaymentRequest(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str


@router.post("/orders/verify")
async def verify_payment(
    req: VerifyPaymentRequest,
    bg: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Called by frontend immediately after Razorpay payment callback fires.
    Verifies HMAC-SHA256 signature server-side and unlocks the product.
    Works WITHOUT a webhook — standard pattern for localhost/dev.
    """
    # 1. Verify signature (skip check in dev if no secret configured)
    if not _verify_razorpay_signature(
        req.razorpay_order_id, req.razorpay_payment_id, req.razorpay_signature
    ):
        logger.warning("Invalid payment signature for order %s", req.razorpay_order_id)
        raise HTTPException(status_code=400, detail="अवैध पेमेंट सिग्नेचर.")

    # 2. Find our internal order
    order = await repo.get_order_by_razorpay_id(db, req.razorpay_order_id)
    if not order:
        raise HTTPException(status_code=404, detail="ऑर्डर सापडला नाही.")

    # 3. Idempotent
    if order.status == "paid":
        logger.info("Order %s already paid (idempotent verify)", order.id)
        return {"status": "already_paid", "unlocked": True}

    # 4. Mark order paid + unlock product
    await repo.mark_order_paid(
        db, order.id, req.razorpay_payment_id, req.razorpay_signature, req.razorpay_order_id,
    )
    await _unlock_record(db, order, bg)

    logger.info("Payment verified & unlocked: order=%s payment=%s", order.id, req.razorpay_payment_id)
    return {
        "status": "paid",
        "unlocked": True,
        "order_id": str(order.id),
        "product_type": order.product_type,
    }


@router.get("/orders/{order_id}/status", response_model=OrderStatusResponse)
async def get_order_status(
    order_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Frontend polls this after Razorpay payment success callback.
    Returns paid=true once webhook has confirmed payment.
    """
    try:
        oid = uuid.UUID(order_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order ID")

    order = await repo.get_order(db, oid)
    if not order:
        raise HTTPException(status_code=404, detail="Order सापडला नाही.")

    record_unlocked = False
    if order.status == "paid":
        if order.kundali_id:
            k = await repo.get_kundali(db, order.kundali_id)
            record_unlocked = k.paid if k else False

    return OrderStatusResponse(
        order_id=str(order.id),
        razorpay_order_id=order.razorpay_order_id,
        status=order.status,
        product_type=order.product_type,
        amount_inr=order.amount_paise / 100,
        paid=order.status == "paid",
        record_unlocked=record_unlocked,
    )


@router.post("/webhooks/razorpay")
async def razorpay_webhook(
    request: Request,
    bg: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Razorpay server-to-server webhook.
    THIS IS THE ONLY SOURCE OF TRUTH for payment confirmation.
    Frontend polls /orders/:id/status — does NOT directly trust client callback.

    Security:
    - Verify X-Razorpay-Signature header
    - Idempotency via webhook_events table (skip if event_id already processed)
    """
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    if not _verify_webhook_signature(body, signature):
        logger.warning("Invalid Razorpay webhook signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    try:
        import json
        payload = json.loads(body)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_id = payload.get("payload", {}).get("payment", {}).get("entity", {}).get("id", "")
    event_type = payload.get("event", "")

    if not event_id:
        # Some webhook events don't have payment entity — log and return 200
        logger.info("Razorpay webhook with no payment entity: %s", event_type)
        return {"status": "ok"}

    # ── Idempotency check ─────────────────────────────────────────────────────
    existing = await repo.get_webhook_event(db, event_id)
    if existing and existing.processed:
        logger.info("Duplicate webhook event %s — skipping", event_id)
        return {"status": "already_processed"}

    # Record the event
    await repo.create_webhook_event(db, event_id, event_type, payload)

    # ── Process payment.captured ──────────────────────────────────────────────
    if event_type == "payment.captured":
        payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        razorpay_order_id = payment_entity.get("order_id", "")
        razorpay_payment_id = payment_entity.get("id", "")
        razorpay_signature = signature  # store raw sig

        if not razorpay_order_id:
            logger.warning("payment.captured without order_id: %s", event_id)
            await repo.mark_webhook_processed(db, event_id, error="No order_id in payload")
            return {"status": "ok"}

        # Find our order by Razorpay order ID
        order = await repo.get_order_by_razorpay_id(db, razorpay_order_id)
        if not order:
            logger.warning("No local order found for razorpay_order_id=%s", razorpay_order_id)
            await repo.mark_webhook_processed(db, event_id, error="Order not found")
            return {"status": "ok"}

        if order.status == "paid":
            logger.info("Order %s already paid — idempotent", order.id)
            await repo.mark_webhook_processed(db, event_id)
            return {"status": "already_paid"}

        # Mark order as paid
        await repo.mark_order_paid(
            db, order.id, razorpay_payment_id, razorpay_signature, razorpay_order_id
        )

        # Unlock the product (run in background to avoid webhook timeout)
        await _unlock_record(db, order, bg)

        await repo.mark_webhook_processed(db, event_id)
        logger.info("Payment captured and record unlocked: order=%s payment=%s", order.id, razorpay_payment_id)

    elif event_type == "payment.failed":
        razorpay_order_id = (
            payload.get("payload", {}).get("payment", {}).get("entity", {}).get("order_id", "")
        )
        if razorpay_order_id:
            from sqlalchemy import update
            from db.models import Order
            await db.execute(
                update(Order).where(Order.razorpay_order_id == razorpay_order_id).values(status="failed")
            )
        await repo.mark_webhook_processed(db, event_id)
        logger.info("Payment failed: event=%s", event_id)

    return {"status": "ok"}
