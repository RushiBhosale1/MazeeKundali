"""
api/routers/pdf.py  — Playwright PDF generation for paid kundalis

GET /api/v1/kundalis/:id/pdf  → generates PDF inline, returns bytes
"""
from __future__ import annotations
import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from db import repository as repo
from engine.chart import compute_kundali
from engine.models import TimeAccuracy, RahuMode

logger = logging.getLogger(__name__)
router = APIRouter()

TEMPLATE_PATH = (
    Path(__file__).parent.parent.parent / "static" / "templates" / "kundali_pdf.html"
)
_TPL: str | None = None


def _tpl() -> str:
    global _TPL
    if _TPL is None:
        _TPL = TEMPLATE_PATH.read_text(encoding="utf-8")
    return _TPL


def _render(ctx: dict) -> str:
    from jinja2 import Environment, BaseLoader, select_autoescape
    env = Environment(loader=BaseLoader(), autoescape=select_autoescape(["html"]))
    return env.from_string(_tpl()).render(**ctx)


def _to_pdf_sync(html: str) -> bytes:
    """
    Generate PDF using sync Playwright in a thread.
    Sync API avoids Windows ProactorEventLoop NotImplementedError.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError("Playwright not installed. Run: playwright install chromium")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        )
        page = browser.new_page()
        page.set_content(html, wait_until="domcontentloaded")
        pdf_bytes = page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "12mm", "bottom": "12mm", "left": "10mm", "right": "10mm"},
        )
        browser.close()
    return pdf_bytes


async def _to_pdf(html: str) -> bytes:
    """
    Run sync PDF generation in a thread pool to keep FastAPI async.
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=1) as pool:
        return await loop.run_in_executor(pool, _to_pdf_sync, html)

def _to_image_sync(html: str) -> bytes:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError("Playwright not installed. Run: playwright install chromium")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        )
        page = browser.new_page(device_scale_factor=2)
        # A4 size at 96 DPI
        page.set_viewport_size({"width": 794, "height": 1123})
        page.set_content(html, wait_until="networkidle")
        image_bytes = page.screenshot(type="jpeg", quality=90, full_page=True)
        browser.close()
    return image_bytes

async def _to_image(html: str) -> bytes:
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=1) as pool:
        return await loop.run_in_executor(pool, _to_image_sync, html)


def _ctx_from_result(result, name: str) -> dict:
    from engine.svg_chart import render_north_indian_svg
    pr: dict[str, int] = {}
    rr: set[str] = set()
    plist = []
    for pp in (result.planet_positions or []):
        pr[pp.planet.value] = pp.rashi.value
        if pp.retrograde:
            rr.add(pp.planet.value)
        plist.append({
            "planet_mr": pp.planet.name_mr,
            "rashi": {"name_mr": pp.rashi.name_mr},
            "house": pp.house,
            "degree_in_rashi": round(pp.degree_in_rashi, 2),
            "retrograde": pp.retrograde,
            "is_exalted": pp.is_exalted,
            "is_debilitated": pp.is_debilitated,
        })

    svg = ""
    if result.lagna and pr:
        try:
            svg = render_north_indian_svg(result.lagna.value, pr, rr, width=380, lang="mr")
        except Exception as e:
            logger.warning("SVG render failed: %s", e)

    d = result.dasha
    dc = {
        "mahadasha_lord_mr": d.mahadasha_lord.name_mr,
        "mahadasha_start": str(d.mahadasha_start)[:10],
        "mahadasha_end": str(d.mahadasha_end)[:10],
        "antardasha_lord_mr": d.antardasha_lord.name_mr,
        "antardasha_start": str(d.antardasha_start)[:10],
        "antardasha_end": str(d.antardasha_end)[:10],
    } if d else None

    md = result.mangal_dosha
    mc = {
        "is_manglik": md.is_manglik,
        "cancellation_applied": md.cancellation_applied,
        "cancellation_rule": md.cancellation_rule,
        "explanation_mr": md.explanation_mr,
    } if md else None

    GM = {"Deva": "देव", "Manushya": "मानव", "Rakshasa": "राक्षस"}
    NM = {"Aadi": "आदि", "Madhya": "मध्य", "Antya": "अंत्य"}
    VARNA_MR = {
        "Brahmin": "ब्राह्मण", "Kshatriya": "क्षत्रिय",
        "Vaishya": "वैश्य", "Shudra": "शूद्र",
    }
    from engine.templates import generate_written_analysis
    wa = generate_written_analysis(result) if result.planet_positions else None
    wc = {
        "rashi_description": wa.rashi_analysis_mr,
        "nakshatra_description": wa.nakshatra_analysis_mr,
        "lagna_description": wa.lagna_analysis_mr,
        "dasha_description": wa.dasha_analysis_mr,
        "overall_summary": f"{wa.gana_analysis_mr} {wa.nadi_analysis_mr}",
    } if wa else None

    return {
        "name": result.name,
        "gender": result.gender,
        "dob": str(result.dob),
        "time_of_birth": result.time_of_birth or "",
        "lagna_reliable": result.lagna_reliable,
        "place_text": result.place_text,
        "latitude": result.latitude,
        "longitude": result.longitude,
        "tz_iana": result.tz_iana,
        "rashi_mr": result.rashi.name_mr if result.rashi else "",
        "nakshatra_mr": result.nakshatra.name_mr if result.nakshatra else "",
        "pada": result.pada or "",
        "lagna_mr": result.lagna.name_mr if result.lagna else None,
        "gana_mr": GM.get(result.gana.value, "") if result.gana else "",
        "nadi_mr": NM.get(result.nadi.value, "") if result.nadi else "",
        "varna_mr": VARNA_MR.get(result.varna.value, result.varna.value) if result.varna else None,
        "chart_svg": svg,
        "planet_positions": plist,
        "dasha": dc,
        "mangal_dosha": mc,
        "written_analysis": wc,
        "generated_date": datetime.now().strftime("%d %B %Y, %H:%M IST"),
    }


