"""
main.py
FastAPI application entry point — full production setup.
"""
from __future__ import annotations
import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from api.config import get_settings
from api.routers import geocode, kundali, orders, matching, biodata, pdf, upload, admin
from fastapi.staticfiles import StaticFiles

# ── Logging ───────────────────────────────────────────────────────────────────
settings = get_settings()
logging.basicConfig(
    level=logging.DEBUG if settings.is_development else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── Rate limiter (Redis-backed in prod, in-memory in dev) ─────────────────────
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"],
    storage_uri=settings.redis_url if settings.redis_url else "memory://",
)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="माझी कुंडली API",
    description="Marathi Kundali, Patrika Matching & Biodata Platform — Backend API",
    version="0.2.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

# ── CORS ──────────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://mazeekundali.in",       # production — update before launch
    "https://www.mazeekundali.in",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    import swisseph as swe
    ephe_path = settings.ephe_path
    swe.set_ephe_path(ephe_path)
    os.environ["EPHE_PATH"] = ephe_path
    logger.info("Swiss Ephemeris initialized: %s", ephe_path)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(geocode.router,  prefix="/api/v1", tags=["Geocoding"])
app.include_router(kundali.router,  prefix="/api/v1", tags=["Kundali"])
app.include_router(matching.router, prefix="/api/v1", tags=["Matching"])
app.include_router(orders.router,   prefix="/api/v1", tags=["Orders & Payment"])
app.include_router(biodata.router,  prefix="/api/v1", tags=["Biodata"])
app.include_router(pdf.router,      prefix="/api/v1", tags=["PDF"])
app.include_router(upload.router,   prefix="/api/v1", tags=["Upload"])
app.include_router(admin.router)

import pathlib
static_path = pathlib.Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "kundali-backend", "version": "0.2.0"}

# ── Global error handler ─────────────────────────────────────────────────────
# IMPORTANT: Only catch unexpected errors (not HTTPException).
# HTTPExceptions flow through CORS middleware correctly on their own.
@app.exception_handler(Exception)
async def global_error_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc  # let FastAPI handle 4xx/5xx with proper CORS headers
    logger.exception("Unhandled exception: %s", exc)
    # Manually add CORS header so browser can read the error message
    origin = request.headers.get("origin", "")
    headers = {}
    if origin in ALLOWED_ORIGINS:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    return JSONResponse(
        status_code=500,
        content={"detail": "\u0924\u093e\u0902\u0924\u094d\u0930\u093f\u0915 \u0938\u092e\u0938\u094d\u092f\u093e \u0906\u0932\u0940. \u0915\u0943\u092a\u092f\u093e \u0925\u094b\u0921\u094d\u092f\u093e \u0935\u0947\u0933\u093e\u0928\u0947 \u092a\u0941\u0928\u094d\u0939\u093e \u092a\u094d\u0930\u092f\u0924\u094d\u0928 \u0915\u0930\u093e."},
        headers=headers,
    )
