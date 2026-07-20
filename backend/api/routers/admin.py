from fastapi import APIRouter, Depends, HTTPException, Header, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import logging

from db.session import get_db
from db import repository as repo
from api.config import get_settings
from api.routers.orders import _unlock_record

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

async def verify_admin_token(x_admin_token: str = Header(None)):
    if not settings.admin_token:
        # If no admin token is set on the backend, refuse all admin access
        raise HTTPException(status_code=500, detail="Admin token not configured on server")
    if not x_admin_token or x_admin_token != settings.admin_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

@router.get("/orders")
async def list_orders(db: AsyncSession = Depends(get_db), token: None = Depends(verify_admin_token)):
    orders = await repo.get_all_orders(db, limit=200)
    data = []
    for o in orders:
        record_unlocked = False
        if o.status == "paid":
            if o.kundali_id and o.kundali:
                record_unlocked = o.kundali.paid
            elif o.matching_id and o.matching:
                record_unlocked = o.matching.paid
            elif o.biodata_id and o.biodata:
                record_unlocked = o.biodata.paid
        
        data.append({
            "id": str(o.id),
            "product_type": o.product_type,
            "amount_inr": o.amount_paise // 100,
            "status": o.status,
            "paid": o.status == "paid",
            "razorpay_order_id": o.razorpay_order_id,
            "record_unlocked": record_unlocked
        })
    return {"orders": data}

@router.post("/orders/{order_id}/force-unlock")
async def force_unlock_order(order_id: str, bg: BackgroundTasks, db: AsyncSession = Depends(get_db), token: None = Depends(verify_admin_token)):
    try:
        oid = uuid.UUID(order_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order ID")

    order = await repo.get_order(db, oid)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status == "paid":
        return {"msg": "Order is already paid and unlocked"}

    # Mark as paid
    order.status = "paid"
    await db.flush()

    # Call the exact same unlock logic as the webhook
    await _unlock_record(db, order, bg)
    
    return {"msg": "Order forcefully unlocked"}

@router.get("/webhooks")
async def list_webhooks(db: AsyncSession = Depends(get_db), token: None = Depends(verify_admin_token)):
    hooks = await repo.get_recent_webhooks(db, limit=100)
    return {
        "webhooks": [
            {
                "id": str(h.id),
                "event_id": h.event_id,
                "event_type": h.event_type,
                "processed": h.processed,
                "created_at": h.created_at.isoformat(),
                "error": h.error
            } for h in hooks
        ]
    }
