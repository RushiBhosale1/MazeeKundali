"""
verify_100_cases.py
-------------------
Automated verification pipeline:
1. Generates 100 diverse birth pairs across various dates, times, and cities.
2. Queries AstroSage for each pair to extract exact total points & koota scores.
3. Computes scores using our MazeeKundali engine.
4. Generates a summary comparison report and logs discrepancies.
"""
import os
import sys
import json
import time
import urllib.request
import urllib.parse
import re
from datetime import datetime, date, time as dtime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.models import TimeAccuracy, RahuMode
from engine.chart import compute_kundali
from engine.matching import compute_match

# Sample Cities with Coordinates (Lat, Lon, Timezone)
CITIES = [
    ("Satara", 17.68, 73.97, 5.5),
    ("Pune", 18.52, 73.85, 5.5),
    ("Mumbai", 19.07, 72.87, 5.5),
    ("Nagpur", 21.14, 79.08, 5.5),
    ("Nashik", 20.00, 73.78, 5.5),
    ("Dhule", 20.90, 74.77, 5.5),
    ("Kolhapur", 16.70, 74.24, 5.5),
    ("Delhi", 28.61, 77.20, 5.5),
    ("Bangalore", 12.97, 77.59, 5.5),
    ("Ahmedabad", 23.02, 72.57, 5.5),
]

def generate_100_pairs():
    pairs = []
    # Seeded generation for 100 distinct profile pairs
    for i in range(1, 101):
        # Boy DOB variation
        b_year = 1985 + (i * 3) % 25
        b_month = (i % 12) + 1
        b_day = (i * 7 % 27) + 1
        b_hour = (i * 5) % 24
        b_min = (i * 13) % 60
        b_city = CITIES[i % len(CITIES)]

        # Girl DOB variation
        g_year = 1988 + (i * 2) % 25
        g_month = ((i + 5) % 12) + 1
        g_day = (i * 11 % 27) + 1
        g_hour = (i * 7) % 24
        g_min = (i * 17) % 60
        g_city = CITIES[(i + 3) % len(CITIES)]

        pair = {
            "id": f"CASE_{i:03d}",
            "boy": {
                "name": f"Boy_{i}",
                "dob": f"{b_year}-{b_month:02d}-{b_day:02d}",
                "time": f"{b_hour:02d}:{b_min:02d}:00",
                "place": b_city[0],
                "lat": b_city[1],
                "lon": b_city[2],
                "tz": b_city[3],
            },
            "girl": {
                "name": f"Girl_{i}",
                "dob": f"{g_year}-{g_month:02d}-{g_day:02d}",
                "time": f"{g_hour:02d}:{g_min:02d}:00",
                "place": g_city[0],
                "lat": g_city[1],
                "lon": g_city[2],
                "tz": g_city[3],
            }
        }
        pairs.append(pair)
    return pairs

