"""
Smoke test — runs against live server at localhost:8000
Usage: venv\Scripts\python tests\smoke_test.py
"""
import urllib.request, json, sys

BASE = "http://localhost:8000"

def post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=body,
          headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def get(path):
    with urllib.request.urlopen(f"{BASE}{path}", timeout=15) as r:
        return json.loads(r.read())

def run():
    ok_count = fail_count = 0
    def ok(msg):
        nonlocal ok_count; ok_count += 1; print(f"  [PASS] {msg}")
    def fail(msg, err):
        nonlocal fail_count; fail_count += 1; print(f"  [FAIL] {msg}: {err}")

    print("\n=== Smoke Test: Mazi Kundali API ===\n")

    # 1. Health
    try:
        r = get("/health"); assert r["status"] == "ok"; ok("GET /health")
    except Exception as e: fail("GET /health", e)

    # 2. Geocode
    try:
        r = get("/api/v1/geocode?query=Pune,Maharashtra")
        assert len(r["places"]) > 0; ok(f"GET /geocode -> {len(r['places'])} places")
    except Exception as e: fail("GET /geocode", e)

    # 3. Create kundali
    kundali_id = None
    try:
        r = post("/api/v1/kundalis", {
            "name": "Test Rushi", "gender": "male", "dob": "1990-05-15",
            "time_of_birth": "14:30", "time_accuracy": "exact",
            "place_query": "Pune, Maharashtra",
            "latitude": 18.5204, "longitude": 73.8567,
            "tz_iana": "Asia/Kolkata", "rahu_mode": "true_node"
        })
        kundali_id = str(r["id"])
        rashi = r.get("rashi", {}).get("name_en", "?")
        nakshatra = r.get("nakshatra", {}).get("name_en", "?")
        ok(f"POST /kundalis -> rashi={rashi} nakshatra={nakshatra}")
        ok(f"  SVG chart={'YES' if r.get('chart_d1_svg') else 'MISSING'}")
        ok(f"  resume_token={'YES' if r.get('resume_token') else 'MISSING'}")
        ok(f"  locked.planet_positions={r.get('locked',{}).get('planet_positions')}")
    except Exception as e: fail("POST /kundalis", e)

    # 4. Fetch back
    if kundali_id:
        try:
            r = get(f"/api/v1/kundalis/{kundali_id}")
            assert r["paid"] == False; ok(f"GET /kundalis/{kundali_id[:8]}... OK")
        except Exception as e: fail("GET /kundalis/:id", e)

    # 5. Matching
    try:
        r = post("/api/v1/matchings", {
            "bride": {"name": "Priya", "gender": "female", "dob": "1992-03-20",
                      "time_of_birth": "08:00", "time_accuracy": "exact",
                      "place_query": "Nashik", "latitude": 19.9975,
                      "longitude": 73.7898, "tz_iana": "Asia/Kolkata", "rahu_mode": "true_node"},
            "groom": {"name": "Rahul", "gender": "male", "dob": "1990-05-15",
                      "time_of_birth": "14:30", "time_accuracy": "exact",
                      "place_query": "Pune", "latitude": 18.5204,
                      "longitude": 73.8567, "tz_iana": "Asia/Kolkata", "rahu_mode": "true_node"}
        })
        ok(f"POST /matchings -> score={r.get('total_score')}/36")
    except Exception as e: fail("POST /matchings", e)

    # 6. Engine (paid fields) — mounted at /api/v1/engine/kundali
    try:
        r = post("/api/v1/engine/kundali", {
            "name": "Engine Test", "gender": "male", "dob": "1985-11-01",
            "time_of_birth": "06:45", "time_accuracy": "exact",
            "place_query": "Mumbai", "latitude": 19.0760, "longitude": 72.8777,
            "tz_iana": "Asia/Kolkata", "rahu_mode": "true_node", "compute_paid_fields": True
        })
        planets = r.get("planet_positions", [])
        ok(f"POST /engine/kundali -> {len(planets)} planets")
    except Exception as e: fail("POST /engine/kundali", e)

    print(f"\n{'='*38}")
    print(f"  {ok_count} PASSED  {fail_count} FAILED")
    print("="*38)
    return 1 if fail_count else 0

if __name__ == "__main__":
    sys.exit(run())
