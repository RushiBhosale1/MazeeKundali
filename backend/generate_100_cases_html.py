"""
generate_100_cases_html.py
--------------------------
Generates a clean, interactive verification dashboard for 100 test profile pairs.
Includes:
- Full 8-Koota breakdown & total Guna score (out of 36)
- Computed Rashi, Nakshatra, and birth details for Boy & Girl
- Direct working links to popular, easy-to-use astrology matching tools (Prokerala, DrikPanchang, AstroTalk)
- 1-Click Copy button to instantly copy birth inputs for fast manual verification on any portal
"""
import os
import sys
import json
from datetime import date, time as dtime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.models import TimeAccuracy
from engine.chart import compute_kundali
from engine.matching import compute_match
from verify_100_cases import generate_100_pairs

def main():
    print("Generating 100 profile pairs and computing local engine scores...")
    pairs = generate_100_pairs()
    cases_data = []

    for idx, pair in enumerate(pairs, 1):
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

        match_res = compute_match(g_kundali, b_kundali)

        boy_rashi = b_kundali.rashi.name if b_kundali.rashi else "N/A"
        boy_nak = b_kundali.nakshatra.name if b_kundali.nakshatra else "N/A"
        girl_rashi = g_kundali.rashi.name if g_kundali.rashi else "N/A"
        girl_nak = g_kundali.nakshatra.name if g_kundali.nakshatra else "N/A"

        copy_text = f"Boy: {b['name']} ({b['dob']} {b['time']} {b['place']} - Rashi: {boy_rashi}, Nakshatra: {boy_nak}) | Girl: {g['name']} ({g['dob']} {g['time']} {g['place']} - Rashi: {girl_rashi}, Nakshatra: {girl_nak})"

        cases_data.append({
            "id": pair["id"],
            "boy_name": b["name"],
            "boy_dob": b["dob"],
            "boy_time": b["time"],
            "boy_place": b["place"],
            "boy_rashi": boy_rashi,
            "boy_nakshatra": boy_nak,
            "girl_name": g["name"],
            "girl_dob": g["dob"],
            "girl_time": g["time"],
            "girl_place": g["place"],
            "girl_rashi": girl_rashi,
            "girl_nakshatra": girl_nak,
            "total_score": match_res.total_score,
            "kootas": {
                "Varna": match_res.varna.points_earned,
                "Vasya": match_res.vashya.points_earned,
                "Tara": match_res.tara.points_earned,
                "Yoni": match_res.yoni.points_earned,
                "Graha Maitri": match_res.graha_maitri.points_earned,
                "Gana": match_res.gana.points_earned,
                "Bhakoot": match_res.bhakoot.points_earned,
                "Nadi": match_res.nadi.points_earned,
            },
            "copy_text": copy_text
        })

    # Save to JSON
    json_path = os.path.join(os.path.dirname(__file__), "100_cases_dataset.json")
    with open(json_path, "w") as f:
        json.dump(cases_data, f, indent=2)

    # Generate HTML Dashboard
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>100 Test Cases Verification Dashboard — MazeeKundali</title>
    <style>
        :root {
            --primary: #4f46e5;
            --success: #16a34a;
            --warning: #ea580c;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --border: #e2e8f0;
            --text: #0f172a;
            --muted: #64748b;
        }
        body { font-family: system-ui, -apple-system, sans-serif; background: var(--bg); margin: 0; padding: 24px; color: var(--text); }
        .header { text-align: center; margin-bottom: 32px; }
        .header h1 { margin: 0 0 8px 0; color: #1e1b4b; font-size: 28px; }
        .header p { margin: 0; color: var(--muted); font-size: 15px; }
        .portal-links { display: flex; justify-content: center; gap: 12px; margin-top: 16px; flex-wrap: wrap; }
        .portal-btn { text-decoration: none; padding: 8px 16px; border-radius: 6px; background: white; border: 1px solid var(--border); color: var(--primary); font-weight: 600; font-size: 13px; transition: all 0.2s; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
        .portal-btn:hover { background: #eeefef; border-color: var(--primary); }
        
        .search-bar { max-width: 500px; margin: 0 auto 24px auto; display: flex; gap: 8px; }
        .search-bar input { flex: 1; padding: 10px 16px; border-radius: 8px; border: 1px solid var(--border); font-size: 14px; outline: none; }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(440px, 1fr)); gap: 20px; }
        .card { background: var(--card-bg); border-radius: 12px; padding: 20px; border: 1px solid var(--border); box-shadow: 0 2px 4px rgba(0,0,0,0.02); display: flex; flex-direction: column; justify-content: space-between; }
        .card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; padding-bottom: 12px; border-bottom: 1px solid var(--border); }
        .case-badge { font-weight: 700; color: var(--primary); font-size: 15px; background: #eef2ff; padding: 4px 10px; border-radius: 6px; }
        .score-badge { font-size: 20px; font-weight: 800; color: var(--success); background: #f0fdf4; padding: 4px 14px; border-radius: 20px; border: 1px solid #bbf7d0; }
        
        .profile-row { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 8px; background: #f8fafc; padding: 8px 12px; border-radius: 6px; }
        .profile-title { font-weight: 700; color: #334155; }
        .profile-sub { color: var(--muted); }
        
        .koota-table { width: 100%; border-collapse: collapse; font-size: 12px; margin: 12px 0; }
        .koota-table th, .koota-table td { border: 1px solid var(--border); padding: 6px 8px; text-align: center; }
        .koota-table th { background: #f1f5f9; font-weight: 600; color: #475569; }
        .koota-zero { color: #dc2626; font-weight: 700; background: #fef2f2; }
        
        .actions { display: flex; gap: 8px; margin-top: 8px; }
        .btn-action { flex: 1; padding: 8px; text-align: center; border-radius: 6px; border: 1px solid var(--border); background: white; font-size: 12px; font-weight: 600; color: #334155; cursor: pointer; text-decoration: none; transition: background 0.15s; }
        .btn-action:hover { background: #f1f5f9; }
        .btn-copy { background: #f8fafc; color: var(--primary); border-color: #c7d2fe; }
        .btn-copy:hover { background: #eef2ff; }
    </style>
</head>
<body>
    <div class="header">
        <h1>100 Test Cases Matching Dashboard</h1>
        <p>MazeeKundali Engine Results & Cross-Platform Verification Suite</p>
        <div class="portal-links">
            <a href="https://www.prokerala.com/astrology/kundali-matching/" target="_blank" class="portal-btn">🌐 Prokerala Kundali Matching ↗</a>
            <a href="https://www.drikpanchang.com/horoscope-matching/kundali-matching.html" target="_blank" class="portal-btn">🌐 DrikPanchang Matching ↗</a>
            <a href="https://astrotalk.com/free-kundli-matching" target="_blank" class="portal-btn">🌐 AstroTalk Guna Milan ↗</a>
        </div>
    </div>

    <div class="search-bar">
        <input type="text" id="searchInput" placeholder="Search by Case ID, City, Rashi, or Nakshatra..." onkeyup="filterCases()">
    </div>

    <div class="grid" id="casesGrid">
"""

    for c in cases_data:
        k = c["kootas"]
        
        def cell(val):
            return f'<td class="koota-zero">{val}</td>' if val == 0 else f'<td>{val}</td>'

        html_content += f"""
        <div class="card" data-search="{c['id']} {c['boy_place']} {c['girl_place']} {c['boy_rashi']} {c['boy_nakshatra']} {c['girl_rashi']} {c['girl_nakshatra']}">
            <div>
                <div class="card-top">
                    <span class="case-badge">{c['id']}</span>
                    <span class="score-badge">{c['total_score']} / 36</span>
                </div>

                <div class="profile-row">
                    <div>
                        <span class="profile-title">👦 Boy ({c['boy_name']})</span><br>
                        <span class="profile-sub">{c['boy_dob']} {c['boy_time']} ({c['boy_place']})</span>
                    </div>
                    <div style="text-align: right;">
                        <span class="profile-title">{c['boy_rashi']}</span><br>
                        <span class="profile-sub">{c['boy_nakshatra']}</span>
                    </div>
                </div>

                <div class="profile-row">
                    <div>
                        <span class="profile-title">👧 Girl ({c['girl_name']})</span><br>
                        <span class="profile-sub">{c['girl_dob']} {c['girl_time']} ({c['girl_place']})</span>
                    </div>
                    <div style="text-align: right;">
                        <span class="profile-title">{c['girl_rashi']}</span><br>
                        <span class="profile-sub">{c['girl_nakshatra']}</span>
                    </div>
                </div>

                <table class="koota-table">
                    <tr><th>Varna</th><th>Vasya</th><th>Tara</th><th>Yoni</th><th>Maitri</th><th>Gana</th><th>Bhakoot</th><th>Nadi</th></tr>
                    <tr>
                        {cell(k['Varna'])}{cell(k['Vasya'])}{cell(k['Tara'])}{cell(k['Yoni'])}
                        {cell(k['Graha Maitri'])}{cell(k['Gana'])}{cell(k['Bhakoot'])}{cell(k['Nadi'])}
                    </tr>
                </table>
            </div>

            <div class="actions">
                <button class="btn-action btn-copy" onclick="copyDetails('{c['copy_text']}', this)">📋 Copy Case Info</button>
                <a href="https://www.prokerala.com/astrology/kundali-matching/" target="_blank" class="btn-action">Check Prokerala ↗</a>
                <a href="https://www.drikpanchang.com/horoscope-matching/kundali-matching.html" target="_blank" class="btn-action">DrikPanchang ↗</a>
            </div>
        </div>
"""

    html_content += """
    </div>

    <script>
        function copyDetails(text, btn) {
            navigator.clipboard.writeText(text);
            const orig = btn.innerText;
            btn.innerText = "✓ Copied!";
            setTimeout(() => { btn.innerText = orig; }, 1500);
        }

        function filterCases() {
            const query = document.getElementById('searchInput').value.toLowerCase();
            const cards = document.querySelectorAll('.card');
            cards.forEach(card => {
                const searchData = card.getAttribute('data-search').toLowerCase();
                card.style.display = searchData.includes(query) ? 'flex' : 'none';
            });
        }
    </script>
</body>
</html>
"""

    html_path = os.path.join(os.path.dirname(__file__), "100_cases_dashboard.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Generated 100 cases dataset: {json_path}")
    print(f"Generated interactive dashboard: {html_path}")

if __name__ == "__main__":
    main()