# ── GET endpoint — browser-friendly (href works) ──────────────────────────────
@router.get("/kundalis/{kundali_id}/pdf")
async def generate_kundali_pdf(kundali_id: str, db: AsyncSession = Depends(get_db)):
    """
    Generate A4 PDF for a paid kundali.
    Uses GET so the browser can navigate directly via <a href=...>.
    Returns 402 if unpaid, 404 if not found.
    """
    import uuid
    try:
        uid = uuid.UUID(kundali_id)
    except ValueError:
        raise HTTPException(400, "Invalid kundali ID.")

    # Load from DB
    kundali_db = await repo.get_kundali(db, uid)
    if not kundali_db:
        raise HTTPException(404, "कुंडली सापडली नाही.")
    if not kundali_db.paid:
        raise HTTPException(402, "PDF फक्त पेड कुंडलीसाठी. प्रथम अनलॉक करा.")

    # Re-compute with paid fields
    profile = kundali_db.birth_profile
    if not profile:
        raise HTTPException(500, "जन्म माहिती उपलब्ध नाही.")

    from datetime import time as dtime
    birth_time = profile.time_of_birth
    if isinstance(birth_time, str):
        try:
            h, m = birth_time.split(":")
            birth_time = dtime(int(h), int(m))
        except Exception:
            birth_time = None

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

    try:
        ctx = _ctx_from_result(result, profile.name)
        pdf = await _to_pdf(_render(ctx))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("PDF generation failed for kundali %s: %s", kundali_id, e)
        # Show actual error message to help debug
        raise HTTPException(500, f"PDF error: {type(e).__name__}: {e}")

    import urllib.parse
    safe_name = "".join(c for c in profile.name if c.isalnum() or c in (" ", "_", "-"))
    safe_name = safe_name.replace(" ", "_")[:20]
    fn = f"kundali_{safe_name}_{kundali_id[:8]}.pdf"
    encoded_fn = urllib.parse.quote(fn)
    content_disposition = f"attachment; filename=\"{encoded_fn}\"; filename*=UTF-8''{encoded_fn}"

    return Response(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": content_disposition},
    )


# ── Biodata PDF and Image Endpoints ──────────────────────────────────────────

BIODATA_TEMPLATE_PATH = Path(__file__).parent.parent.parent / "static" / "templates" / "biodata_pdf.html"
_BIODATA_TPL: str | None = None

def _biodata_tpl() -> str:
    global _BIODATA_TPL
    if _BIODATA_TPL is None:
        _BIODATA_TPL = BIODATA_TEMPLATE_PATH.read_text(encoding="utf-8")
    return _BIODATA_TPL

def _render_biodata(ctx: dict) -> str:
    from jinja2 import Environment, BaseLoader, select_autoescape
    env = Environment(loader=BaseLoader(), autoescape=select_autoescape(["html"]))
    return env.from_string(_biodata_tpl()).render(**ctx)


