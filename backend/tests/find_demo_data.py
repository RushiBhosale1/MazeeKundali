import os
import sys
from datetime import datetime, timedelta, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.geocoding import resolve_utc_birth_moment
from engine.ephemeris import compute_planetary_positions, longitude_to_rashi, longitude_to_nakshatra, longitude_to_pada

def check_date(dt_str, time_str, lat, lon):
    dt = datetime.strptime(f"{dt_str} {time_str}", "%Y-%m-%d %H:%M")
    utc_dt = resolve_utc_birth_moment(dt, time(dt.hour, dt.minute), "Asia/Kolkata")
    raw = compute_planetary_positions(utc_dt, lat, lon, "TRUE_NODE", "./static/ephemeris")
    moon_lon = raw["planets"]["Moon"]["longitude"]
    rashi = longitude_to_rashi(moon_lon)
    nak = longitude_to_nakshatra(moon_lon)
    pada = longitude_to_pada(moon_lon)
    return rashi, nak, pada

if __name__ == "__main__":
    lat, lon = 18.5204, 73.8567 # Pune
    
    start_dt = datetime(1995, 7, 15, 0, 0)
    for i in range(24):
        dt = start_dt + timedelta(hours=i*2)
        r, n, p = check_date(dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M"), lat, lon)
        print(f"{dt.strftime('%Y-%m-%d %H:%M')} -> Nakshatra: {n}, Pada: {p}")
