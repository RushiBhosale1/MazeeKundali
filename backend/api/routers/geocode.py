"""
api/routers/geocode.py
GET /api/v1/geocode?query=Kolhapur
Returns candidate places with lat/long + IANA timezone.
Rate limited: 30/minute per IP (prevents scraping the geocoding service).
"""
from __future__ import annotations
import logging
from fastapi import APIRouter, Query, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from api.schemas import GeocodeResponse, PlaceCandidate
from engine.geocoding import geocode_place

limiter = Limiter(key_func=get_remote_address)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/geocode", response_model=GeocodeResponse)
@limiter.limit("120/minute")
async def geocode_endpoint(
    request: Request,
    query: str = Query(..., min_length=2, max_length=200, description="Place name to search"),
    limit: int = Query(5, ge=1, le=10),
):
    """
    Search for a birth place by name.
    Returns up to `limit` matching places with coordinates and IANA timezone.

    Used for the autocomplete search on the birth input form.
    Example: /api/v1/geocode?query=Kolhapur
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    results = geocode_place(query.strip(), max_results=limit)

    if not results:
        return GeocodeResponse(places=[])

    return GeocodeResponse(
        places=[
            PlaceCandidate(
                display_name=r.display_name,
                latitude=r.latitude,
                longitude=r.longitude,
                tz_iana=r.tz_iana,
            )
            for r in results
        ]
    )
