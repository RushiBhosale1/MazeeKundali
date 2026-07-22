"""
astrosage_link_generator.py
────────────────────────────
Given two birth details, print:
  1. The AstroSage Kundli Matching URL (click to verify instantly)
  2. Our engine's computed koota breakdown

Usage:
    python astrosage_link_generator.py

Or import and call generate_link() from code.
"""
import sys
import os
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def generate_astrosage_url(
    boy_name, boy_dob, boy_time, boy_lat, boy_lon, boy_tz=5.5,
    girl_name, girl_dob, girl_time, girl_lat, girl_lon, girl_tz=5.5,
):
    """
    Generates a direct AstroSage Kundali Matching URL.

    AstroSage GET params (Kundli Milan form):
    https://www.astrosage.com/free/kundli-matching.asp

    Parameters are inferred from their form fields.
    """
    # Parse dates
    boy_d, boy_m, boy_y   = boy_dob.day, boy_dob.month, boy_dob.year
    girl_d, girl_m, girl_y = girl_dob.day, girl_dob.month, girl_dob.year
    boy_h, boy_min, boy_s  = boy_time.hour, boy_time.minute, boy_time.second
    girl_h, girl_min, girl_s = girl_time.hour, girl_time.minute, girl_time.second

    params = {
        # Boy
        "bname":  boy_name,
        "bday":   boy_d,  "bmon": boy_m,  "byear": boy_y,
        "bhrs":   boy_h,  "bmin": boy_min, "bsec": boy_s,
        "blat":   f"{boy_lat:.2f}",
        "blon":   f"{boy_lon:.2f}",
        "btzone": boy_tz,
        # Girl
        "gname":  girl_name,
        "gday":   girl_d,  "gmon": girl_m,  "gyear": girl_y,
        "ghrs":   girl_h,  "gmin": girl_min, "gsec": girl_s,
        "glat":   f"{girl_lat:.2f}",
        "glon":   f"{girl_lon:.2f}",
        "gtzone": girl_tz,
    }
    base = "https://www.astrosage.com/free/kundli-matching.asp"
    return base + "?" + urllib.parse.urlencode(params)


def print_engine_result(
    boy_rashi_name: str, boy_nak_name: str,
    girl_rashi_name: str, girl_nak_name: str,
):
    """Print our engine's koota breakdown for given rashi+nakshatra pairs."""
    from engine.models import Nakshatra, Rashi
    from engine.matching import (
        _compute_varna, _compute_vashya, _compute_tara, _compute_yoni,
        _compute_graha_maitri, _compute_gana, _compute_bhakoot, _compute_nadi,
    )

    boy_rashi  = next(r for r in Rashi     if r.name == boy_rashi_name)
    boy_nak    = next(n for n in Nakshatra  if n.name == boy_nak_name)
    girl_rashi = next(r for r in Rashi     if r.name == girl_rashi_name)
    girl_nak   = next(n for n in Nakshatra  if n.name == girl_nak_name)

    # Convention: bride=girl, groom=boy
    bride_rashi, groom_rashi = girl_rashi, boy_rashi
    bride_nak, groom_nak     = girl_nak, boy_nak

    varna   = _compute_varna(bride_rashi, groom_rashi)
    vasya   = _compute_vashya(bride_rashi, groom_rashi)
    tara    = _compute_tara(bride_nak, groom_nak)
    yoni    = _compute_yoni(bride_nak, groom_nak)
    maitri  = _compute_graha_maitri(bride_rashi, groom_rashi)
    gana    = _compute_gana(bride_nak, groom_nak, graha_maitri_score=maitri.points_earned)
    bhakoot, _ = _compute_bhakoot(bride_rashi, groom_rashi, graha_maitri_score=maitri.points_earned)
    nadi, _    = _compute_nadi(bride_nak, groom_nak, bride_rashi, groom_rashi)

    total = (varna.points_earned + vasya.points_earned + tara.points_earned +
             yoni.points_earned + maitri.points_earned + gana.points_earned +
             bhakoot.points_earned + nadi.points_earned)

    rows = [
        ("Varna",        varna.points_earned,   1),
        ("Vasya",        vasya.points_earned,   2),
        ("Tara",         tara.points_earned,    3),
        ("Yoni",         yoni.points_earned,    4),
        ("Graha Maitri", maitri.points_earned,  5),
        ("Gana",         gana.points_earned,    6),
        ("Bhakoot",      bhakoot.points_earned, 7),
        ("Nadi",         nadi.points_earned,    8),
    ]

    print(f"\n{'Koota':<14} {'Earned':>6} {'Max':>4}")
    print("-" * 28)
    for name, earned, max_ in rows:
        flag = "  <-- DOSHA" if earned == 0 and max_ > 1 else ""
        print(f"{name:<14} {earned:>6.1f} /{max_}{flag}")
    print("-" * 28)
    print(f"{'TOTAL':<14} {total:>6.1f} /36")