async def _get_biodata_html(db: AsyncSession, biodata_id: str, preview: bool = False) -> str:
    import uuid
    try:
        uid = uuid.UUID(biodata_id)
    except ValueError:
        raise HTTPException(400, "Invalid biodata ID.")

    biodata = await repo.get_biodata(db, uid)
    if not biodata:
        raise HTTPException(404, "बायोडाटा सापडला नाही.")
    if not biodata.paid and not preview:
        raise HTTPException(402, "PDF/Image फक्त पेड बायोडाटासाठी. प्रथम अनलॉक करा.")
        
    photo_url = biodata.photo_url or ""
    if photo_url and photo_url.startswith("/static/"):
        import pathlib
        import base64
        root_dir = pathlib.Path(__file__).parent.parent.parent
        local_path = root_dir / photo_url.lstrip("/")
        if local_path.exists():
            with open(local_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
                ext = local_path.suffix.lstrip(".") or "jpg"
                photo_url = f"data:image/{ext};base64,{b64}"

    ctx = {
        "id": str(biodata.id),
        "template_id": biodata.template_id,
        "personal_info": biodata.personal_info or {},
        "family_info": biodata.family_info or {},
        "education_info": biodata.education_info or {},
        "horoscope_info": biodata.horoscope_info or {},
        "expectations": biodata.expectations or "",
        "photo_url": photo_url,
        "is_preview": preview and not biodata.paid,
    }
    return _render_biodata(ctx), biodata


@router.get("/biodatas/{biodata_id}/pdf")
async def generate_biodata_pdf(biodata_id: str, db: AsyncSession = Depends(get_db)):
    """Generate A4 PDF for a biodata."""
    html, biodata = await _get_biodata_html(db, biodata_id)
    
    try:
        pdf_bytes = await _to_pdf(html)
    except Exception as e:
        logger.exception("Biodata PDF failed: %s", e)
        raise HTTPException(500, f"PDF error: {e}")

    name = (biodata.personal_info or {}).get("full_name", "biodata").replace(" ", "_")
    import urllib.parse
    fn = f"{name}_{biodata_id[:8]}.pdf"
    encoded_fn = urllib.parse.quote(fn)
    return Response(
        pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=\"{encoded_fn}\"; filename*=UTF-8''{encoded_fn}"},
    )


@router.get("/biodatas/{biodata_id}/image")
async def generate_biodata_image(biodata_id: str, preview: bool = False, db: AsyncSession = Depends(get_db)):
    """Generate high-res Image for WhatsApp sharing for a biodata."""
    html, biodata = await _get_biodata_html(db, biodata_id, preview=preview)
    
    try:
        image_bytes = await _to_image(html)
    except Exception as e:
        logger.exception("Biodata Image failed: %s", e)
        raise HTTPException(500, f"Image error: {e}")

    name = (biodata.personal_info or {}).get("full_name", "biodata").replace(" ", "_")
    import urllib.parse
    fn = f"{name}_{biodata_id[:8]}.jpg"
    encoded_fn = urllib.parse.quote(fn)
    return Response(
        image_bytes,
        media_type="image/jpeg",
        headers={"Content-Disposition": f"attachment; filename=\"{encoded_fn}\"; filename*=UTF-8''{encoded_fn}"},
    )



MATCHING_TEMPLATE_PATH = (
    Path(__file__).parent.parent.parent / "static" / "templates" / "matching_pdf.html"
)
_MATCHING_TPL: str | None = None

def _matching_tpl() -> str:
    global _MATCHING_TPL
    if _MATCHING_TPL is None:
        _MATCHING_TPL = MATCHING_TEMPLATE_PATH.read_text(encoding="utf-8")
    return _MATCHING_TPL

def _render_matching(ctx: dict) -> str:
    from jinja2 import Environment, BaseLoader, select_autoescape
    env = Environment(loader=BaseLoader(), autoescape=select_autoescape(["html"]))
    return env.from_string(_matching_tpl()).render(**ctx)

def _generate_3_charts(result) -> dict:
    from engine.svg_chart import render_north_indian_svg
    from engine.ephemeris import longitude_to_navamsa_rashi
    
    if not result or not result.planet_positions:
        return {"d1": "", "d9": "", "moon": ""}
    
    # D1 Chart (Lagna)
    pr_d1 = {}
    rr = set()
    for pp in result.planet_positions:
        pr_d1[pp.planet.value] = pp.rashi.value
        if pp.retrograde:
            rr.add(pp.planet.value)
    
    svg_d1 = render_north_indian_svg(result.lagna.value, pr_d1, rr, width=230, lang="mr") if result.lagna else ""
    
    # D9 Chart (Navamsa)
    pr_d9 = {}
    for pp in result.planet_positions:
        pr_d9[pp.planet.value] = longitude_to_navamsa_rashi(pp.longitude).value
    
    lagna_d9 = longitude_to_navamsa_rashi(result._raw_ephemeris["lagna_longitude"]).value if hasattr(result, "_raw_ephemeris") else None
    svg_d9 = render_north_indian_svg(lagna_d9, pr_d9, rr, width=230, lang="mr") if lagna_d9 else ""
    
    # Moon Chart (Chandra)
    pr_moon = pr_d1 # Rashi remains same, only ascendant changes to Moon's Rashi
    moon_lagna = pr_d1.get("Moon")
    svg_moon = render_north_indian_svg(moon_lagna, pr_moon, rr, width=230, lang="mr") if moon_lagna else ""
    
    return {"d1": svg_d1, "d9": svg_d9, "moon": svg_moon}