def fetch_astrosage_result(pair):
    """Fetch matching result from AstroSage using HTTP POST request."""
    boy = pair["boy"]
    girl = pair["girl"]

    b_y, b_m, b_d = map(int, boy["dob"].split("-"))
    b_h, b_min, _ = map(int, boy["time"].split(":"))

    g_y, g_m, g_d = map(int, girl["dob"].split("-"))
    g_h, g_min, _ = map(int, girl["time"].split(":"))

    form_data = {
        "bname": boy["name"],
        "bday": str(b_d), "bmon": str(b_m), "byear": str(b_y),
        "bhrs": str(b_h), "bmin": str(b_min), "bsec": "0",
        "blat": f"{boy['lat']:.2f}", "blon": f"{boy['lon']:.2f}", "btzone": str(boy["tz"]),
        "gname": girl["name"],
        "gday": str(g_d), "gmon": str(g_m), "gyear": str(g_y),
        "ghrs": str(g_h), "gmin": str(g_min), "gsec": "0",
        "glat": f"{girl['lat']:.2f}", "glon": f"{girl['lon']:.2f}", "gtzone": str(girl["tz"]),
    }

    url = "https://www.astrosage.com/free/kundli-matching.asp"
    data = urllib.parse.urlencode(form_data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-encoding"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            html = response.read().decode("utf-8", errors="ignore")

            # Extract total score
            total_match = re.search(r"Ashtakoot Matching between boy and girl is\s*<b>?\s*([\d\.]+)/36", html, re.IGNORECASE)
            if not total_match:
                total_match = re.search(r"Obtained Point.*?([\d\.]+)/36", html, re.DOTALL | re.IGNORECASE)

            if total_match:
                total_score = float(total_match.group(1))
                return {"success": True, "total": total_score, "raw_html": html}
            else:
                return {"success": False, "error": "Total score pattern not found"}

    except Exception as e:
        return {"success": False, "error": str(e)}

def run_local_engine(pair):
    """Calculate match using local MazeeKundali engine."""
    b = pair["boy"]
    g = pair["girl"]

    b_y, b_m, b_d = map(int, b["dob"].split("-"))
    b_h, b_min, _ = map(int, b["time"].split(":"))

    g_y, g_m, g_d = map(int, g["dob"].split("-"))
    g_h, g_min, _ = map(int, g["time"].split(":"))

    b_kundali = compute_kundali(
        name=b["name"],
        gender="male",
        birth_date=date(b_y, b_m, b_d),
        birth_time=dtime(b_h, b_min),
        time_accuracy=TimeAccuracy.EXACT,
        place_text=b["place"],
        latitude=b["lat"],
        longitude=b["lon"],
        tz_iana="Asia/Kolkata",
    )
    g_kundali = compute_kundali(
        name=g["name"],
        gender="female",
        birth_date=date(g_y, g_m, g_d),
        birth_time=dtime(g_h, g_min),
        time_accuracy=TimeAccuracy.EXACT,
        place_text=g["place"],
        latitude=g["lat"],
        longitude=g["lon"],
        tz_iana="Asia/Kolkata",
    )

    # Note: Matching engine takes Bride=Girl, Groom=Boy
    match_res = compute_match(g_kundali, b_kundali)
    return match_res.total_score, b_kundali, g_kundali

def main():
    print("Generating 100 profile pairs...")
    pairs = generate_100_pairs()

    print("Starting automated verification against AstroSage...")
    results = []
    matched_count = 0
    failed_fetch_count = 0

    for idx, pair in enumerate(pairs, 1):
        print(f"[{idx}/100] Testing {pair['id']}: {pair['boy']['name']} & {pair['girl']['name']}...", end="", flush=True)

        try:
            local_score, b_k, g_k = run_local_engine(pair)
        except Exception as e:
            print(f" [ENGINE ERROR: {e}]")
            continue

        # Fetch AstroSage result
        astrosage_res = fetch_astrosage_result(pair)

        if astrosage_res["success"]:
            as_score = astrosage_res["total"]
            is_match = (abs(local_score - as_score) < 0.1)
            if is_match:
                matched_count += 1
                status = "MATCH ✅"
            else:
                status = f"MISMATCH ❌ (Local: {local_score}, AstroSage: {as_score})"

            print(f" -> Local: {local_score}, AstroSage: {as_score} | {status}")

            results.append({
                "id": pair["id"],
                "boy": pair["boy"],
                "girl": pair["girl"],
                "boy_rashi": b_k.moon_sign.rashi.name,
                "boy_nakshatra": b_k.moon_sign.nakshatra.name,
                "girl_rashi": g_k.moon_sign.rashi.name,
                "girl_nakshatra": g_k.moon_sign.nakshatra.name,
                "local_score": local_score,
                "astrosage_score": as_score,
                "match": is_match
            })
        else:
            failed_fetch_count += 1
            print(f" -> AstroSage Fetch Failed ({astrosage_res['error']}) | Local Score: {local_score}")

        # Polite delay between requests
        time.sleep(1)

    print("\n" + "="*60)
    print(f"VERIFICATION COMPLETE")
    print(f"Total Evaluated: {len(results)}")
    print(f"Exact Matches:   {matched_count} / {len(results)}")
    if len(results) > 0:
        print(f"Accuracy Rate:   {(matched_count / len(results)) * 100:.2f}%")
    print("="*60)

    # Save detailed JSON summary report
    report_path = os.path.join(os.path.dirname(__file__), "100_cases_verification_report.json")
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Report saved to: {report_path}")

if __name__ == "__main__":
    main()