# ──────────────────────────────────────────────────────────────────────────────
# Demo with our 3 verified cases
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import datetime

    test_cases = [
        {
            "label": "Case 1: Suraj/Sonali (expected 28/36)",
            "boy_name": "Suraj",  "boy_dob": datetime.date(1996,5,5),  "boy_time": datetime.time(15,5),
            "boy_lat": 17.68, "boy_lon": 73.97,
            "girl_name": "Sonali", "girl_dob": datetime.date(1994,2,5), "girl_time": datetime.time(15,5),
            "girl_lat": 17.68, "girl_lon": 73.97,
            "boy_rashi": "SCORPIO", "boy_nak": "JYESHTHA",
            "girl_rashi": "SCORPIO", "girl_nak": "JYESHTHA",
        },
        {
            "label": "Case 2: Aishwarya/Rushikesh (expected 26/36)",
            "boy_name": "Rushikesh", "boy_dob": datetime.date(1996,10,7), "boy_time": datetime.time(21,33),
            "boy_lat": 17.63, "boy_lon": 74.07,
            "girl_name": "Aishwarya", "girl_dob": datetime.date(2000,12,24), "girl_time": datetime.time(0,55),
            "girl_lat": 17.68, "girl_lon": 73.97,
            "boy_rashi": "CANCER", "boy_nak": "ASHLESHA",
            "girl_rashi": "SCORPIO", "girl_nak": "JYESHTHA",
        },
        {
            "label": "Case 3: Sujata/Suraj (expected 18.5/36)",
            "boy_name": "Suraj", "boy_dob": datetime.date(1889,5,5), "boy_time": datetime.time(13,55),
            "boy_lat": 17.68, "boy_lon": 73.97,
            "girl_name": "Sujata", "girl_dob": datetime.date(1997,1,18), "girl_time": datetime.time(21,0),
            "girl_lat": 20.9, "girl_lon": 74.77,
            "boy_rashi": "GEMINI", "boy_nak": "PUNARVASU",
            "girl_rashi": "TAURUS", "girl_nak": "KRITTIKA",
        },
    ]

    for case in test_cases:
        print(f"\n{'='*60}")
        print(f"  {case['label']}")
        print(f"{'='*60}")

        url = generate_astrosage_url(
            boy_name=case["boy_name"], boy_dob=case["boy_dob"], boy_time=case["boy_time"],
            boy_lat=case["boy_lat"], boy_lon=case["boy_lon"],
            girl_name=case["girl_name"], girl_dob=case["girl_dob"], girl_time=case["girl_time"],
            girl_lat=case["girl_lat"], girl_lon=case["girl_lon"],
        )
        print(f"\n  AstroSage URL:\n  {url}\n")

        print_engine_result(case["boy_rashi"], case["boy_nak"], case["girl_rashi"], case["girl_nak"])