@router.get("/matchings/{matching_id}/pdf")
async def generate_matching_pdf(matching_id: str, db: AsyncSession = Depends(get_db)):
    import uuid
    try:
        mid = uuid.UUID(matching_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")

    record = await repo.get_matching(db, mid)
    if not record:
        raise HTTPException(status_code=404, detail="जुळणी सापडली नाही.")
    if not record.paid:
        raise HTTPException(status_code=403, detail="ही जुळणी अजून अनलॉक केलेली नाही.")

    bride_profile = record.bride_birth_profile if record.bride_birth_profile else (record.bride_kundali.birth_profile if record.bride_kundali else None)
    groom_profile = record.groom_birth_profile if record.groom_birth_profile else (record.groom_kundali.birth_profile if record.groom_kundali else None)
    
    bride_name = bride_profile.name if bride_profile else "वधू"
    groom_name = groom_profile.name if groom_profile else "वर"
    
    bride_dob = bride_profile.dob.strftime("%d-%m-%Y") if bride_profile else "N/A"
    bride_time = bride_profile.time_of_birth.strftime("%I:%M %p") if bride_profile and bride_profile.time_of_birth else "N/A"
    
    groom_dob = groom_profile.dob.strftime("%d-%m-%Y") if groom_profile else "N/A"
    groom_time = groom_profile.time_of_birth.strftime("%I:%M %p") if groom_profile and groom_profile.time_of_birth else "N/A"
    
    # Recompute to get charts and detailed interpretations
    from engine.chart import compute_kundali
    from engine.matching import compute_match
    from engine.models import TimeAccuracy, RahuMode
    from datetime import time as dtime

    def _get_time(bp):
        if not bp or not bp.time_of_birth: return None
        if isinstance(bp.time_of_birth, str):
            h, m = bp.time_of_birth.split(":")
            return dtime(int(h), int(m))
        return bp.time_of_birth

    bride_result = compute_kundali(
        name=bride_name, gender="female", birth_date=bride_profile.dob if bride_profile else None,
        birth_time=_get_time(bride_profile), time_accuracy=TimeAccuracy.EXACT,
        place_text=bride_profile.place_text if bride_profile else "",
        latitude=bride_profile.latitude if bride_profile else 0, longitude=bride_profile.longitude if bride_profile else 0,
        tz_iana=bride_profile.tz_iana if bride_profile else "Asia/Kolkata",
        rahu_mode=RahuMode.TRUE_NODE, compute_paid_fields=True
    ) if bride_profile else None

    groom_result = compute_kundali(
        name=groom_name, gender="male", birth_date=groom_profile.dob if groom_profile else None,
        birth_time=_get_time(groom_profile), time_accuracy=TimeAccuracy.EXACT,
        place_text=groom_profile.place_text if groom_profile else "",
        latitude=groom_profile.latitude if groom_profile else 0, longitude=groom_profile.longitude if groom_profile else 0,
        tz_iana=groom_profile.tz_iana if groom_profile else "Asia/Kolkata",
        rahu_mode=RahuMode.TRUE_NODE, compute_paid_fields=True
    ) if groom_profile else None

    match_result = compute_match(bride_result, groom_result) if bride_result and groom_result else None

    bride_charts = _generate_3_charts(bride_result)
    groom_charts = _generate_3_charts(groom_result)


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
        "total_score": match_result.total_score if match_result else record.total_score,
        "kootas": match_result.kootas if match_result else [],
        "koota_breakdown": record.koota_breakdown or [],
        "bride_charts": bride_charts,
        "groom_charts": groom_charts,
        "nadi_dosha": record.dosha_analysis.get("nadi_dosha") if record.dosha_analysis else None,
        "bhakoot_dosha": record.dosha_analysis.get("bhakoot_dosha") if record.dosha_analysis else None,
        "verdict_mr": record.verdict_mr,
    }

    html = _render_matching(ctx)
    pdf_bytes = await _to_pdf(html)
    
    import urllib.parse
    safe_bride = "".join(c for c in bride_name if c.isalnum() or c in (" ", "_", "-")).replace(" ", "_")[:15]
    safe_groom = "".join(c for c in groom_name if c.isalnum() or c in (" ", "_", "-")).replace(" ", "_")[:15]
    fn = f"matching_{safe_bride}_{safe_groom}.pdf"
    encoded_fn = urllib.parse.quote(fn)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=\"{encoded_fn}\"; filename*=UTF-8''{encoded_fn}"},
    )
